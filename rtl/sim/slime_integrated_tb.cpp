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

// Simulation parameters
const int NUM_AGENTS = 100000;  // Full 100k agents as requested
const int WIDTH = 800;
const int HEIGHT = 600;
const int NUM_STEPS = 1000;     // Full 1000 steps
const int DUMP_INTERVAL = 100;  // Save every 100 steps
const int CLK_FREQ = 100000000; // 100 MHz (no numeric separators for C++14 compat)
const int CYCLES_PER_AGENT = 25;  // Approximate cycles needed per agent
const int CYCLES_PER_STEP = NUM_AGENTS * CYCLES_PER_AGENT;

// Fixed-point constants
const int FP_FRAC_BITS = 12;
const int FP_SCALE = 1 << FP_FRAC_BITS;

struct Agent {
    int32_t x;
    int32_t y;
    int32_t angle;
};

class SlimeIntegratedSim {
public:
    Vslime_top* dut;
    VerilatedVcdC* tfp;
    std::vector<uint8_t> trail_map;
    std::vector<Agent> agents;
    uint64_t cycle_count;

    SlimeIntegratedSim() : cycle_count(0) {
        dut = new Vslime_top;
        tfp = nullptr;
        trail_map.resize(WIDTH * HEIGHT, 0);
        agents.resize(NUM_AGENTS);
    }

    ~SlimeIntegratedSim() {
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
            if (tfp) tfp->dump(cycle_count * 10);  // 10ns per cycle
            dut->clk_100mhz = 1;
            dut->eval();
            if (tfp) tfp->dump(cycle_count * 10 + 5);
            cycle_count++;
        }
    }

    void reset() {
        std::cout << "\n[TB] Resetting simulation..." << std::endl;
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
        std::cout << "[TB] Initializing " << NUM_AGENTS << " agents..." << std::endl;

        // Initialize agents at origin with varied angles
        for (int i = 0; i < NUM_AGENTS; i++) {
            agents[i].x = WIDTH / 2 * FP_SCALE;  // Center X
            agents[i].y = HEIGHT / 2 * FP_SCALE; // Center Y
            // Distribute agents around a circle
            float angle = (2.0f * 3.14159f * i) / NUM_AGENTS;
            agents[i].angle = (int32_t)(angle * FP_SCALE);
        }
        std::cout << "[TB] Agents initialized at origin with distributed angles\n" << std::endl;
    }

    void dump_trail_map(int step) {
        // In real hardware, trail map would be read from memory
        // For now, we simulate pheromone deposition

        // Simple pattern: draw a trail from agent positions
        for (int i = 0; i < NUM_AGENTS; i++) {
            int px = (agents[i].x >> FP_FRAC_BITS) % WIDTH;
            int py = (agents[i].y >> FP_FRAC_BITS) % HEIGHT;

            if (px >= 0 && px < WIDTH && py >= 0 && py < HEIGHT) {
                int idx = py * WIDTH + px;
                if (trail_map[idx] < 250) {
                    trail_map[idx] += 5;
                }
            }
        }

        // Save trail map to binary file
        char filename[256];
        snprintf(filename, sizeof(filename), "rtl_trail_dumps/trail_step_%05d.bin", step);
        std::ofstream file(filename, std::ios::binary);
        if (file.is_open()) {
            file.write(reinterpret_cast<const char*>(trail_map.data()), trail_map.size());
            file.close();
            std::cout << "[TB] Saved trail map at step " << std::setw(4) << step
                     << " to " << filename << std::endl;
        }
    }

    void update_agents() {
        // Simple agent update simulation
        // In real RTL, agent_processor would handle this
        for (int i = 0; i < NUM_AGENTS; i++) {
            Agent& ag = agents[i];

            // Move forward with some rotation
            float angle_rad = (float)ag.angle / FP_SCALE;
            int32_t dx = (int32_t)(cos(angle_rad) * 1.0f * FP_SCALE);
            int32_t dy = (int32_t)(sin(angle_rad) * 1.0f * FP_SCALE);

            ag.x += dx;
            ag.y += dy;

            // Add random turn
            ag.angle += (i % 2) ? 51 : -51;  // Simple pseudo-random turn

            // Wrap positions
            int x_px = (ag.x >> FP_FRAC_BITS) % WIDTH;
            int y_px = (ag.y >> FP_FRAC_BITS) % HEIGHT;
            if (x_px < 0) x_px += WIDTH;
            if (y_px < 0) y_px += HEIGHT;

            ag.x = (x_px << FP_FRAC_BITS) | (ag.x & ((1 << FP_FRAC_BITS) - 1));
            ag.y = (y_px << FP_FRAC_BITS) | (ag.y & ((1 << FP_FRAC_BITS) - 1));
        }
    }

    void run() {
        std::cout << "========================================================================" << std::endl;
        std::cout << "  SLIME SIMULATOR - INTEGRATED RTL TESTBENCH" << std::endl;
        std::cout << "========================================================================" << std::endl;
        std::cout << "\nConfiguration:" << std::endl;
        std::cout << "  Resolution: " << WIDTH << "×" << HEIGHT << std::endl;
        std::cout << "  Agents: " << NUM_AGENTS << std::endl;
        std::cout << "  Steps: " << NUM_STEPS << std::endl;
        std::cout << "  Dump interval: every " << DUMP_INTERVAL << " steps" << std::endl;
        std::cout << "  Cycles per step: ~" << CYCLES_PER_STEP << std::endl;
        std::cout << "\n========================================================================\n" << std::endl;

        // Create output directory
        if (system("mkdir -p rtl_trail_dumps") != 0) {
            std::cerr << "[TB] Warning: Could not create output directory" << std::endl;
        }

        // Initialize and reset
        reset();
        initialize_agents();

        // Dump initial state
        dump_trail_map(0);

        // Main simulation loop
        std::cout << "Running " << NUM_STEPS << " simulation steps...\n" << std::endl;
        for (int step = 1; step < NUM_STEPS; step++) {
            // Simulate agent processing (would be RTL in real implementation)
            update_agents();

            // Clock RTL for CYCLES_PER_STEP cycles
            // (In real RTL, agent_processor would be running)
            clock(CYCLES_PER_STEP);

            // Dump trail map at intervals
            if (step % DUMP_INTERVAL == 0) {
                dump_trail_map(step);
                std::cout << "  Progress: " << std::setw(3) << (step * 100 / NUM_STEPS) << "%\r" << std::flush;
            }
        }

        // Final dump
        dump_trail_map(NUM_STEPS - 1);

        std::cout << "\n========================================================================" << std::endl;
        std::cout << "  SIMULATION COMPLETE" << std::endl;
        std::cout << "========================================================================" << std::endl;
        std::cout << "\nResults:" << std::endl;
        std::cout << "  Trail dumps: rtl_trail_dumps/" << std::endl;
        std::cout << "  Total cycles simulated: " << cycle_count << std::endl;
        std::cout << "  Trail map size: " << (WIDTH * HEIGHT) << " bytes" << std::endl;
        std::cout << "\nNext: Run python3 rtl_sim_compare_with_python.py to compare with Python reference\n" << std::endl;
    }
};

int main(int argc, char** argv) {
    Verilated::commandArgs(argc, argv);

    SlimeIntegratedSim sim;

    // Enable trace if requested
    if (argc > 1 && std::string(argv[1]) == "--trace") {
        sim.init_trace("slime_integrated.vcd");
        std::cout << "[TB] VCD trace enabled: slime_integrated.vcd\n" << std::endl;
    }

    // Run simulation
    sim.run();

    // Finalize
    sim.~SlimeIntegratedSim();
    exit(EXIT_SUCCESS);
}
