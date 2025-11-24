# Slime Simulator RTL Implementation

Hardware implementation of physarum slime mold simulation for Basys3 FPGA.

## Quick Start

### 1. Build VGA Test Pattern (Verify Board)
```bash
source ~/2025.2/Vivado/.settings64-Vivado.sh
cd rtl
vivado -mode batch -source scripts/build_test_pattern.tcl
```

**Programming:**
```bash
vivado -mode batch -source program_fpga.tcl -tclargs vivado_project_test/vga_test.runs/impl_1/vga_test_top.bit
```

**Test Patterns:** Use SW[2:0] to select:
- 0: Color bars - Verify RGB channels
- 1: Gradient - Check uniformity
- 2: Checkerboard - Verify pixel clock
- 3: Border test - Check timing boundaries
- 4: Grid - Verify resolution
- 5: RGB bars - Individual color channels
- 6: Crosshatch - Check geometry
- 7: Pixel test - Maximum resolution

### 2. Build Main Slime Simulator
```bash
vivado -mode batch -source build_vivado.tcl
```

**Configuration:**
- Resolution: 320x240 (2x upscaled to VGA 640x480)
- Agents: 1000 (configurable up to ~5000)
- Memory: ~45% BRAM utilization

### 3. Build Debug Version (with Image Capture)
```bash
vivado -mode batch -source scripts/build_debug.tcl
```

Includes:
- ILA for waveform capture
- VIO for manual control
- JTAG-to-AXI for trail map download

## Button Controls

| Button | Function |
|--------|----------|
| **BTNC** | Start/Stop simulation |
| **BTNU/BTND** | Speed up/down |
| **BTNL** | Randomize seed |
| **BTNR** | Hardware reset |
| **SW[0]** | Pause |

## LED Status

| LED | Meaning |
|-----|---------|
| LED[3:0] | Speed level (0-15) |
| LED[4] | Simulation running |
| LED[5] | Paused |
| LED[6] | Debug freeze (debug build only) |
| LED[7:6] | State machine status |
| LED[15:8] | LFSR state (lower byte) |

## Capturing Images (Debug Build)

### Method 1: JTAG-to-AXI (Fast)
```bash
python scripts/download_image.py -o fpga_capture.png
```

### Method 2: VIO Manual Control
```bash
python scripts/download_image.py --method vio -o capture.png
```

### Compare with Python Reference
```bash
# Generate Python reference
python sim/python_reference.py --steps 100 -o reference.bin

# Download and compare
python scripts/download_image.py --compare reference.bin
```

## Project Structure

```
rtl/
├── src/               # RTL source files
│   ├── slime_top.sv              # Main top module (320x240)
│   ├── slime_top_debug.sv        # Debug-enabled version
│   ├── vga_controller.sv         # 640x480@60Hz VGA
│   ├── vga_test_pattern.sv       # Test patterns
│   ├── agent_processor.sv        # Agent update pipeline
│   ├── lfsr.sv                   # Random number generator
│   ├── fixed_point_mult.sv       # Q12.12 multiplier
│   ├── trig_lut.sv               # Sin/cos lookup
│   ├── debouncer.sv              # Button debouncing
│   ├── debug_wrapper.sv          # JTAG memory access
│   ├── sin_lut.hex / cos_lut.hex # Trig tables
│   └── gen_trig_lut.py           # LUT generator
│
├── constraints/
│   └── basys3.xdc                # Pin constraints
│
├── scripts/
│   ├── build_debug.tcl           # Debug build
│   ├── build_test_pattern.tcl    # VGA test
│   ├── create_debug_ip.tcl       # Generate debug IPs
│   ├── create_project.tcl        # Create project for GUI
│   ├── download_image.py         # Capture from FPGA
│   └── program_fpga.tcl          # Programming script
│
├── sim/                # Cocotb testbenches
│   ├── test_lfsr.py
│   ├── test_fixed_point.py
│   ├── test_trig_lut.py
│   ├── test_vga.py
│   ├── test_rtl_vs_python.py     # Component comparison
│   ├── python_reference.py       # Reference model
│   └── Makefile
│
├── docs/
│   └── resource_estimate.md      # FPGA resource analysis
│
├── build_vivado.tcl              # Main build script
└── program_fpga.tcl              # FPGA programming
```

## Resource Utilization (320x240, 1000 agents)

| Resource | Used | Available | % |
|----------|------|-----------|---|
| LUTs | ~3,300 | 20,800 | 16% |
| Flip-Flops | ~3,000 | 41,600 | 7% |
| BRAM 18Kb | ~49 | 100 | 49% |
| DSP48 | 4 | 90 | 4% |

## Simulation Tests

All component tests pass with bit-exact matching to Python:

```bash
cd sim
source ../.venv/bin/activate

# Individual components
make test_lfsr          # LFSR sequences
make test_fixed_point   # Q12.12 arithmetic
make test_trig          # Sin/cos tables
make test_vga           # VGA timing

# Python comparison
make test_comparison    # Verify all match Python

# Results: 14/14 tests pass
```

## Design Parameters

Configurable in `slime_top.sv`:

```systemverilog
parameter NUM_AGENTS   = 1000;     // Number of agents
parameter SIM_WIDTH    = 320;      // Simulation width
parameter SIM_HEIGHT   = 240;      // Simulation height
parameter FP_INT_BITS  = 12;       // Fixed-point integer bits
parameter FP_FRAC_BITS = 12;       // Fixed-point fraction bits
```

**Memory scaling:**
- Trail map: WIDTH × HEIGHT × 8 bits
- Agents: NUM_AGENTS × 75 bits
- 320×240 with 1000 agents ≈ 614 Kb + 75 Kb = 689 Kb (fits comfortably)

## Known Limitations

1. **Diffusion not implemented** - Trail decay/blur needs to be added
2. **Resolution limited by BRAM** - Max ~400×300 for full 640×480
3. **Icarus Verilog compatibility** - Use Vivado or Verilator for full test

## Next Steps

1. ✅ Component verification (LFSR, fixed-point, trig)
2. ✅ Agent processor implementation
3. ✅ VGA output with test patterns
4. ⚠️ Trail diffusion kernel (TODO)
5. ⏳ Full end-to-end verification (in progress)

## References

- [Sebastian Lague's Video](https://www.youtube.com/watch?v=X-iSQQgOd1A)
- [Physarum Paper](https://uwe-repository.worktribe.com/output/980579)
- Python simulator: `../slime_simulator.py`
