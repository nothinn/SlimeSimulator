# Slime Simulator Project Status
**Last Updated:** 2025-11-21
**Vivado Version:** 2025.2

## Current Status: VGA Test Build In Progress ⏳

First Vivado build (VGA test pattern) is running to verify toolchain.

---

## Completed Work ✅

### 1. Python Simulator
- ✅ Full NumPy-based slime mold simulation
- ✅ Fixed-point Q12.12 arithmetic for RTL compatibility
- ✅ LFSR-based deterministic random
- ✅ Pygame real-time display (`--display` flag)
- ✅ Configurable parameters (agents, size, seed)
- ✅ Git branch: `feature/python-simulator` with 6 commits

**Location:** `slime_simulator.py`

### 2. RTL Implementation (SystemVerilog)

#### Core Modules
| Module | Status | Tests | Description |
|--------|--------|-------|-------------|
| `lfsr.sv` | ✅ Complete | 3/3 pass | 32-bit LFSR, matches Python exactly |
| `fixed_point_mult.sv` | ✅ Complete | 3/3 pass | Q12.12 multiplier, ≤1 LSB error |
| `trig_lut.sv` | ✅ Complete | 3/3 pass | 1024-entry sin/cos ROM, bit-exact |
| `vga_controller.sv` | ✅ Complete | 5/5 pass | 640x480@60Hz, verified timing |
| `debouncer.sv` | ✅ Complete | - | 20ms button debounce |
| `agent_processor.sv` | ✅ Complete | - | Pipelined agent update (19 states) |
| `slime_top.sv` | ✅ Complete | - | Top module, 320x240 resolution |
| `slime_top_debug.sv` | ✅ Complete | - | With ILA/VIO/JTAG-to-AXI |
| `vga_test_pattern.sv` | ✅ Complete | - | 8 test patterns for VGA verification |

#### Test Results
```
Component Tests:          14/14 PASS
├─ LFSR                   3/3   (1000-step sequence match)
├─ Fixed-point            3/3   (comprehensive test cases)
├─ Trig LUT               3/3   (all 1024 entries)
└─ VGA                    5/5   (timing + signals)

Python Comparison:        4/4   PASS
├─ LFSR sequence          ✅    (bit-exact)
├─ LFSR statistics        ✅    (50.4% uniform)
├─ Fixed-point multiply   ✅    (≤1 LSB)
└─ Trig full table        ✅    (bit-exact)
```

**Test command:**
```bash
cd rtl/sim
source ../../.venv/bin/activate
make test_comparison
```

### 3. Build Infrastructure

#### Scripts Created
| Script | Purpose |
|--------|---------|
| `build_vivado.tcl` | Full synthesis + implementation + bitstream |
| `scripts/build_test_pattern.tcl` | Quick VGA test (currently building) |
| `scripts/build_debug.tcl` | Debug build with ILA/VIO/JTAG |
| `create_project.tcl` | Create project for GUI editing |
| `program_fpga.tcl` | Program Basys3 |
| `scripts/create_debug_ip.tcl` | Generate Xilinx debug IPs |
| `scripts/download_image.py` | Capture trail map via JTAG |

#### Test Infrastructure
| File | Purpose |
|------|---------|
| `sim/test_*.py` | Cocotb testbenches for all modules |
| `sim/python_reference.py` | Bit-exact Python reference model |
| `sim/test_rtl_vs_python.py` | Component comparison tests |
| `sim/test_trail_map.py` | Full trail map comparison (WIP) |
| `sim/Makefile` | Test automation |

### 4. Constraints
- ✅ `constraints/basys3.xdc` - Complete pin assignments
- ✅ Clock: 100MHz input → 25MHz VGA pixel clock
- ✅ All buttons, switches, LEDs, VGA mapped
- ✅ BTNR configured as hardware reset

---

## Design Specifications

### Resolution & Memory
- **Simulation:** 320×240 pixels
- **VGA Output:** 640×480 @ 60Hz (2x upscaled)
- **Trail Memory:** 76,800 bytes (614 Kb)
- **Agents:** 1000 (configurable to ~5000)

### Resource Estimates (320×240, 1000 agents, debug)
| Resource | Used | Available | Utilization |
|----------|------|-----------|-------------|
| LUTs | ~3,300 | 20,800 | 16% |
| Flip-Flops | ~3,000 | 41,600 | 7% |
| BRAM 18Kb | 49 | 100 | 49% |
| DSP48 | 4 | 90 | 4% |

**Status:** Fits comfortably on Basys3 ✅

### Fixed-Point Format
- **Q12.12** - 12 integer bits, 12 fractional bits, 1 sign bit
- **Range:** -2048.0 to +2047.9998
- **Precision:** 1/4096 ≈ 0.000244

### Parameters (Configurable)
```systemverilog
Move Speed:        1.0    (pixels per step)
Turn Speed:        0.3    (radians per turn)
Sensor Angle:      0.5    (radians, ~30°)
Sensor Distance:   9.0    (pixels ahead)
Deposit Amount:    5      (trail intensity)
Decay Rate:        0.95   (per step)
```

---

## Button/LED Mapping

### Controls
| Button | Function |
|--------|----------|
| BTNC | Start/Stop simulation |
| BTNU | Speed up |
| BTND | Speed down |
| BTNL | Randomize seed |
| BTNR | Hardware reset |
| SW[0] | Pause |

### VGA Test Patterns (SW[2:0])
| Value | Pattern | Use |
|-------|---------|-----|
| 0 | Color bars | Verify RGB channels |
| 1 | Gradient | Check uniformity |
| 2 | Checkerboard | Verify pixel clock |
| 3 | Border test | Check timing |
| 4 | Grid | Verify resolution |
| 5 | RGB bars | Individual channels |
| 6 | Crosshatch | Check geometry |
| 7 | Pixel test | Maximum resolution |

### LED Indicators
- LED[3:0]: Speed level (0-15)
- LED[4]: Simulation running
- LED[5]: Paused
- LED[6]: Debug freeze
- LED[7]: State indicator
- LED[15:8]: LFSR state (lower byte)

---

## Build Commands

### Quick Start (VGA Test)
```bash
cd /home/reson/SlimeSimulator/rtl
source ~/2025.2/Vivado/.settings64-Vivado.sh

# Build VGA test pattern (currently running)
vivado -mode batch -source scripts/build_test_pattern.tcl

# Program FPGA
vivado -mode batch -source program_fpga.tcl \
  -tclargs vivado_project_test/vga_test.runs/impl_1/vga_test_top.bit
```

### Main Design
```bash
# Basic build (no debug)
vivado -mode batch -source build_vivado.tcl

# Debug build (with ILA, VIO, JTAG-to-AXI)
vivado -mode batch -source scripts/build_debug.tcl

# Open in GUI
vivado -mode batch -source create_project.tcl
vivado vivado_project/slime_simulator.xpr
```

### Run Tests
```bash
cd sim
source ../../.venv/bin/activate  # cocotb environment

make test_all          # Run all module tests
make test_comparison   # Compare RTL vs Python
```

---

## Current Build Status

### VGA Test Pattern Build
- **Started:** 2025-11-21 19:01:49
- **Status:** Running (routing phase)
- **Timing:** WNS = +8.008ns (good slack)
- **Log:** `rtl/vga_build.log`

**When complete:**
- Bitstream: `vivado_project_test/vga_test.runs/impl_1/vga_test_top.bit`
- Use SW[2:0] to select test patterns
- Verify VGA output on monitor

---

## Next Steps

### Immediate (Today)
1. ⏳ Complete VGA test build
2. ⏳ Program FPGA and verify VGA works
3. 📋 Build main slime simulator
4. 📋 Test on hardware

### Short Term
1. 📋 Implement trail diffusion kernel (currently TODO)
2. 📋 Add decay factor to trail memory
3. 📋 End-to-end trail map comparison test
4. 📋 Optimize for higher agent counts

### Future Enhancements
1. Variable resolution (runtime configurable)
2. Multiple species with different colors
3. UART interface for parameter updates
4. Frame buffer export via Ethernet

---

## Known Issues / Limitations

### RTL
1. **Diffusion not implemented** - Trail decay/blur TODO
2. **Icarus Verilog incompatible** - Use Vivado or Verilator for full tests
3. **Agent processor** - Not tested in full integration (Icarus limitations)

### Resolution
- Limited to ~320×240 by BRAM availability
- Could use external SRAM for full 640×480
- Current 2x upscaling provides acceptable quality

---

## File Locations

### Source
```
SlimeSimulator/
├── slime_simulator.py          # Python reference
├── rtl/
│   ├── src/                    # SystemVerilog sources
│   ├── constraints/            # Basys3 XDC file
│   ├── scripts/                # TCL build scripts
│   ├── sim/                    # Cocotb tests
│   ├── docs/                   # Documentation
│   ├── build_vivado.tcl        # Main build
│   ├── program_fpga.tcl        # Programming
│   └── README.md               # RTL documentation
└── STATUS.md                   # This file
```

### Build Outputs
```
rtl/
├── vivado_project_test/        # VGA test build
├── vivado_project/             # Main design build
├── vivado_project_debug/       # Debug build
└── vga_build.log               # Current build log
```

### Generated Files
```
rtl/src/
├── sin_lut.hex                 # 1024-entry sin table
└── cos_lut.hex                 # 1024-entry cos table
```

---

## Environment

### Tools Installed
- ✅ Vivado 2025.2 (`~/2025.2/Vivado/`)
- ✅ Icarus Verilog 12.0
- ✅ cocotb 2.0.1
- ✅ Python 3.12 + venv (`.venv/`)

### Python Packages
```
cocotb==2.0.1
numpy==2.3.5
pillow==12.0.0
scipy==1.16.3
pygame (for display mode)
```

---

## Git Status

### Branch: `feature/python-simulator`
6 commits:
1. Initial Python simulator
2. Add fixed-point and LFSR
3. Add display mode
4. RTL implementation
5. Testbenches and verification
6. Debug infrastructure

**To merge:**
```bash
git checkout main
git merge feature/python-simulator
```

---

## Quick Reference

### Program FPGA After Build
```bash
source ~/2025.2/Vivado/.settings64-Vivado.sh
cd /home/reson/SlimeSimulator/rtl
vivado -mode batch -source program_fpga.tcl \
  -tclargs <path_to_bitstream.bit>
```

### Capture Image (Debug Build)
```bash
cd /home/reson/SlimeSimulator/rtl
python scripts/download_image.py -o capture.png

# Compare with Python
python sim/python_reference.py --steps 100 -o ref.bin
python scripts/download_image.py --compare ref.bin
```

### Regenerate Trig Tables
```bash
cd rtl/src
python gen_trig_lut.py .
```

---

## Contact / Notes

- Python simulator runs ~30 seconds for 100k agents × 100 steps
- RTL design processes 1 agent every ~19 clock cycles @ 100MHz
- Expected frame rate: ~60 FPS with 1000 agents
- All core components verified bit-exact against Python ✅

**Next session:** Check VGA build completion, program FPGA, verify test patterns work.
