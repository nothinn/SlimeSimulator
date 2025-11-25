# Slime Simulator FPGA Debug Infrastructure - Quick Start Guide

This guide will help you quickly set up and use the JTAG2AXI and VIO IP cores for FPGA memory readout and regression testing.

## Overview

The debug infrastructure enables:
- **JTAG-to-AXI Master**: Read trail memory from FPGA via JTAG (no soft processor needed)
- **VIO (Virtual I/O)**: Monitor and control signals interactively from Vivado
- **ILA (Integrated Logic Analyzer)**: Capture internal signal waveforms

## Prerequisites

- Xilinx Vivado 2023.x or later
- Basys3 FPGA board with USB-JTAG cable
- Python 3.8+ with NumPy and PIL

## Quick Start - 5 Minute Setup

### 1. Add IP Cores to Project (First Time Only)

```bash
cd /home/reson/SlimeSimulator/rtl
vivado -mode batch -source add_ip_cores.tcl
```

This creates three IP cores:
- `debug_jtag_axi` - JTAG-to-AXI Master
- `debug_vio` - Virtual I/O
- `debug_ila` - Integrated Logic Analyzer

**Duration**: ~2-3 minutes

### 2. Build Debug Bitstream

```bash
vivado -mode batch -source rebuild_with_ips.tcl
```

This performs:
- Synthesis
- Implementation
- Bitstream generation

**Duration**: ~10-15 minutes on typical machine

**Output**: `vivado_project_debug/slime_simulator_debug.runs/impl_1/slime_top_debug.bit`

### 3. Program FPGA

```bash
vivado -mode batch -source program_debug_fpga.tcl
```

**Duration**: ~30 seconds

### 4. Verify Connection

The programming script will report detected debug cores:
```
✓ JTAG-to-AXI detected: 1 core(s)
✓ VIO detected: 1 core(s)
✓ ILA detected: 1 core(s)
```

### 5. Start Simulation

Press **BTNC** (center button) on the Basys3 board to start the simulation.

LEDs will indicate:
- LED[3:0]: Speed level
- LED[4]: Simulation running
- LED[5]: Simulation paused (SW[0])
- LED[7:0]: LFSR state

## Usage Scenarios

### Scenario A: Interactive Debugging with Vivado GUI

1. **Open Vivado**:
   ```bash
   vivado -mode gui
   ```

2. **Open Hardware Manager**:
   - Tools → Hardware Manager
   - Auto Connect (click green bar)

3. **Monitor with VIO**:
   - Window → Dashboard
   - Find `hw_vio_1` widget
   - **Monitor** (Input Probes):
     - `probe_in0`: capture_done
     - `probe_in1`: frame_count (increments at 60 Hz)
     - `probe_in2`: trail_data (value at read_addr)
   - **Control** (Output Probes):
     - `probe_out1`: Set to 1 to freeze simulation
     - `probe_out3`: Memory address to read (0-307199)

4. **Capture Waveforms with ILA**:
   - Window → Hardware
   - Select `hw_ila_1`
   - Configure trigger (e.g., sim_state == 4'h2)
   - Click Run Trigger
   - View waveforms after trigger

### Scenario B: Reading Memory via TCL Console

In Vivado Hardware Manager TCL console:

```tcl
# Get JTAG-to-AXI interface
set jtag_axi [get_hw_axis hw_axi_1]

# Read frame count register
create_hw_axi_txn read_frame_txn $jtag_axi \
    -address 0x00100008 -len 1 -type read
run_hw_axi read_frame_txn
set frame_count [get_property DATA [get_hw_axi_txn read_frame_txn]]
puts "Frame count: $frame_count"

# Freeze simulation
create_hw_axi_txn freeze_txn $jtag_axi \
    -address 0x00100000 -data 00000001 -type write
run_hw_axi freeze_txn

# Read first 1024 bytes of trail memory
create_hw_axi_txn read_mem_txn $jtag_axi \
    -address 0x00000000 -len 256 -type read
run_hw_axi read_mem_txn
set mem_data [get_property DATA [get_hw_axi_txn read_mem_txn]]
puts "Memory data: $mem_data"

# Resume simulation
create_hw_axi_txn resume_txn $jtag_axi \
    -address 0x00100000 -data 00000000 -type write
run_hw_axi resume_txn
```

### Scenario C: Python Automated Frame Capture

**Note**: The Python fpga_controller.py needs JTAG-to-AXI implementation completed. Current version is a framework.

```python
from fpga_controller import SlimeFPGAController

# Connect to FPGA
fpga = SlimeFPGAController(verbose=True)

# Get dimensions
width, height = fpga.get_dimensions()
print(f"Trail map: {width}x{height}")

# Capture frame
frame = fpga.capture_frame()

# Save to PNG
fpga.save_frame(frame, "fpga_capture.png")

# Compare with Python simulator
python_frame = load_reference_frame()
metrics = fpga.compare_frames(frame, python_frame)
print(f"Max error: {metrics['max_error']}")
```

## Memory Map Reference

### Trail Memory
- **Address**: 0x0000_0000 - 0x0004_AFFF
- **Size**: 307200 bytes (640 × 480)
- **Format**: 8-bit grayscale per pixel
- **Layout**: Row-major (addr = y × 640 + x)

### Control/Status Registers
| Address      | Name        | Access | Description                    |
|--------------|-------------|--------|--------------------------------|
| 0x0010_0000  | CONTROL     | R/W    | bit[0]: freeze_sim             |
| 0x0010_0004  | STATUS      | R      | bit[0]: triggered, bit[1]: done|
| 0x0010_0008  | FRAME_COUNT | R      | 32-bit frame counter (~60 Hz)  |
| 0x0010_000C  | WIDTH       | R      | Trail map width (640)          |
| 0x0010_0010  | HEIGHT      | R      | Trail map height (480)         |

**Full memory map**: See `register_map.txt`

## VIO Probes Reference

### Input Probes (Design → Host)
| Probe    | Width | Signal       | Description                |
|----------|-------|--------------|----------------------------|
| probe_in0| 1-bit | capture_done | Capture completed at frame |
| probe_in1| 32-bit| frame_count  | VGA frame counter          |
| probe_in2| 8-bit | trail_data   | Memory value at read_addr  |

### Output Probes (Host → Design)
| Probe     | Width | Signal          | Description                   |
|-----------|-------|-----------------|-------------------------------|
| probe_out0| 1-bit | capture_trigger | Trigger capture sequence      |
| probe_out1| 1-bit | sim_freeze      | Freeze simulation             |
| probe_out2| 1-bit | read_enable     | Enable VIO memory reads       |
| probe_out3| 19-bit| read_addr       | Memory address (0-307199)     |

## ILA Probes Reference

| Probe  | Width | Signal      | Description                |
|--------|-------|-------------|----------------------------|
| probe0 | 4-bit | sim_state   | FSM state (0=IDLE, 2=RUN)  |
| probe1 | 10-bit| agent_idx   | Current agent index        |
| probe2 | 32-bit| lfsr_state  | Random number state        |
| probe3 | 8-bit | trail_data  | Trail memory data          |
| probe4 | 10-bit| pixel_x     | VGA X coordinate           |
| probe5 | 9-bit | pixel_y     | VGA Y coordinate           |
| probe6 | 1-bit | frame_start | Frame start pulse          |
| probe7 | 1-bit | sim_running | Simulation active          |

**Capture Depth**: 4096 samples @ 100 MHz

## Common Operations

### Freeze Simulation for Coherent Capture

**Method 1: Via VIO in GUI**
1. In VIO dashboard, set `probe_out1` to `1`
2. Verify LED[6] lights up on FPGA
3. Perform memory read
4. Set `probe_out1` back to `0`

**Method 2: Via AXI Register Write**
```tcl
set jtag_axi [get_hw_axis hw_axi_1]
create_hw_axi_txn freeze $jtag_axi \
    -address 0x00100000 -data 00000001 -type write
run_hw_axi freeze
```

### Wait for Specific Frame

```tcl
# Read current frame count
create_hw_axi_txn read_fc $jtag_axi \
    -address 0x00100008 -type read
run_hw_axi read_fc
set fc1 [get_property DATA [get_hw_axi_txn read_fc]]

# Wait for increment
after 20
run_hw_axi read_fc
set fc2 [get_property DATA [get_hw_axi_txn read_fc]]

if {$fc2 > $fc1} {
    puts "Frame advanced from $fc1 to $fc2"
}
```

### Capture Full Frame via TCL

```tcl
# Freeze simulation
create_hw_axi_txn freeze $jtag_axi \
    -address 0x00100000 -data 00000001 -type write
run_hw_axi freeze

# Read trail memory in chunks (76800 words = 307200 bytes)
for {set i 0} {$i < 76800} {incr i 1024} {
    create_hw_axi_txn read_chunk_$i $jtag_axi \
        -address [expr $i * 4] -len 1024 -type read
    run_hw_axi read_chunk_$i
    # Process data...
}

# Resume simulation
create_hw_axi_txn resume $jtag_axi \
    -address 0x00100000 -data 00000000 -type write
run_hw_axi resume
```

## Troubleshooting

### Problem: "No hardware targets found"
**Solution**:
1. Check USB cable connection
2. Verify FPGA is powered on
3. Install/update cable drivers:
   ```bash
   sudo $XILINX_VIVADO/data/xicom/cable_drivers/lin64/install_script/install_drivers/install_drivers
   ```

### Problem: "JTAG-to-AXI not detected"
**Solution**:
1. Verify debug bitstream is programmed (not production version)
2. Check bitstream path in program_debug_fpga.tcl
3. Refresh hardware device: `refresh_hw_device [current_hw_device]`

### Problem: Frame count not incrementing
**Solution**:
1. Press BTNC to start simulation
2. Check LED[4] is lit (simulation running)
3. Verify VGA is not frozen (LED[6] should be off)

### Problem: Memory reads return all zeros
**Solution**:
1. Start simulation (BTNC button)
2. Wait several seconds for trails to form
3. Check agent_idx is advancing (use ILA or VIO)
4. Verify trail memory writes (check trail_we_b signal in ILA)

### Problem: Bitstream build fails
**Solution**:
1. Check Vivado version (needs 2023.x or later for IP versions)
2. Verify all source files exist
3. Check reports in `vivado_project_debug/slime_simulator_debug.runs/synth_1/`
4. Look for timing violations in `reports/timing_summary.txt`

## Performance Notes

- **Full frame read time**: ~20-50 ms (depends on JTAG adapter speed)
- **Single register read**: ~5-10 ms
- **Frame rate**: ~60 Hz when running (VGA vertical refresh)
- **ILA sample rate**: 100 MHz (10 ns per sample)

## File Structure

```
rtl/
├── add_ip_cores.tcl              # Create debug IP cores
├── rebuild_with_ips.tcl          # Full build with debug IPs
├── program_debug_fpga.tcl        # Program debug bitstream
├── register_map.txt              # Complete register reference
├── ip_integration_report.txt    # Detailed integration guide
├── QUICKSTART_DEBUG.md           # This file
├── fpga_controller.py            # Python interface (framework)
│
├── src/
│   ├── slime_top_debug.sv        # Debug-enabled top module
│   └── debug_wrapper.sv          # AXI-to-memory bridge
│
├── vivado_project_debug/
│   ├── ip/
│   │   ├── debug_jtag_axi/      # JTAG-to-AXI IP
│   │   ├── debug_vio/           # VIO IP
│   │   └── debug_ila/           # ILA IP
│   └── reports/                  # Build reports
```

## Next Steps

1. **Verify Setup**: Follow Quick Start to build and program
2. **Test Basic Access**: Use VIO to read frame_count
3. **Capture Waveforms**: Use ILA to verify simulation FSM
4. **Implement Python**: Complete fpga_controller.py JTAG-to-AXI functions
5. **Run Regression**: Compare FPGA vs Python simulator outputs

## Additional Resources

- **Detailed Register Map**: `register_map.txt`
- **Integration Report**: `ip_integration_report.txt`
- **Xilinx Documentation**:
  - UG908: Programming and Debugging Guide
  - PG174: JTAG to AXI Master Product Guide
  - PG159: Virtual Input/Output Product Guide

## Support

For questions or issues:
- Check `ip_integration_report.txt` for detailed integration info
- Verify all files in this directory are present
- Consult Xilinx forums for IP-specific questions

---

**Last Updated**: 2025-11-24
**Target Device**: Basys3 (Artix-7 XC7A35T)
**Vivado Version**: 2023.x or later
