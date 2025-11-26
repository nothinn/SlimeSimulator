#include "Vslime_top.h"
#include "verilated.h"
#include "verilated_vcd_c.h"
#include <iostream>
#include <fstream>
#include <cstring>
#include <cstdint>
#include <vector>
#include <iomanip>
#include <sstream>

// Simulation constants
const int NUM_AGENTS = 100000;
const int WIDTH = 800;
const int HEIGHT = 600;
const int NUM_STEPS = 1000;
const int DUMP_INTERVAL = 100;  // Save trail map every 100 steps
const int CLK_FREQ = 100000000; // 100 MHz

struct TrailMapDump {
    int step;
    std::vector<uint8_t> trail_map;
};

class SlimeTopSimulation {
public:
    Vslime_top* dut;
    VerilatedVcdC* tfp;
    std::vector<TrailMapDump> trail_dumps;
    uint64_t tick_count;

    SlimeTopSimulation() {
        dut = new Vslime_top;
        tfp = nullptr;
        tick_count = 0;
    }

    ~SlimeTopSimulation() {
        if (tfp) {
            tfp->close();
            delete tfp;
        }
        delete dut;
    }

    void init_trace(const std::string& vcd_file = "slime_sim.vcd") {
        Verilated::traceEverOn(true);
        tfp = new VerilatedVcdC;
        dut->trace(tfp, 99);
        tfp->open(vcd_file.c_str());
    }

    void clock() {
        dut->clk_100mhz = 0;
        eval();
        dut->clk_100mhz = 1;
        eval();
        tick_count++;
    }

    void eval() {
        dut->eval();
        if (tfp) tfp->dump(tick_count * 5);  // 5ns per time unit
    }

    void reset() {
        std::cout << "[TB] Resetting simulation..." << std::endl;
        dut->btnc = 0;
        dut->btnu = 0;
        dut->btnd = 0;
        dut->btnl = 0;
        dut->btnr = 0;
        dut->sw = 0;
        for (int i = 0; i < 10; i++) {
            clock();
        }
        std::cout << "[TB] Reset complete" << std::endl;
    }

    void start_simulation() {
        std::cout << "[TB] Starting simulation..." << std::endl;
        dut->btnc = 1;
        clock();
        clock();
        dut->btnc = 0;
        clock();
    }

    void run(int num_steps) {
        std::cout << "[TB] Running " << num_steps << " simulation steps..." << std::endl;
        std::cout << "[TB] Configuration:" << std::endl;
        std::cout << "     Resolution: " << WIDTH << "x" << HEIGHT << std::endl;
        std::cout << "     Agents: " << NUM_AGENTS << std::endl;
        std::cout << "     Steps: " << num_steps << std::endl;
        std::cout << "     Dump interval: every " << DUMP_INTERVAL << " steps" << std::endl << std::endl;

        for (int step = 0; step < num_steps; step++) {
            // Clock many cycles per simulation step
            // RTL processes agents in pipeline, so each agent takes ~19 cycles
            // For 100k agents, we need roughly (100000 * 19 / 1000) = 1900 cycles per step
            // But let's use a simpler ratio
            const int CYCLES_PER_STEP = 2000;

            for (int c = 0; c < CYCLES_PER_STEP; c++) {
                clock();
            }

            if ((step + 1) % DUMP_INTERVAL == 0 || step == num_steps - 1) {
                std::cout << "[TB] Step " << (step + 1) << "/" << num_steps
                          << " (" << ((step + 1) * 100 / num_steps) << "%)" << std::endl;
            }
        }
    }

    void dump_trail_map(int step) {
        // Note: In a real RTL implementation, we would read the trail map from BRAM
        // This is a placeholder that will be filled by actual memory reads
        TrailMapDump dump;
        dump.step = step;
        dump.trail_map.resize(WIDTH * HEIGHT, 0);  // Placeholder
        trail_dumps.push_back(dump);
    }

    void save_trail_dumps(const std::string& output_dir) {
        std::cout << "[TB] Saving trail map dumps to " << output_dir << std::endl;

        // Create output directory
        std::string mkdir_cmd = "mkdir -p " + output_dir;
        system(mkdir_cmd.c_str());

        // Save trail dumps as binary files
        for (const auto& dump : trail_dumps) {
            std::ostringstream filename;
            filename << output_dir << "/trail_step_" << std::setfill('0')
                    << std::setw(5) << dump.step << ".bin";

            std::ofstream file(filename.str(), std::ios::binary);
            if (file.is_open()) {
                file.write(reinterpret_cast<const char*>(dump.trail_map.data()),
                          dump.trail_map.size());
                file.close();
            }
        }
    }
};

int main(int argc, char** argv) {
    std::cout << "========================================================================" << std::endl;
    std::cout << "  SLIME SIMULATOR RTL SIMULATION (Verilator)" << std::endl;
    std::cout << "========================================================================" << std::endl << std::endl;

    Verilated::commandArgs(argc, argv);

    SlimeTopSimulation sim;

    // Initialize tracing if requested
    bool enable_vcd = false;
    for (int i = 1; i < argc; i++) {
        if (std::string(argv[i]) == "--vcd") {
            enable_vcd = true;
        }
    }

    if (enable_vcd) {
        sim.init_trace("rtl_sim_100k.vcd");
        std::cout << "[TB] VCD tracing enabled -> rtl_sim_100k.vcd" << std::endl << std::endl;
    }

    sim.reset();
    sim.start_simulation();
    sim.run(NUM_STEPS);

    // Capture some trail dumps (placeholder)
    for (int step = 0; step < NUM_STEPS; step += DUMP_INTERVAL) {
        sim.dump_trail_map(step);
    }
    sim.dump_trail_map(NUM_STEPS - 1);

    sim.save_trail_dumps("rtl_trail_dumps");

    if (Verilated::gotFinish()) {
        std::cout << "[TB] Simulation finished via $finish" << std::endl;
    }

    std::cout << std::endl << "========================================================================" << std::endl;
    std::cout << "  SIMULATION COMPLETE" << std::endl;
    std::cout << "========================================================================" << std::endl;

    return 0;
}
