/*
 * Agent Initialization Validator Testbench
 *
 * This testbench extracts agent initialization state from the RTL
 * for comparison with Python reference implementation.
 *
 * Outputs: rtl_agent_validation.json
 */

#include "Vslime_top.h"
#include "verilated.h"
#include <iostream>
#include <fstream>
#include <vector>
#include <cstdint>
#include <cstring>
#include <cmath>
#include <iomanip>
#include <sstream>

// Simulation parameters (must match Python validation)
const int NUM_AGENTS = 1000;
const int WIDTH = 320;
const int HEIGHT = 240;

// Fixed-point constants
const int FP_FRAC_BITS = 12;
const int FP_SCALE = 1 << FP_FRAC_BITS;
const int FP_TOTAL_BITS = 25;

// Agent structure
struct AgentState {
    int32_t x_fp;
    int32_t y_fp;
    int32_t angle_fp;

    double x_px() const { return (double)x_fp / FP_SCALE; }
    double y_px() const { return (double)y_fp / FP_SCALE; }
    double angle_rad() const { return (double)angle_fp / FP_SCALE; }
    double angle_deg() const { return angle_rad() * 180.0 / M_PI; }
};

class AgentInitValidator {
public:
    Vslime_top* dut;
    std::vector<AgentState> agents;
    uint64_t cycle_count;

    AgentInitValidator() : cycle_count(0) {
        dut = new Vslime_top;
        agents.resize(NUM_AGENTS);
    }

    ~AgentInitValidator() {
        delete dut;
    }

    void clock(int num_clocks = 1) {
        for (int i = 0; i < num_clocks; i++) {
            dut->clk_100mhz = 0;
            dut->eval();

            dut->clk_100mhz = 1;
            dut->eval();

            cycle_count++;
        }
    }

    void reset() {
        std::cout << "\n[RTL Validator] Resetting RTL..." << std::endl;
        dut->btnc = 0;
        dut->btnu = 0;
        dut->btnd = 0;
        dut->btnl = 0;
        dut->btnr = 0;
        dut->sw = 0;

        for (int i = 0; i < 20; i++) {
            clock();
        }
        std::cout << "[RTL Validator] Reset complete\n" << std::endl;
    }

    bool read_agent_memory() {
        /*
         * Read agent state from RTL through debug interface.
         *
         * Uses the debug_agent_* signals added to slime_top:
         *   - debug_agent_idx: selects which agent (0-999)
         *   - debug_agent_sel: selects x/y/angle (0/1/2)
         *   - debug_agent_data: returns the selected value
         */

        std::cout << "[RTL Validator] Reading agent memory from RTL..." << std::endl;

        // Initialize all debug inputs to zero
        dut->debug_trail_addr = 0;
        dut->sim_start = 0;

        for (int i = 0; i < NUM_AGENTS; i++) {
            // Read agent x
            dut->debug_agent_idx = i;
            dut->debug_agent_sel = 0;  // 0 = x
            dut->eval();
            // Sign-extend from 25-bit to 32-bit
            uint32_t x_raw = dut->debug_agent_data;
            agents[i].x_fp = (x_raw & 0x1000000) ? (int32_t)(x_raw | 0xFE000000) : (int32_t)x_raw;

            // Read agent y
            dut->debug_agent_sel = 1;  // 1 = y
            dut->eval();
            uint32_t y_raw = dut->debug_agent_data;
            agents[i].y_fp = (y_raw & 0x1000000) ? (int32_t)(y_raw | 0xFE000000) : (int32_t)y_raw;

            // Read agent angle
            dut->debug_agent_sel = 2;  // 2 = angle
            dut->eval();
            uint32_t angle_raw = dut->debug_agent_data;
            agents[i].angle_fp = (angle_raw & 0x1000000) ? (int32_t)(angle_raw | 0xFE000000) : (int32_t)angle_raw;

            // Progress indicator
            if ((i + 1) % 100 == 0) {
                std::cout << "[RTL Validator]   Read " << (i + 1) << "/" << NUM_AGENTS << " agents..." << std::endl;
            }
        }

        std::cout << "[RTL Validator] ✓ Agent memory read complete" << std::endl;
        return true;
    }

    void extract_agent_state(const std::string& output_file, int num_validate = -1) {
        std::cout << "[RTL Validator] Extracting agent initialization state..." << std::endl;

        if (num_validate < 0 || num_validate > NUM_AGENTS) {
            num_validate = NUM_AGENTS;
        }

        // Read agent state from RTL
        if (!read_agent_memory()) {
            std::cerr << "[RTL Validator] Failed to read agent memory!" << std::endl;
            return;
        }

        // Calculate center coordinates
        double cx_px = WIDTH / 2.0;
        double cy_px = HEIGHT / 2.0;
        int32_t cx_fp = (int32_t)(cx_px * FP_SCALE);
        int32_t cy_fp = (int32_t)(cy_px * FP_SCALE);

        // Expected radius for circle spawn (40% of min dimension)
        int min_dim = (WIDTH < HEIGHT) ? WIDTH : HEIGHT;
        double radius_px = min_dim * 0.4;
        int32_t radius_fp = (int32_t)(radius_px * FP_SCALE);

        // Build JSON output
        std::ofstream json_file(output_file);
        if (!json_file.is_open()) {
            std::cerr << "[RTL Validator] Failed to open output file: " << output_file << std::endl;
            return;
        }

        json_file << "{\n";
        json_file << "  \"summary\": {\n";
        json_file << "    \"num_agents\": " << num_validate << ",\n";
        json_file << "    \"total_agents\": " << NUM_AGENTS << ",\n";
        json_file << "    \"resolution\": {\"width\": " << WIDTH << ", \"height\": " << HEIGHT << "},\n";
        json_file << "    \"spawn_pattern\": \"circle\",\n";
        json_file << "    \"fixed_point\": {\n";
        json_file << "      \"integer_bits\": 12,\n";
        json_file << "      \"fractional_bits\": " << FP_FRAC_BITS << ",\n";
        json_file << "      \"scale\": " << FP_SCALE << "\n";
        json_file << "    }\n";
        json_file << "  },\n";
        json_file << "  \"agents\": [\n";

        // Statistics accumulators
        double min_dist = 1e9, max_dist = -1e9, sum_dist = 0;
        double min_angle = 1e9, max_angle = -1e9, sum_angle = 0;

        for (int i = 0; i < num_validate; i++) {
            const AgentState& agent = agents[i];

            // Position in pixels
            double x_px = agent.x_px();
            double y_px = agent.y_px();
            double angle_rad = agent.angle_rad();
            double angle_deg = agent.angle_deg();

            // Distance from center
            double dx_px = x_px - cx_px;
            double dy_px = y_px - cy_px;
            double dist = std::sqrt(dx_px*dx_px + dy_px*dy_px);

            // Angle from center
            double angle_from_center = std::atan2(dy_px, dx_px);
            if (angle_from_center < 0) {
                angle_from_center += 2 * M_PI;
            }

            // Expected spawn angle
            double expected_spawn_rad = (2.0 * M_PI * i) / NUM_AGENTS;
            int32_t expected_spawn_fp = (int32_t)(expected_spawn_rad * FP_SCALE);

            // Expected agent angle (spawn + π, wrapped to [0, 2π))
            int32_t pi_fp = (int32_t)(M_PI * FP_SCALE);
            int32_t two_pi_fp = (int32_t)(2 * M_PI * FP_SCALE);
            int32_t expected_angle_fp = expected_spawn_fp + pi_fp;
            if (expected_angle_fp >= two_pi_fp) {
                expected_angle_fp -= two_pi_fp;
            }
            double expected_angle_rad = (double)expected_angle_fp / FP_SCALE;

            // Determine quadrant
            int quadrant = 0;
            if (angle_from_center >= 0 && angle_from_center < M_PI/2) quadrant = 0;
            else if (angle_from_center >= M_PI/2 && angle_from_center < M_PI) quadrant = 1;
            else if (angle_from_center >= M_PI && angle_from_center < 3*M_PI/2) quadrant = 2;
            else quadrant = 3;

            // Update statistics
            min_dist = std::min(min_dist, dist);
            max_dist = std::max(max_dist, dist);
            sum_dist += dist;
            min_angle = std::min(min_angle, angle_rad);
            max_angle = std::max(max_angle, angle_rad);
            sum_angle += angle_rad;

            // Write agent JSON
            json_file << "    {\n";
            json_file << "      \"index\": " << i << ",\n";
            json_file << "      \"position\": {\n";
            json_file << "        \"x_fp\": " << agent.x_fp << ",\n";
            json_file << "        \"y_fp\": " << agent.y_fp << ",\n";
            json_file << "        \"x_px\": " << x_px << ",\n";
            json_file << "        \"y_px\": " << y_px << "\n";
            json_file << "      },\n";
            json_file << "      \"angle\": {\n";
            json_file << "        \"angle_fp\": " << agent.angle_fp << ",\n";
            json_file << "        \"angle_rad\": " << angle_rad << ",\n";
            json_file << "        \"angle_deg\": " << angle_deg << "\n";
            json_file << "      },\n";
            json_file << "      \"spawn\": {\n";
            json_file << "        \"spawn_angle_rad\": " << angle_from_center << ",\n";
            json_file << "        \"spawn_angle_deg\": " << (angle_from_center * 180.0 / M_PI) << ",\n";
            json_file << "        \"expected_spawn_rad\": " << expected_spawn_rad << ",\n";
            json_file << "        \"expected_spawn_fp\": " << expected_spawn_fp << "\n";
            json_file << "      },\n";
            json_file << "      \"agent_angle\": {\n";
            json_file << "        \"expected_angle_fp\": " << expected_angle_fp << ",\n";
            json_file << "        \"expected_angle_rad\": " << expected_angle_rad << ",\n";
            json_file << "        \"expected_angle_deg\": " << (expected_angle_rad * 180.0 / M_PI) << "\n";
            json_file << "      },\n";
            json_file << "      \"geometry\": {\n";
            json_file << "        \"distance_from_center\": " << dist << ",\n";
            json_file << "        \"angle_from_center_rad\": " << angle_from_center << ",\n";
            json_file << "        \"angle_from_center_deg\": " << (angle_from_center * 180.0 / M_PI) << ",\n";
            json_file << "        \"quadrant\": " << quadrant << "\n";
            json_file << "      },\n";
            json_file << "      \"expected\": {\n";
            json_file << "        \"radius_fp\": " << radius_fp << ",\n";
            json_file << "        \"radius_px\": " << radius_px << ",\n";
            json_file << "        \"center_x_fp\": " << cx_fp << ",\n";
            json_file << "        \"center_y_fp\": " << cy_fp << ",\n";
            json_file << "        \"center_x_px\": " << cx_px << ",\n";
            json_file << "        \"center_y_px\": " << cy_px << "\n";
            json_file << "      }\n";
            json_file << "    }";
            if (i < num_validate - 1) {
                json_file << ",";
            }
            json_file << "\n";
        }

        json_file << "  ],\n";

        // Write statistics
        double mean_dist = sum_dist / num_validate;
        double mean_angle = sum_angle / num_validate;

        json_file << "  \"statistics\": {\n";
        json_file << "    \"distance\": {\n";
        json_file << "      \"min\": " << min_dist << ",\n";
        json_file << "      \"max\": " << max_dist << ",\n";
        json_file << "      \"mean\": " << mean_dist << "\n";
        json_file << "    },\n";
        json_file << "    \"angle\": {\n";
        json_file << "      \"min_rad\": " << min_angle << ",\n";
        json_file << "      \"max_rad\": " << max_angle << ",\n";
        json_file << "      \"mean_rad\": " << mean_angle << ",\n";
        json_file << "      \"min_deg\": " << (min_angle * 180.0 / M_PI) << ",\n";
        json_file << "      \"max_deg\": " << (max_angle * 180.0 / M_PI) << ",\n";
        json_file << "      \"mean_deg\": " << (mean_angle * 180.0 / M_PI) << "\n";
        json_file << "    }\n";
        json_file << "  }\n";
        json_file << "}\n";

        json_file.close();

        std::cout << "[RTL Validator] ✓ Validation data saved to " << output_file << std::endl;
    }
};

int main(int argc, char** argv) {
    std::cout << "\n========================================" << std::endl;
    std::cout << "RTL Agent Initialization Validator" << std::endl;
    std::cout << "========================================\n" << std::endl;

    // Parse command line arguments
    std::string output_file = "rtl_agent_validation.json";
    int num_validate = NUM_AGENTS;

    for (int i = 1; i < argc; i++) {
        std::string arg(argv[i]);
        if (arg == "--output" && i + 1 < argc) {
            output_file = argv[++i];
        } else if (arg == "--num-validate" && i + 1 < argc) {
            num_validate = std::atoi(argv[++i]);
        } else if (arg == "--help") {
            std::cout << "Usage: " << argv[0] << " [options]\n";
            std::cout << "Options:\n";
            std::cout << "  --output FILE        Output JSON file (default: rtl_agent_validation.json)\n";
            std::cout << "  --num-validate N     Number of agents to validate (default: all)\n";
            std::cout << "  --help               Show this help message\n";
            return 0;
        }
    }

    // Create validator
    AgentInitValidator validator;

    // Reset RTL
    validator.reset();

    // Extract agent state
    validator.extract_agent_state(output_file, num_validate);

    std::cout << "\n[RTL Validator] Done!" << std::endl;

    return 0;
}
