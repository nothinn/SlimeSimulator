# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**SlimeSimulator** is an FPGA-based real-time simulation of slime mold (Physarum) behavior running on a Basys3 board. The project combines a bit-exact Python reference implementation with a SystemVerilog hardware design that processes 1000 agents in parallel, producing 320×240 trail maps upscaled to 640×480 VGA output.

**Key Architecture:** Pipelined agent processor (19 stages) → Trail map memory → VGA controller → Basys3 output (VGA + LED/button I/O)

## Essential Build & Test Commands

### Python Reference Model
```bash
# Run full simulation (100 agents, 100 steps)
python slime_simulator.py

# With real-time display (requires pygame)
python slime_simulator.py --display

# Generate reference trail data for validation
python rtl/sim/python_reference.py --steps 100 -o reference.bin
```

### RTL Simulation & Testing
```bash
cd rtl/sim
source ../../.venv/bin/activate  # Activate cocotb environment

make test_all           # Run all module tests (14 tests)
make test_comparison    # RTL vs Python comparison tests (4 tests)
make test_lfsr         # Individual module tests
make test_trig_lut
make test_vga
```

### FPGA Build (Vivado)
```bash
cd rtl
source ~/2025.2/Vivado/.settings64-Vivado.sh

# Build main design (synthesis + implementation + bitstream)
vivado -mode batch -source build_vivado.tcl

# Quick VGA test pattern build (for verification)
vivado -mode batch -source scripts/build_test_pattern.tcl

# Open GUI for interactive development
vivado -mode batch -source create_project.tcl
vivado vivado_project/slime_simulator.xpr
```

### FPGA Programming
```bash
cd rtl
vivado -mode batch -source program_fpga.tcl \
  -tclargs vivado_project/slime_simulator.runs/impl_1/slime_top.bit
```

### Debug & Image Capture (Debug Build Only)
```bash
# Capture trail map from FPGA via JTAG-to-AXI
python rtl/scripts/download_image.py -o fpga_capture.png

# Compare with Python reference
python rtl/scripts/download_image.py --compare reference.bin
```

## High-Level Architecture

### Component Organization
```
slime_top.sv (Top Module)
├─ Control Layer
│  ├─ button_debouncer.sv (5 buttons: start/stop, speed±, randomize, reset)
│  └─ LED status indicators (speed level, run state, LFSR state)
│
├─ Simulation Core
│  ├─ agent_processor.sv (19-stage pipeline for 1000 agents)
│  │  ├─ Stages 1-3:    Forward sensor calculation (trig lookup)
│  │  ├─ Stages 4-5:    Forward trail read
│  │  ├─ Stages 6-8:    Left sensor calculation
│  │  ├─ Stages 9-10:   Left trail read
│  │  ├─ Stages 11-13:  Right sensor calculation
│  │  ├─ Stages 14-15:  Right trail read
│  │  ├─ Stage 16:      Decision logic (compare F/L/R)
│  │  ├─ Stage 17:      Angle update
│  │  ├─ Stage 18:      Position calculation
│  │  └─ Stage 19:      Agent write + trail deposit
│  │
│  ├─ lfsr.sv (32-bit maximal-length LFSR, deterministic RNG)
│  ├─ fixed_point_mult.sv (Q12.12 signed multiplier)
│  └─ trig_lut.sv (1024-entry sin/cos ROM, 10-bit addressing)
│
├─ Memory System
│  ├─ Trail Map (320×240 × 8-bit = 76.8 KB)
│  └─ Agent Array (1000 × 75-bit = 75 KB, ~49 BRAM blocks)
│
├─ Output Layer
│  ├─ vga_controller.sv (640×480@60Hz, 2x upscale from simulation)
│  └─ debug_wrapper.sv (JTAG-to-AXI for memory access in debug build)
│
└─ Support Modules
   └─ vga_test_pattern.sv (8 diagnostic VGA patterns for validation)
```

### Data Flow
1. **Simulation Phase:** agent_processor continuously cycles through 1000 agents
2. **Sensing:** LFSR generates random values; trig_lut provides sensor angles; trail map is read at F/L/R positions
3. **Decision:** Agent rotates based on sensory comparison (forward > left/right, etc.)
4. **Motor:** Agent position updated; trail deposited at new location
5. **Display:** VGA controller reads trail map at 60 FPS and outputs 640×480 display

### Fixed-Point Arithmetic (Q12.12 Format)
- **Total:** 25 bits (12 integer + 12 fractional + 1 sign)
- **Range:** -2048.0 to +2047.9998
- **Precision:** 1/4096 ≈ 0.000244
- **Multiplication:** (a × b) >> 12, with 50-bit intermediate result
- Critical for position/angle calculations to match Python exactly

## Key Design Parameters

| Parameter | Value | Location | Adjustable |
|-----------|-------|----------|------------|
| Resolution | 320×240 | `slime_top.sv` | Yes (affects BRAM) |
| VGA Output | 640×480 @ 60Hz | `vga_controller.sv` | Hardcoded |
| Agent Count | 1000 | `slime_top.sv` | Yes (~5000 max) |
| Move Speed | 1.0 px/step | `agent_processor.sv` | Yes |
| Turn Speed | 0.3 rad/turn | `agent_processor.sv` | Yes |
| Sensor Angle | 0.5 rad (~30°) | `agent_processor.sv` | Yes |
| Sensor Distance | 9.0 pixels | `agent_processor.sv` | Yes |
| Trail Deposit | 5 units | `agent_processor.sv` | Yes |
| Decay Rate | 0.95 | NOT IMPLEMENTED | Future |

## Testing Strategy

### Verification Approach: Bit-Exact Python Reference
The Python reference (`slime_simulator.py` and `rtl/sim/python_reference.py`) uses identical arithmetic to RTL:
- **LFSR:** Same tap sequences and state machine
- **Fixed-Point:** Exact Q12.12 multiplication with saturation
- **Trig:** Pre-computed 1024-entry lookup tables (sin/cos)

### Test Levels
1. **Component Tests** (sim/test_*.py): LFSR, fixed_point, trig_lut, vga_controller
2. **Comparison Tests** (sim/test_rtl_vs_python.py): Component-level RTL vs Python
3. **Integration Tests** (sim/test_trail_map.py): Full agent processor pipeline (WIP)

### Current Status
- ✅ 14/14 component tests passing
- ✅ 4/4 comparison tests passing
- ⏳ Full integration testing in progress (Icarus Verilog limitations)

### Known Testing Limitations
- **Icarus Verilog:** Insufficient for agent_processor integration (use Vivado or Verilator)
- **Trail Diffusion:** Not yet implemented (decay kernel TODO)

## File Organization

### Source Code Structure
```
rtl/src/
├── slime_top.sv              # Top module (400 LOC)
├── agent_processor.sv        # Agent pipeline (350 LOC)
├── lfsr.sv                   # Random number generator (80 LOC)
├── fixed_point_mult.sv       # Q12.12 multiplier (50 LOC)
├── trig_lut.sv              # 1024-entry sin/cos ROM (40 LOC)
├── vga_controller.sv        # 640×480 timing + framebuffer (100 LOC)
├── debouncer.sv             # 20ms button debouncer (50 LOC)
├── debug_wrapper.sv         # JTAG-to-AXI bridge (100 LOC)
├── vga_test_pattern.sv      # 8 diagnostic patterns (150 LOC)
├── sin_lut.hex              # Generated sin table
└── cos_lut.hex              # Generated cos table
```

### Simulation & Testing
```
rtl/sim/
├── Makefile                 # Test automation
├── python_reference.py      # Bit-exact Python implementation
├── test_lfsr.py            # LFSR cocotb tests
├── test_fixed_point.py     # Fixed-point arithmetic tests
├── test_trig_lut.py        # Trig table verification
├── test_vga.py             # VGA timing tests
├── test_rtl_vs_python.py   # Cross-validation tests
└── test_trail_map.py       # Full integration (WIP)
```

### Build & Configuration
```
rtl/
├── build_vivado.tcl            # Main synthesis + implementation
├── scripts/
│   ├── build_test_pattern.tcl  # Quick VGA test build
│   ├── build_debug.tcl         # Debug build with ILA/VIO
│   ├── create_debug_ip.tcl     # Generate Xilinx IPs
│   └── download_image.py       # JTAG capture utility
├── constraints/
│   └── basys3.xdc              # Pin assignments + timing
├── vivado_project*/            # Build output directories
└── *.tcl                        # Various helper scripts
```

### Python Reference
```
├── slime_simulator.py           # Full standalone simulator (850 LOC)
└── rtl/sim/python_reference.py  # Verification model
```

## Control Interface (Basys3)

### Buttons
| Button | Function | Effect |
|--------|----------|--------|
| BTNC | Start/Stop | Toggle simulation run state |
| BTNU | Speed Up | Increase frame rate (0-15) |
| BTND | Speed Down | Decrease frame rate (0-15) |
| BTNL | Randomize | New LFSR seed |
| BTNR | Reset | Hardware reset (configured in .xdc) |

### Switches
| Switch | Effect |
|--------|--------|
| SW[0] | Pause (freeze agents, keep VGA running) |
| SW[2:0] | VGA test pattern select (test pattern build only) |

### LED Indicators
| LEDs | Meaning |
|------|---------|
| LED[3:0] | Current speed level (0-15) |
| LED[4] | Simulation running |
| LED[5] | Paused state |
| LED[6] | Debug freeze (debug build only) |
| LED[7] | State machine indicator |
| LED[15:8] | LFSR state (lower 8 bits) |

## Resource Utilization (Basys3 Artix-7, 320×240 + 1000 agents)

| Resource | Used | Available | Utilization |
|----------|------|-----------|------------|
| LUTs | ~3,300 | 20,800 | 16% |
| Flip-Flops | ~3,000 | 41,600 | 7% |
| BRAM (18Kb) | 49 | 100 | 49% |
| DSP48 | 4 | 90 | 4% |

**Status:** Design fits comfortably. Room for increased resolution or agent count. External SRAM needed for 640×480 trail map.

## Common Development Tasks

### Adding a New Parameter
1. Add parameter to `slime_top.sv` as localparam
2. Update Python reference in `slime_simulator.py`
3. Add test cases in `rtl/sim/test_*.py`
4. Rebuild with `vivado -mode batch -source build_vivado.tcl`

### Fixing a Component Bug
1. Write failing test case in `rtl/sim/test_*.py`
2. Debug with cocotb: `cd rtl/sim && make test_<module>`
3. Validate Python reference matches expected behavior
4. Run full comparison suite: `make test_comparison`

### Modifying Agent Decision Logic
1. Update sensory comparison in `agent_processor.sv` (stage 16)
2. Update corresponding logic in `python_reference.py`
3. Run full integration test: `cd rtl/sim && make test_trail_map`

### Changing VGA Resolution or Timing
1. Modify `vga_controller.sv` timing parameters
2. Update `slime_top.sv` resolution constants
3. Adjust memory sizes if needed (trail map is resolution²)
4. Update test cases in `test_vga.py`

## Current Project Status

**Branch:** `feature/python-simulator`

**Completed:**
- ✅ Python reference simulator with bit-exact arithmetic
- ✅ All core RTL modules verified (LFSR, fixed-point, trig, VGA)
- ✅ 14/14 component tests passing
- ✅ Cocotb test infrastructure
- ✅ Vivado build flow validated
- ✅ Pin constraints for Basys3

**In Progress:**
- ⏳ Full end-to-end FPGA testing
- ⏳ Trail diffusion/decay kernel implementation

**Not Yet Implemented:**
- 🔲 Trail decay/diffusion (blur effect)
- 🔲 Full integration test on hardware
- 🔲 UART parameter update interface

## Python Virtual Environment

The project uses a Python venv for cocotb and dependencies:

```bash
# Activate
source .venv/bin/activate

# Deactivate
deactivate

# Installed packages
cocotb==2.0.1
numpy==2.3.5
pillow==12.0.0
scipy==1.16.3
pygame (optional, for --display mode)
```

## Environment Variables & Setup

```bash
# Vivado environment (required for builds)
source ~/2025.2/Vivado/.settings64-Vivado.sh

# Python environment (required for tests)
source .venv/bin/activate
```

## Typical Development Workflow

1. **Make changes** to Python reference or RTL module
2. **Run relevant tests:** `cd rtl/sim && make test_<module>`
3. **Validate against Python:** `make test_comparison`
4. **Build RTL** (if changes affect synthesis): `vivado -mode batch -source build_vivado.tcl`
5. **Program FPGA** (if testing on hardware): `vivado -mode batch -source program_fpga.tcl ...`
6. **Verify output** via VGA display or captured image

## Performance Expectations

- **Python simulation:** ~30 seconds for 100,000 agents × 100 steps
- **RTL throughput:** 1 agent every ~19 clock cycles @ 100 MHz → ~5.26M agents/sec
- **Expected frame rate:** ~60 FPS with 1000 agents on Basys3
- **Agent processing bandwidth:** ~19 MHz for 1000 agents @ 60 FPS

## Quick Debugging Tips

### Verify LFSR Sequence
```bash
python -c "from rtl.sim.python_reference import LFSR; l=LFSR(0x1234); print([l.next() for _ in range(10)])"
```

### Check Fixed-Point Precision
```bash
python -c "from rtl.sim.python_reference import FixedPoint; print(FixedPoint(1.0) * FixedPoint(3.14))"
```

### Validate Trig Tables
```bash
cd rtl/sim
python -c "from python_reference import TrigLUT; t=TrigLUT(); print(f'sin(π/4) = {t.sin(256)}')"
```

### Monitor VGA Timing (from Vivado simulation)
Run `make test_vga` to verify hsync/vsync signals match 640×480@60Hz specification.

## Key References

- **Sebastian Lague Video:** https://www.youtube.com/watch?v=X-iSQQgOd1A
- **Academic Paper:** https://uwe-repository.worktribe.com/output/980579
- **Basys3 Reference Manual:** Pin assignments documented in `constraints/basys3.xdc`
- **Vivado IP Cores:** Debug IPs (ILA, VIO) available in `scripts/create_debug_ip.tcl`

## Important Notes

- **Decay not implemented:** Trail map doesn't currently decay. Future enhancement required.
- **Memory-limited resolution:** Limited to ~320×240 by BRAM on Basys3. Use external SRAM for higher resolution.
- **Icarus Verilog limitations:** Full integration tests require Vivado or Verilator; Icarus insufficient for agent_processor.
- **Deterministic simulation:** LFSR provides repeatable (not random) behavior. Seed from button input for variation.
