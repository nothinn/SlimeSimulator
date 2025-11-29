/*
 * Example: Using Pre-computed Agent Initialization Data
 *
 * This minimal example demonstrates how to use the generated
 * agent_init_data.h file in a C++ testbench.
 *
 * Compile: g++ -o test_agent_init_example test_agent_init_example.cpp
 * Run:     ./test_agent_init_example
 */

#include <iostream>
#include <iomanip>
#include <cmath>

// Include the generated header
#include "agent_init_data.h"

// Fixed-point constants (must match Python reference)
const int FP_FRAC_BITS = 12;
const int FP_SCALE = 1 << FP_FRAC_BITS;  // 4096

// Convert fixed-point to float
double fp_to_float(int32_t fp_value) {
    return (double)fp_value / FP_SCALE;
}

// Calculate distance from center
double distance_from_center(double x, double y, double cx, double cy) {
    double dx = x - cx;
    double dy = y - cy;
    return sqrt(dx*dx + dy*dy);
}

int main() {
    std::cout << "================================================================================\n";
    std::cout << "Agent Initialization Data Test\n";
    std::cout << "================================================================================\n\n";

    std::cout << "Configuration:\n";
    std::cout << "  Number of agents: " << NUM_INIT_AGENTS << "\n";
    std::cout << "  Fixed-point format: Q12.12 (scale = " << FP_SCALE << ")\n";
    std::cout << "\n";

    // For 320×240 simulation
    const int WIDTH = 320;
    const int HEIGHT = 240;
    const double cx = WIDTH / 2.0;
    const double cy = HEIGHT / 2.0;
    const double expected_radius = std::min(WIDTH, HEIGHT) * 0.4;

    std::cout << "Expected circle spawn parameters:\n";
    std::cout << "  Center: (" << cx << ", " << cy << ") pixels\n";
    std::cout << "  Radius: " << expected_radius << " pixels\n";
    std::cout << "\n";

    // Display first 10 agents
    std::cout << "First 10 agents:\n";
    std::cout << "--------------------------------------------------------------------------------\n";
    std::cout << std::setw(6) << "Agent"
              << std::setw(12) << "X (px)"
              << std::setw(12) << "Y (px)"
              << std::setw(14) << "Angle (rad)"
              << std::setw(14) << "Angle (deg)"
              << std::setw(16) << "Distance"
              << std::setw(10) << "Status"
              << "\n";
    std::cout << "--------------------------------------------------------------------------------\n";

    int pass_count = 0;
    int fail_count = 0;

    for (int i = 0; i < std::min(10, NUM_INIT_AGENTS); i++) {
        // Extract fixed-point values
        int32_t x_fp = AGENT_INIT_DATA[i][0];
        int32_t y_fp = AGENT_INIT_DATA[i][1];
        int32_t angle_fp = AGENT_INIT_DATA[i][2];

        // Convert to float
        double x = fp_to_float(x_fp);
        double y = fp_to_float(y_fp);
        double angle_rad = fp_to_float(angle_fp);
        double angle_deg = angle_rad * 180.0 / M_PI;

        // Calculate distance from center
        double dist = distance_from_center(x, y, cx, cy);

        // Verify distance is approximately correct (within 1%)
        double error = fabs(dist - expected_radius) / expected_radius;
        bool pass = error < 0.01;

        if (pass) pass_count++;
        else fail_count++;

        std::cout << std::fixed << std::setprecision(2)
                  << std::setw(6) << i
                  << std::setw(12) << x
                  << std::setw(12) << y
                  << std::setw(14) << angle_rad
                  << std::setw(14) << angle_deg
                  << std::setw(16) << dist
                  << std::setw(10) << (pass ? "PASS" : "FAIL")
                  << "\n";
    }

    std::cout << "--------------------------------------------------------------------------------\n";
    std::cout << "\n";

    // Verify all agents
    std::cout << "Verifying all " << NUM_INIT_AGENTS << " agents...\n";

    pass_count = 0;
    fail_count = 0;

    for (int i = 0; i < NUM_INIT_AGENTS; i++) {
        double x = fp_to_float(AGENT_INIT_DATA[i][0]);
        double y = fp_to_float(AGENT_INIT_DATA[i][1]);
        double dist = distance_from_center(x, y, cx, cy);
        double error = fabs(dist - expected_radius) / expected_radius;

        if (error < 0.01) {
            pass_count++;
        } else {
            fail_count++;
            std::cout << "  WARNING: Agent " << i << " distance error: "
                      << (error * 100.0) << "%\n";
        }
    }

    std::cout << "\n";
    std::cout << "Results:\n";
    std::cout << "  PASS: " << pass_count << "/" << NUM_INIT_AGENTS << "\n";
    std::cout << "  FAIL: " << fail_count << "/" << NUM_INIT_AGENTS << "\n";
    std::cout << "\n";

    if (fail_count == 0) {
        std::cout << "✓ All agents verified successfully!\n";
        std::cout << "  - All agents are positioned on circle with 40% radius\n";
        std::cout << "  - Ready for use in RTL testbench\n";
    } else {
        std::cout << "✗ Verification failed!\n";
        std::cout << "  - Some agents are not correctly positioned\n";
    }

    std::cout << "\n";
    std::cout << "================================================================================\n";

    return (fail_count == 0) ? 0 : 1;
}
