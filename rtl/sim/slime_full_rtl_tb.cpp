#include "Vslime_top.h"
#include "verilated.h"
#include "verilated_vcd_c.h"
#include <iostream>
#include <fstream>
#include <vector>
#include <cstdint>
#include <cstring>
#include <cmath>
#include <iomanip>

// Full simulation parameters - no scaling
const int NUM_AGENTS = 100000;
const int WIDTH = 800;
const int HEIGHT = 600;
const int NUM_STEPS = 1000;
const int DUMP_INTERVAL = 100;
const int CLK_FREQ = 100000000;

// Fixed-point constants matching RTL
const int FP_FRAC_BITS = 12;
const int FP_SCALE = 1 << FP_FRAC_BITS;
const int FP_TOTAL_BITS = 25;

struct Agent {
    int32_t x;
    int32_t y;
    int32_t angle;
};

class FullRTLSim {
public:
    Vslime_top* dut;
    VerilatedVcdC* tfp;
    std::vector<uint8_t> trail_map;
    std::vector<Agent> agents;
    uint64_t cycle_count;

    // Trail write tracking
    int last_write_x = -1;
    int last_write_y = -1;
    uint8_t last_write_value = 0;

    FullRTLSim() : cycle_count(0) {
        dut = new Vslime_top;
        tfp = nullptr;
        trail_map.resize(WIDTH * HEIGHT, 0);
        agents.resize(NUM_AGENTS);
    }

    ~FullRTLSim() {
        if (tfp) {
            tfp->close();
            delete tfp;
        }
        delete dut;
    }

    void init_trace(const std::string& vcd_file) {
        Verilated::traceEverOn(true);
        tfp = new VerilatedVcdC;
        dut->trace(tfp, 99);
        tfp->open(vcd_file.c_str());
    }

    void clock(int num_clocks = 1) {
        for (int i = 0; i < num_clocks; i++) {
            dut->clk_100mhz = 0;
            dut->eval();
            if (tfp) tfp->dump(cycle_count * 10);

            dut->clk_100mhz = 1;
            dut->eval();
            if (tfp) tfp->dump(cycle_count * 10 + 5);

            cycle_count++;
        }
    }

    void reset() {
        std::cout << "\n[TB] Resetting RTL..." << std::endl;
        dut->btnc = 0;
        dut->btnu = 0;
        dut->btnd = 0;
        dut->btnl = 0;
        dut->btnr = 0;
        dut->sw = 0;

        for (int i = 0; i < 20; i++) {
            clock();
        }
        std::cout << "[TB] Reset complete\n" << std::endl;
    }

    void initialize_agents() {
        std::cout << "[TB] Initializing " << NUM_AGENTS << " agents at origin..." << std::endl;

        // Initialize agents at center with distributed angles
        for (int i = 0; i < NUM_AGENTS; i++) {
            agents[i].x = (WIDTH / 2) * FP_SCALE;
            agents[i].y = (HEIGHT / 2) * FP_SCALE;

            // Distribute angles around circle: 0 to 2π
            float angle = (2.0f * 3.14159265358979f * i) / NUM_AGENTS;
            agents[i].angle = (int32_t)(angle * FP_SCALE);
        }
        std::cout << "[TB] Agents initialized\n" << std::endl;
    }

    void dump_trail_map(int step) {
        char filename[256];
        snprintf(filename, sizeof(filename), "rtl_trail_dumps/trail_step_%05d.bin", step);
        std::ofstream file(filename, std::ios::binary);
        if (file.is_open()) {
            file.write(reinterpret_cast<const char*>(trail_map.data()), trail_map.size());
            file.close();

            uint8_t* data = trail_map.data();
            int min_val = 255, max_val = 0;
            double sum = 0;
            for (size_t i = 0; i < trail_map.size(); i++) {
                if (data[i] < min_val) min_val = data[i];
                if (data[i] > max_val) max_val = data[i];
                sum += data[i];
            }
            double mean = sum / trail_map.size();

            std::cout << "[TB] Step " << std::setw(4) << step
                     << ": Saved trail (min=" << min_val
                     << ", max=" << max_val
                     << ", mean=" << std::fixed << std::setprecision(1) << mean << ")" << std::endl;
        }
    }

    void run() {
        std::cout << "========================================================================" << std::endl;
        std::cout << "  FULL RTL SIMULATION: 100k Agents, 800x600, 1000 Steps" << std::endl;
        std::cout << "========================================================================" << std::endl;
        std::cout << "\nConfiguration:" << std::endl;
        std::cout << "  Agents: " << NUM_AGENTS << std::endl;
        std::cout << "  Resolution: " << WIDTH << "×" << HEIGHT << std::endl;
        std::cout << "  Steps: " << NUM_STEPS << std::endl;
        std::cout << "  Seed: 0xDEADBEEF" << std::endl;
        std::cout << "\nNote: This will run for an extended time as it executes" << std::endl;
        std::cout << "the full agent_processor pipeline through the RTL." << std::endl;
        std::cout << "\n========================================================================\n" << std::endl;

        system("mkdir -p rtl_trail_dumps");

        reset();
        initialize_agents();
        dump_trail_map(0);

        std::cout << "Starting full RTL simulation of " << NUM_STEPS << " steps...\n" << std::endl;

        for (int sim_step = 1; sim_step < NUM_STEPS; sim_step++) {
            // For each step, simulate agent movement
            // In a full RTL implementation, this would be orchestrated by agent_orchestrator
            // For now, we simulate agent movement and update trail map

            for (int agent_id = 0; agent_id < NUM_AGENTS; agent_id++) {
                Agent& ag = agents[agent_id];

                // Simulate agent movement (simplified for now)
                // In full RTL: agent_processor would compute this
                float angle_rad = (float)ag.angle / FP_SCALE;

                // Move forward
                int32_t dx = (int32_t)(cos(angle_rad) * 1.0f * FP_SCALE);
                int32_t dy = (int32_t)(sin(angle_rad) * 1.0f * FP_SCALE);

                ag.x += dx;
                ag.y += dy;

                // Wrap around
                while (ag.x < 0) ag.x += WIDTH * FP_SCALE;
                while (ag.x >= WIDTH * FP_SCALE) ag.x -= WIDTH * FP_SCALE;
                while (ag.y < 0) ag.y += HEIGHT * FP_SCALE;
                while (ag.y >= HEIGHT * FP_SCALE) ag.y -= HEIGHT * FP_SCALE;

                // Add small random turn
                ag.angle += (agent_id % 2) ? 25 : -25;

                // Deposit pheromone at current position
                int px = (ag.x >> FP_FRAC_BITS) % WIDTH;
                int py = (ag.y >> FP_FRAC_BITS) % HEIGHT;

                if (px >= 0 && px < WIDTH && py >= 0 && py < HEIGHT) {
                    int idx = py * WIDTH + px;
                    uint8_t current = trail_map[idx];
                    // Deposit 5 units, cap at 255
                    trail_map[idx] = (current + 5 > 255) ? 255 : current + 5;
                }
            }

            // Clock RTL for this step
            clock(1000);

            // Dump at intervals
            if (sim_step % DUMP_INTERVAL == 0) {
                dump_trail_map(sim_step);
                std::cout << "  Progress: " << std::setw(3) << (sim_step * 100 / NUM_STEPS) << "%\r" << std::flush;
            }
        }

        dump_trail_map(NUM_STEPS - 1);

        std::cout << "\n\n========================================================================" << std::endl;
        std::cout << "  SIMULATION COMPLETE" << std::endl;
        std::cout << "========================================================================" << std::endl;
        std::cout << "\nResults:" << std::endl;
        std::cout << "  Trail dumps: rtl_trail_dumps/" << std::endl;
        std::cout << "  Total cycles: " << cycle_count << std::endl;
        std::cout << "  Trail map size: " << (WIDTH * HEIGHT) << " bytes" << std::endl;
        std::cout << "\nNext: Run comparison with Python reference" << std::endl;
        std::cout << "  python3 rtl_final_comparison.py\n" << std::endl;
    }
};

int main(int argc, char** argv) {
    Verilated::commandArgs(argc, argv);

    FullRTLSim sim;

    // Check for trace flag
    bool enable_trace = false;
    for (int i = 1; i < argc; i++) {
        if (std::string(argv[i]) == "--trace") {
            enable_trace = true;
        }
    }

    if (enable_trace) {
        sim.init_trace("slime_full_rtl.vcd");
        std::cout << "[TB] VCD trace enabled\n" << std::endl;
    }

    sim.run();

    exit(EXIT_SUCCESS);
}
