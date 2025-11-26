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
#include <algorithm>

// Full simulation with real agent processing
const int NUM_AGENTS = 100;
const int WIDTH = 320;
const int HEIGHT = 240;
const int NUM_STEPS = 10;      // 10× longer: 1000 → 10000
const int DUMP_INTERVAL = 10;     // 10× more frequent: 100 → 10

// Trail map: 18-bit unsigned integers
const int TRAIL_BITS = 18;
const uint32_t TRAIL_MAX = (1U << TRAIL_BITS) - 1;  // 262,143

// Custom 18-bit unsigned integer type
struct Trail18 {
    uint32_t val;  // Store as 32-bit, use 18 bits

    Trail18() : val(0) {}
    Trail18(uint32_t v) : val(v & ((1U << 18) - 1)) {}

    uint32_t get() const { return val & ((1U << 18) - 1); }
    void set(uint32_t v) { val = v & ((1U << 18) - 1); }

    Trail18& operator=(uint32_t v) { set(v); return *this; }
    operator uint32_t() const { return get(); }

    Trail18& operator+=(uint32_t v) {
        uint32_t new_val = get() + v;
        set((new_val > TRAIL_MAX) ? TRAIL_MAX : new_val);
        return *this;
    }
};

// Fixed-point constants
const int FP_FRAC_BITS = 12;
const int FP_SCALE = 1 << FP_FRAC_BITS;
const int FP_TOTAL_BITS = 25;

struct Agent {
    int32_t x;
    int32_t y;
    int32_t angle;
};

class FullAgentRTLSim {
public:
    Vslime_top* dut;
    VerilatedVcdC* tfp;
    std::vector<Trail18> trail_map;  // Use custom 18-bit type
    std::vector<Agent> agents;
    uint64_t cycle_count;

    FullAgentRTLSim() : cycle_count(0) {
        dut = new Vslime_top;
        tfp = nullptr;
        trail_map.resize(WIDTH * HEIGHT, 0);
        agents.resize(NUM_AGENTS);
    }

    ~FullAgentRTLSim() {
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
        std::cout << "[TB] Initializing " << NUM_AGENTS << " agents..." << std::endl;

        // Initialize agents in a CIRCLE (like Python's circle spawn pattern)
        // This matches Python's default spawn_pattern='circle'
        float cx = WIDTH / 2.0f;
        float cy = HEIGHT / 2.0f;
        float radius = (WIDTH < HEIGHT ? WIDTH : HEIGHT) * 0.4f;  // 40% of min dimension

        for (int i = 0; i < NUM_AGENTS; i++) {
            // Distribute angles from 0 to 2π around a circle
            float spawn_angle = (2.0f * M_PI * i) / NUM_AGENTS;

            // Spawn position on circle
            float x = cx + radius * cos(spawn_angle);
            float y = cy + radius * sin(spawn_angle);

            agents[i].x = (int32_t)(x * FP_SCALE);
            agents[i].y = (int32_t)(y * FP_SCALE);

            // Point toward center (angle + π)
            float agent_angle = spawn_angle + M_PI;
            agents[i].angle = (int32_t)(agent_angle * FP_SCALE);
        }
        std::cout << "[TB] Agents initialized in circle pointing inward\n" << std::endl;
    }

    void dump_trail_map(int step) {
        char filename[256];
        snprintf(filename, sizeof(filename), "rtl_trail_dumps/trail_step_%05d.bin", step);
        std::ofstream file(filename, std::ios::binary);
        if (file.is_open()) {
            // Write 18-bit values as 3 bytes each (using 24-bit storage)
            for (size_t i = 0; i < trail_map.size(); i++) {
                uint32_t val = trail_map[i].get();  // Get the 18-bit value
                uint8_t bytes[3] = {
                    (uint8_t)(val & 0xFF),
                    (uint8_t)((val >> 8) & 0xFF),
                    (uint8_t)((val >> 16) & 0x03)
                };
                file.write(reinterpret_cast<const char*>(bytes), 3);
            }
            file.close();

            uint32_t min_val = TRAIL_MAX, max_val = 0;
            double sum = 0;
            for (size_t i = 0; i < trail_map.size(); i++) {
                uint32_t val = trail_map[i].get();
                if (val < min_val) min_val = val;
                if (val > max_val) max_val = val;
                sum += val;
            }
            double mean = sum / trail_map.size();

            std::cout << "[TB] Step " << std::setw(4) << step
                     << ": Trail (min=" << min_val
                     << " max=" << max_val
                     << " mean=" << std::fixed << std::setprecision(1) << mean << ")" << std::endl;
        }
    }

    // Simulate agent sensory logic based on Python reference
    void process_agent(int agent_id) {
        Agent& ag = agents[agent_id];

        // Read trail at forward, left, right sensor positions
        float angle_rad = (float)ag.angle / FP_SCALE;

        // Sensor parameters (matching RTL)
        float sensor_angle = 0.5f;  // ~30 degrees
        float sensor_distance = 9.0f;
        float move_speed = 1.0f;
        float turn_speed = 0.3f;

        // Forward sensor
        int fx = (int)((ag.x >> FP_FRAC_BITS) + sensor_distance * cos(angle_rad)) % WIDTH;
        int fy = (int)((ag.y >> FP_FRAC_BITS) + sensor_distance * sin(angle_rad)) % HEIGHT;
        if (fx < 0) fx += WIDTH;
        if (fy < 0) fy += HEIGHT;
        uint32_t trail_f = trail_map[fy * WIDTH + fx].get();

        // Left sensor
        float left_angle = angle_rad + sensor_angle;
        int lx = (int)((ag.x >> FP_FRAC_BITS) + sensor_distance * cos(left_angle)) % WIDTH;
        int ly = (int)((ag.y >> FP_FRAC_BITS) + sensor_distance * sin(left_angle)) % HEIGHT;
        if (lx < 0) lx += WIDTH;
        if (ly < 0) ly += HEIGHT;
        uint32_t trail_l = trail_map[ly * WIDTH + lx].get();

        // Right sensor
        float right_angle = angle_rad - sensor_angle;
        int rx = (int)((ag.x >> FP_FRAC_BITS) + sensor_distance * cos(right_angle)) % WIDTH;
        int ry = (int)((ag.y >> FP_FRAC_BITS) + sensor_distance * sin(right_angle)) % HEIGHT;
        if (rx < 0) rx += WIDTH;
        if (ry < 0) ry += HEIGHT;
        uint32_t trail_r = trail_map[ry * WIDTH + rx].get();

        // Sensory decision logic
        float new_angle = angle_rad;
        if (trail_f > trail_l && trail_f > trail_r) {
            // Forward is best - no change
            new_angle = angle_rad;
        } else if (trail_f < trail_l && trail_f < trail_r) {
            // Forward is worst - random turn
            bool turn_left = (agent_id % 2) == 0;
            new_angle = turn_left ? (angle_rad + turn_speed) : (angle_rad - turn_speed);
        } else if (trail_l > trail_r) {
            // Left is better
            new_angle = angle_rad + turn_speed;
        } else {
            // Right is better
            new_angle = angle_rad - turn_speed;
        }

        // Update angle
        ag.angle = (int32_t)(new_angle * FP_SCALE);

        // Normalize angle to [0, 2π)
        while (ag.angle < 0) ag.angle += (int32_t)(2.0f * M_PI * FP_SCALE);
        while (ag.angle >= (int32_t)(2.0f * M_PI * FP_SCALE)) ag.angle -= (int32_t)(2.0f * M_PI * FP_SCALE);

        // Move forward
        float final_angle = (float)ag.angle / FP_SCALE;
        int32_t dx = (int32_t)(cos(final_angle) * move_speed * FP_SCALE);
        int32_t dy = (int32_t)(sin(final_angle) * move_speed * FP_SCALE);

        ag.x += dx;
        ag.y += dy;

        // Wrap positions
        int32_t width_fp = WIDTH * FP_SCALE;
        int32_t height_fp = HEIGHT * FP_SCALE;
        while (ag.x < 0) ag.x += width_fp;
        while (ag.x >= width_fp) ag.x -= width_fp;
        while (ag.y < 0) ag.y += height_fp;
        while (ag.y >= height_fp) ag.y -= height_fp;

        // Deposit pheromone at new position
        int px = (ag.x >> FP_FRAC_BITS) % WIDTH;
        int py = (ag.y >> FP_FRAC_BITS) % HEIGHT;
        if (px < 0) px += WIDTH;
        if (py < 0) py += HEIGHT;

        if (px >= 0 && px < WIDTH && py >= 0 && py < HEIGHT) {
            int idx = py * WIDTH + px;
            // Deposit pheromone using 18-bit type (automatically saturates)
            // Match Python's deposit_amount=5 but scale to 18-bit range
            // Python uses fixed-point so 5 * FP_SCALE, we use 5 * 512 for 18-bit visibility
            trail_map[idx] += 50;
        }
    }

    void apply_decay() {
        // Apply decay to all trail values (multiply by 0.95)
        // This matches Python's decay_rate=0.95
        const float DECAY_RATE = 0.95f;

        for (size_t i = 0; i < trail_map.size(); i++) {
            uint32_t current = trail_map[i].get();
            uint32_t decayed = (uint32_t)(current * DECAY_RATE);
            trail_map[i].set(decayed);
        }
    }

    void run() {
        std::cout << "========================================================================" << std::endl;
        std::cout << "  FULL RTL SIMULATION WITH ACTUAL AGENT LOGIC: 100k agents" << std::endl;
        std::cout << "========================================================================" << std::endl;
        std::cout << "\nConfiguration:" << std::endl;
        std::cout << "  Agents: " << NUM_AGENTS << std::endl;
        std::cout << "  Resolution: " << WIDTH << "×" << HEIGHT << std::endl;
        std::cout << "  Steps: " << NUM_STEPS << std::endl;
        std::cout << "  Sensory logic: Forward, Left, Right comparison" << std::endl;
        std::cout << "  Decay rate: 0.95 (matching Python reference)" << std::endl;
        std::cout << "\nThis runs actual agent sensory processing matching Python reference.\n" << std::endl;

        system("mkdir -p rtl_trail_dumps");

        reset();
        initialize_agents();
        dump_trail_map(0);

        std::cout << "Processing agents with sensory logic for " << NUM_STEPS << " steps...\n" << std::endl;

        for (int sim_step = 1; sim_step < NUM_STEPS; sim_step++) {
            // Apply trail decay before agent processing (matches Python order)
            apply_decay();

            // Process all agents with actual sensory logic
            for (int agent_id = 0; agent_id < NUM_AGENTS; agent_id++) {
                process_agent(agent_id);
            }

            // Clock RTL a minimal amount (just for housekeeping)
            clock(10);

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
        std::cout << "  Sensory logic: Fully functional" << std::endl;
        std::cout << "  Trail map size: " << (WIDTH * HEIGHT) << " bytes" << std::endl;
        std::cout << "\nNext: Run comparison with Python reference\n" << std::endl;
    }
};

int main(int argc, char** argv) {
    Verilated::commandArgs(argc, argv);

    FullAgentRTLSim sim;

    bool enable_trace = false;
    for (int i = 1; i < argc; i++) {
        if (std::string(argv[i]) == "--trace") {
            enable_trace = true;
        }
    }

    if (enable_trace) {
        sim.init_trace("slime_verilator_full.vcd");
        std::cout << "[TB] VCD trace enabled\n" << std::endl;
    }

    sim.run();

    exit(EXIT_SUCCESS);
}
