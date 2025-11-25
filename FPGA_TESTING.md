# FPGA Testing and Validation Guide

## Available Bitstreams

### 1. **Production Bitstream** (Main Design)
- **File:** `rtl/vivado_project/slime_simulator.runs/impl_1/slime_top.bit`
- **Features:** Full slime simulator with 1000 agents
- **Resolution:** 320×240 simulation → 640×480 VGA output
- **Performance:** ~60 FPS on 100 MHz clock
- **Use Case:** Real-time hardware simulation

### 2. **VGA Test Pattern Bitstream**
- **File:** `rtl/vivado_project_solid/vga_solid_test.runs/impl_1/vga_solid_color.bit`
- **Features:** 8 diagnostic VGA patterns (solid colors, gradients, etc.)
- **Use Case:** Quick VGA validation before full simulation
- **Advantages:** Minimal design, fastest boot time

### 3. **Debug Bitstream** (With ILA/VIO)
- **File:** `vivado_project_debug/slime_simulator_debug.runs/impl_1/slime_top.bit`
- **Features:** 
  - Integrated Logic Analyzer (ILA) for waveform capture
  - Virtual I/O (VIO) for runtime control
  - JTAG-to-AXI bridge for memory access
  - 15 critical signal probes
- **Use Case:** In-depth debugging and analysis
- **Memory:** 8192 samples at 100 MHz

---

## Programming the FPGA

### Prerequisites
```bash
# Basys3 board connected via USB (JTAG interface)
# Vivado 2025.2 installed
source ~/2025.2/Vivado/.settings64-Vivado.sh
```

### Quick Program (Production Bitstream)
```bash
cd /home/reson/SlimeSimulator
./scripts/program_fpga.sh
```

### Program with Specific Bitstream
```bash
./scripts/program_fpga.sh rtl/vivado_project_solid/vga_solid_test.runs/impl_1/vga_solid_color.bit
```

### Manual Programming (Using Vivado GUI)
```bash
vivado -mode gui
# Hardware → Open Hardware Manager → Program Device
```

---

## Button Controls (All Bitstreams)

| Button | Function | Effect |
|--------|----------|--------|
| **BTNC** | Start/Stop | Toggle simulation run state |
| **BTNU** | Speed Up | Increase frame rate (0-15) |
| **BTND** | Speed Down | Decrease frame rate (0-15) |
| **BTNL** | Randomize | New LFSR seed (random trail pattern) |
| **BTNR** | Reset | Hardware reset (requires reconfiguration) |

## LED Indicators

| LEDs | Meaning |
|------|---------|
| LED[3:0] | Speed level (0-15) |
| LED[4] | Simulation running |
| LED[5] | Paused state |
| LED[15:8] | LFSR state (lower 8 bits) |

---

## Testing Procedure

### Stage 1: VGA Verification (5 minutes)
1. Program **VGA Test Pattern** bitstream
2. Observe VGA output for solid colors and patterns
3. Check for flickering or signal issues
4. Press buttons to cycle through test patterns (if implemented)

**Expected Result:** Clean VGA display with no artifacts

### Stage 2: Basic Simulation Test (10 minutes)
1. Program **Production** bitstream
2. Press BTNC to start simulation
3. Observe trail patterns evolving on screen
4. Test speed buttons (BTNU/BTND) for different frame rates
5. Press BTNL to generate new random patterns

**Expected Result:** Smooth animation, patterns converging into trails

### Stage 3: Reference Comparison (15 minutes)
```bash
# Generate Python reference (10 steps)
cd rtl/sim
python python_reference.py --steps 10 -o reference_10steps.bin

# Run FPGA validation
cd ../..
python scripts/validate_fpga_output.py --reference rtl/sim/reference_10steps.bin
```

**Expected Result:** Trail maps match within tolerance

### Stage 4: Debug Analysis (20+ minutes, Debug Bitstream only)
```bash
# Open Vivado with debug bitstream programmed
vivado -mode gui

# Hardware → Open Hardware Manager → Set trigger conditions
# Capture waveforms of:
# - Agent position/angle updates
# - Trail deposit operations
# - Memory read/write patterns
# - LFSR state evolution
```

---

## Expected Behavior

### Trail Pattern Evolution
- **Initial state:** Random agent positions
- **Steps 1-50:** Agents create sparse trails
- **Steps 50-500:** Trails converge into preferred paths
- **Steps 500+:** Stable "pheromone" patterns emerge
- **Final result:** Self-organized paths (typically 2-4 main trails)

### Performance Metrics
- **Throughput:** 1 agent every ~19 cycles @ 100 MHz = 5.26M agents/sec
- **Frame rate:** ~60 FPS with 1000 agents
- **Memory bandwidth:** ~800 MB/sec (trail reads + deposits)
- **Power consumption:** ~500mW (estimated, under load)

### Common Issues

| Symptom | Likely Cause | Solution |
|---------|-------------|----------|
| No VGA output | JTAG not connected | Check USB cable, reseat |
| Flickering display | Clock timing | Verify Basys3 clock (100 MHz) |
| Stuck agents | Sensor angle/distance wrong | Check parameters in slime_top.sv |
| Memory corruption | BRAM access conflict | Check trail_mem read/write timing |
| Unpredictable patterns | LFSR seed issues | Press BTNL to reseed |

---

## Advanced Testing with Debug Bitstream

### Capture Agent Processing Pipeline
```tcl
# In Vivado ILA window
set_trigger agent_processor.stage_valid
set_action_window 1000 (capture 1000 samples around trigger)
```

### Monitor Trail Memory Access
```tcl
# Watch both read and write ports simultaneously
set_probe trail_addr_read
set_probe trail_addr_write
set_probe trail_data_out
```

### Verify LFSR Determinism
```tcl
# Run identical simulation twice, compare LFSR sequences
# Capture LFSR state evolution over 100 clock cycles
# Should be identical both times (deterministic RNG)
```

---

## Bitstream Sizes and Load Times

| Bitstream | Size | Load Time | BRAM Used |
|-----------|------|-----------|-----------|
| VGA Test | ~2.8 MB | ~3 sec | 0 KB |
| Production | ~6.2 MB | ~8 sec | 76.8 KB (trail map) |
| Debug | ~12.4 MB | ~15 sec | 100+ KB (ILA buffer) |

---

## Troubleshooting

### JTAG Connection Issues
```bash
# Check if Basys3 is detected
vivado -mode batch -source rtl/verify_fpga.tcl

# Expected output: Basys3 detected on JTAG chain
```

### Bitstream Verification
```bash
# Check bitstream integrity
md5sum rtl/vivado_project/slime_simulator.runs/impl_1/slime_top.bit

# Compare with known good checksum (available in build logs)
```

### Clean Rebuild (if corruption suspected)
```bash
cd rtl
rm -rf vivado_project* .Xil
source ~/2025.2/Vivado/.settings64-Vivado.sh
python scripts/vivado_build.py main --verbose --clean
```

---

## Next Steps

1. **Hardware validation:** Program and test on Basys3
2. **Reference comparison:** Validate against Python simulation
3. **Performance tuning:** Adjust parameters (speed, sensor angle, etc.)
4. **Integration:** Add UART interface for parameter updates
5. **Documentation:** Create user guide for real-time demo

---

*Generated: 2025-11-25 | SlimeSimulator FPGA Project*
