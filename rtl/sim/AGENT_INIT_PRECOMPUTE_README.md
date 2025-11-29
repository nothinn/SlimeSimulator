# Agent Initialization Pre-Computation Guide

## Overview

This directory contains tools to generate pre-computed agent initialization data from the Python reference implementation for use in C++ RTL testbenches.

**Problem Solved:** RTL initialization code was having compilation issues when trying to compute circle spawn positions on-the-fly. This solution pre-computes the exact initialization values using the Python reference and outputs them as C++ arrays.

## Files

| File | Description |
|------|-------------|
| `generate_cpp_agent_init.py` | Main script to generate C++ initialization code from Python reference |
| `verify_agent_init.py` | Verification script to validate generated values |
| `agent_init_data.h` | Generated C++ header with pre-computed agent data (auto-generated) |

## Quick Start

### 1. Generate C++ Initialization Data

```bash
cd /home/reson/SlimeSimulator
source .venv/bin/activate
cd rtl/sim

# Generate initialization data for 100 agents at 320x240 resolution
python3 generate_cpp_agent_init.py --num-agents 100 --width 320 --height 240
```

This creates `agent_init_data.h` with:
- `AGENT_INIT_DATA[][3]` - Array of {x_fp, y_fp, angle_fp} for each agent
- `NUM_INIT_AGENTS` - Number of agents in the array
- `initialize_agents_from_precomputed()` - Function to load data into RTL

### 2. Verify Generated Data

```bash
python3 verify_agent_init.py
```

This validates:
- All agents are positioned on circle with 40% radius
- All agents point inward toward center
- Agents are evenly distributed around the circle

### 3. Use in C++ Testbench

Include the generated header and call the initialization function:

```cpp
#include "agent_init_data.h"

// In your testbench (after reset, before simulation):
void setup_simulation() {
    reset();  // Reset the DUT

    // Load pre-computed agent positions
    initialize_agents_from_precomputed();

    // Continue with simulation...
}
```

## Implementation Details

### Circle Spawn Pattern

The generated data matches the Python reference implementation's `spawn_pattern='circle'` logic:

1. **Position Calculation:**
   - Center: (WIDTH/2, HEIGHT/2)
   - Radius: min(WIDTH, HEIGHT) × 0.4
   - Agent i spawns at angle: 2π × i / NUM_AGENTS
   - Position: (cx + cos(θ)×r, cy + sin(θ)×r)

2. **Angle Calculation:**
   - Each agent points toward center
   - Agent angle = spawn_angle + π (mod 2π)

3. **Fixed-Point Format:**
   - Q12.12 format (12 integer bits, 12 fractional bits)
   - Scale: 4096 (1.0 = 0x1000)
   - Range: -2048.0 to +2047.9998

### Data Format

Each agent is represented as a 3-element array:

```cpp
{x_fp, y_fp, angle_fp}
```

Where:
- `x_fp`: X position in fixed-point (Q12.12)
- `y_fp`: Y position in fixed-point (Q12.12)
- `angle_fp`: Angle in radians in fixed-point (Q12.12)

All values are in hexadecimal for clarity and stored as signed 32-bit integers.

### Example Values (320×240, first 5 agents)

| Agent | X (px)  | Y (px)  | Angle (rad) | Angle (deg) | X (hex)      | Y (hex)      | Angle (hex)  |
|-------|---------|---------|-------------|-------------|--------------|--------------|--------------|
| 0     | 256.00  | 120.00  | 3.141602    | 180.0       | 0x00100000   | 0x00078000   | 0x00003244   |
| 1     | 255.81  | 125.88  | 3.204346    | 183.6       | 0x000FFD00   | 0x0007DE20   | 0x00003345   |
| 2     | 255.27  | 131.74  | 3.267334    | 187.2       | 0x000FF460   | 0x00083BE0   | 0x00003447   |
| 3     | 254.38  | 137.58  | 3.330078    | 190.8       | 0x000FE620   | 0x00089940   | 0x00003548   |
| 4     | 253.12  | 143.32  | 3.392822    | 194.4       | 0x000FD1E0   | 0x0008F520   | 0x00003649   |

## Command-Line Options

### generate_cpp_agent_init.py

```bash
python3 generate_cpp_agent_init.py [OPTIONS]

Options:
  --num-agents N         Number of agents to generate (default: 100)
  --width W              Simulation width in pixels (default: 320)
  --height H             Simulation height in pixels (default: 240)
  --output FILE          Output C++ header file (default: agent_init_data.h)
  --verify-first N       Number of agents to print for verification (default: 5)
```

### Examples

```bash
# Generate for 1000 agents at 800x600
python3 generate_cpp_agent_init.py --num-agents 1000 --width 800 --height 600

# Generate with custom output file
python3 generate_cpp_agent_init.py --output my_agents.h

# Show first 10 agents for verification
python3 generate_cpp_agent_init.py --verify-first 10
```

## Verification

The `verify_agent_init.py` script performs the following checks:

1. **Distance Verification:** Ensures all agents are positioned exactly at 40% radius
2. **Angle Verification:** Confirms agents point inward (toward center)
3. **Distribution Verification:** Validates even spacing around the circle

### Expected Output

```
✓ All verification checks PASSED!
  - All agents are positioned on circle with 40% radius
  - All agents are pointing inward (toward center)
  - Agents are evenly distributed around the circle
```

## Integration with Testbench

### Required RTL Signals

The initialization function assumes these debug signals are available:

```systemverilog
input  [9:0]  debug_agent_idx,        // Which agent to access (0-999)
input  [1:0]  debug_agent_sel,        // Which field: 0=x, 1=y, 2=angle
input  [24:0] debug_agent_data_write, // Data to write
input         debug_agent_write_en,   // Write enable
```

### Example Integration

```cpp
#include "Vslime_top.h"
#include "agent_init_data.h"

int main() {
    Vslime_top* dut = new Vslime_top;

    // Reset
    dut->btnr = 1;
    for (int i = 0; i < 20; i++) {
        dut->clk_100mhz = 0; dut->eval();
        dut->clk_100mhz = 1; dut->eval();
    }
    dut->btnr = 0;

    // Initialize agents with pre-computed data
    initialize_agents_from_precomputed();

    // Run simulation...

    delete dut;
    return 0;
}
```

## Advantages of Pre-Computation

1. **Compilation Safety:** No complex C++ math during compilation
2. **Bit-Exact Values:** Uses Python reference implementation (guarantees correctness)
3. **Fast Initialization:** No runtime computation needed
4. **Easy Verification:** Python script validates all generated values
5. **Reproducibility:** Same initialization every time (no random variation)

## Regenerating Data

To regenerate initialization data (e.g., after changing parameters):

```bash
# Step 1: Generate new data
python3 generate_cpp_agent_init.py --num-agents 500 --width 640 --height 480

# Step 2: Verify correctness
python3 verify_agent_init.py

# Step 3: Rebuild testbench
cd obj_dir
make -f Vslime_top.mk
```

## Troubleshooting

### "No module named 'numpy'"

Make sure the Python virtual environment is activated:

```bash
source /home/reson/SlimeSimulator/.venv/bin/activate
```

### "No module named 'slime_simulator'"

The script automatically adds the correct path. If this fails, ensure you're running from `rtl/sim/`:

```bash
cd /home/reson/SlimeSimulator/rtl/sim
python3 generate_cpp_agent_init.py
```

### Initialization function not found

Ensure you've included the header:

```cpp
#include "agent_init_data.h"
```

And that the header file exists in the same directory as your testbench.

### Wrong number of agents initialized

Check that `NUM_AGENTS` in your testbench matches `NUM_INIT_AGENTS` from the header:

```cpp
const int NUM_AGENTS = 100;  // Must match agent_init_data.h
```

## Related Files

- `/home/reson/SlimeSimulator/slime_simulator.py` - Python reference implementation
- `/home/reson/SlimeSimulator/rtl/sim/python_reference.py` - RTL comparison reference
- `/home/reson/SlimeSimulator/rtl/sim/agent_init_validator_tb.cpp` - RTL validation testbench

## See Also

- `CLAUDE.md` - Project documentation
- `python_agent_validation.json` - Python reference agent validation output
- `rtl_agent_validation.json` - RTL agent validation output (from testbench)
