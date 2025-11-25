# JTAG Debug Tools Guide for Slime Simulator

## Overview

This guide covers the comprehensive suite of Python tools for debugging and validating the Slime Simulator FPGA implementation via JTAG. These tools provide real-time access to FPGA internal state, waveform capture, and automated comparison with the Python reference model.

**Created:** 2025-11-25
**Version:** 1.0

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Tool Reference](#tool-reference)
   - [jtag_inspect.py](#jtag_inspectpy)
   - [vio_control.py](#vio_controlpy)
   - [ila_capture.py](#ila_capturepy)
   - [fpga_compare.py](#fpga_comparepy)
   - [fpga_debug_monitor.py](#fpga_debug_monitorpy)
4. [Common Workflows](#common-workflows)
5. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Hardware
- **Basys3 FPGA Board** with programmed debug-enabled bitstream
- **USB Cable** connected to host PC
- **Xilinx Platform Cable** (or built-in JTAG)

### Required Software
- **Vivado 2025.2** (or compatible version)
- **Vivado Hardware Server** (hw_server) running on localhost:3121
- **Python 3.6+** with packages:
  - numpy (for numerical operations)
  - PIL/Pillow (for image generation)
  - matplotlib (optional, for advanced visualizations)

### Setup
1. **Start Hardware Server:**
   ```bash
   # In one terminal
   source ~/2025.2/Vivado/.settings64-Vivado.sh
   hw_server
   ```

2. **Program FPGA:**
   ```bash
   # In another terminal
   cd /home/reson/SlimeSimulator
   vivado -mode batch -source rtl/program_fpga.tcl
   ```

3. **Verify Connection:**
   ```bash
   cd /home/reson/SlimeSimulator/scripts
   ./jtag_inspect.py --read-all --dry-run
   ```

---

## Quick Start

### 10-Second Status Check
```bash
./fpga_debug_monitor.py --snapshot
```

### Read Current FPGA State
```bash
./jtag_inspect.py --read-all
```

### Compare FPGA with Python Reference
```bash
./fpga_compare.py --full-compare --seed 0x12345678 --steps 10
```

### Monitor FPGA in Real-Time
```bash
./fpga_debug_monitor.py --rate 1.0 --show-trail
```

---

## Tool Reference

### jtag_inspect.py

**Purpose:** Low-level JTAG interface for reading/writing FPGA registers and memory.

**Key Features:**
- Read LFSR state (32-bit random number generator)
- Read simulation state machine
- Read current agent index
- Read/write trail map memory
- Freeze/unfreeze simulation
- Compare trail maps

**Common Commands:**

```bash
# Read LFSR state
./jtag_inspect.py --read-lfsr

# Read simulation state
./jtag_inspect.py --read-state

# Read all status registers
./jtag_inspect.py --read-all

# Freeze simulation for inspection
./jtag_inspect.py --freeze

# Dump entire 160×120 trail map to binary
./jtag_inspect.py --dump-trail-map fpga_trail.bin

# Dump trail map as PNG image
./jtag_inspect.py --dump-trail-png fpga_trail.png

# Read single pixel at (80, 60)
./jtag_inspect.py --read-pixel 80 60

# Compare FPGA trail with Python reference
./jtag_inspect.py --compare fpga_trail.bin python_trail.bin

# Unfreeze simulation
./jtag_inspect.py --unfreeze
```

**Options:**
- `--hw-server HOST:PORT` - Hardware server address (default: localhost:3121)
- `--dry-run` - Show commands without executing
- `-v, --verbose` - Enable detailed logging

**Exit Codes:**
- `0` - Success
- `1` - Connection or operation failure

---

### vio_control.py

**Purpose:** High-level interface to Virtual I/O (VIO) registers for live monitoring and control.

**Key Features:**
- Read VIO input probes (FPGA → Software)
- Write VIO output probes (Software → FPGA)
- Inject LFSR seed for reproducible tests
- Real-time dashboard mode
- Pretty-print register values

**VIO Input Probes (Read):**
- `lfsr_state[31:0]` - Current LFSR value
- `sim_state[3:0]` - State machine (0=RESET, 1=INIT, 2=PROCESS_AGENTS, etc.)
- `agent_idx[9:0]` - Current agent (0-999)
- `frame_count[31:0]` - VGA frame counter (~60 Hz)
- `sim_running` - Running flag
- `led_status[15:0]` - LED display

**VIO Output Probes (Write):**
- `sim_freeze` - Freeze simulation
- `trail_read_en` - Enable trail map read
- `trail_addr[18:0]` - Trail map address
- `lfsr_seed[31:0]` - Inject new seed

**Common Commands:**

```bash
# Read all VIO registers
./vio_control.py --read-all

# Read just LFSR state
./vio_control.py --read-lfsr

# Read simulation state
./vio_control.py --read-state

# Freeze simulation
./vio_control.py --freeze

# Unfreeze simulation
./vio_control.py --unfreeze

# Inject new LFSR seed
./vio_control.py --set-lfsr-seed 0x12345678

# Read trail pixel via VIO
./vio_control.py --read-pixel 80 60

# Real-time monitor (updates every second)
./vio_control.py --monitor

# Monitor at 2 Hz
./vio_control.py --monitor --interval 0.5
```

**Monitor Mode:**
Press `Ctrl+C` to exit monitoring loop.

---

### ila_capture.py

**Purpose:** Configure and capture waveforms from the Integrated Logic Analyzer (ILA).

**Key Features:**
- Arm ILA for capture
- Configure trigger conditions
- Capture up to 8192 samples
- Export to CSV or VCD format
- Analyze capture statistics

**ILA Probes (15 total):**
- Probe 0: `lfsr_state[31:0]`
- Probe 1: `sim_state[3:0]`
- Probe 2: `agent_idx[9:0]`
- Probe 3: `trail_addr_b[18:0]`
- Probe 4: `trail_data_b_in[7:0]`
- Probe 5: `trail_we_b`
- Probe 6: `vga_hs`
- Probe 7: `vga_vs`
- Probe 8: `pixel_x[9:0]`
- Probe 9: `pixel_y[8:0]`
- Probe 10: `frame_start`
- Probe 11: `sim_running`
- Probe 12: `sim_pause`
- Probe 13: `speed_level[3:0]`
- Probe 14: `btn_debounced[4:0]`

**Common Commands:**

```bash
# Arm ILA and wait for trigger
./ila_capture.py --arm --wait --capture output.csv

# Trigger on specific LFSR value
./ila_capture.py --trigger-lfsr 0x12345678 --capture lfsr_trigger.csv

# Trigger on agent index 0
./ila_capture.py --trigger-agent 0 --capture agent0.csv

# Trigger on simulation state = PROCESS_AGENTS (2)
./ila_capture.py --trigger-state 2 --capture state2.csv

# Trigger on frame start pulse
./ila_capture.py --trigger-frame-start --capture frame_start.csv

# Analyze existing capture
./ila_capture.py --analyze capture.csv

# Export CSV to VCD for waveform viewers (GTKWave, etc.)
./ila_capture.py --load capture.csv --export-vcd waveform.vcd
```

**Trigger Timeout:**
- Default: 30 seconds
- Use `--timeout N` to override

**Viewing VCD Files:**
```bash
gtkwave waveform.vcd
```

---

### fpga_compare.py

**Purpose:** Master comparison tool for validating FPGA implementation against Python reference.

**Key Features:**
- Automated end-to-end comparison workflow
- Captures FPGA trail map via JTAG
- Runs Python reference with same seed
- Pixel-by-pixel comparison
- Statistical analysis
- Visual difference maps
- Batch testing

**Common Commands:**

```bash
# Full automated comparison
./fpga_compare.py --full-compare --seed 0x12345678 --steps 10 --output-dir results/

# Compare pre-captured files
./fpga_compare.py --compare-files fpga.bin python.bin

# Generate difference image
./fpga_compare.py --compare-files fpga.bin python.bin --diff diff.png

# Batch test with 100 random seeds
./fpga_compare.py --batch-test 100 --output-dir batch_results/

# Compare with tolerance (allow ±2 error)
./fpga_compare.py --compare-files fpga.bin python.bin --tolerance 2
```

**Output Files:**
- `fpga_trail.bin` - Captured FPGA trail map
- `python_trail.bin` - Python reference trail map
- `diff.png` - Visual difference map (green=match, red=FPGA higher, blue=Python higher)
- `comparison.png` - Side-by-side comparison
- `stats.txt` - Comparison statistics

**Interpretation:**
- **100% match** → Perfect FPGA implementation
- **>99% match** → Excellent (minor timing differences)
- **>95% match** → Good (investigate differences)
- **<95% match** → Poor (major issues)

---

### fpga_debug_monitor.py

**Purpose:** Unified real-time dashboard combining all debug information.

**Key Features:**
- Live status updates (1 Hz default)
- LFSR state monitoring
- State machine status
- Agent processing progress
- Frame rate (FPS) calculation
- LED status visualization
- ASCII art trail map preview
- ANSI color support

**Common Commands:**

```bash
# Start interactive monitor
./fpga_debug_monitor.py

# Monitor at 2 Hz
./fpga_debug_monitor.py --rate 0.5

# Include trail map preview
./fpga_debug_monitor.py --show-trail

# Single snapshot (no loop)
./fpga_debug_monitor.py --snapshot

# Disable colors (for non-ANSI terminals)
./fpga_debug_monitor.py --no-color

# Save logs to file
./fpga_debug_monitor.py --log-file debug.log
```

**Monitor Display:**
```
================================================================================
FPGA Debug Monitor - 2025-11-25 14:30:00
================================================================================

SYSTEM STATUS:
  LFSR State:       0x12345678 (305419896)
  Sim State:        2 (PROCESS_AGENTS)
  Agent Index:      450/999
  Frame Count:      1234
  Frame Rate:       60.1 FPS
  Simulation:       RUNNING

LED STATUS:
  LEDs:             0x03FF (0000001111111111)
                    ░░░░░░░░████████

TRAIL MAP PREVIEW (ASCII):
  [ASCII art representation of trail map]
================================================================================
```

---

## Common Workflows

### Workflow 1: Verify FPGA is Running Correctly

```bash
# Step 1: Quick status check
./fpga_debug_monitor.py --snapshot

# Step 2: Check simulation is running
# Look for "Simulation: RUNNING" and FPS > 50

# Step 3: Verify LFSR is changing
./jtag_inspect.py --read-lfsr
# Wait a few seconds
./jtag_inspect.py --read-lfsr
# LFSR value should be different
```

### Workflow 2: Capture and Analyze Trail Map

```bash
# Step 1: Freeze simulation
./vio_control.py --freeze

# Step 2: Capture trail map
./jtag_inspect.py --dump-trail-map frozen_trail.bin
./jtag_inspect.py --dump-trail-png frozen_trail.png

# Step 3: Analyze image
# Open frozen_trail.png in image viewer

# Step 4: Unfreeze
./vio_control.py --unfreeze
```

### Workflow 3: Debug Specific Agent Processing

```bash
# Step 1: Trigger ILA on agent 0
./ila_capture.py --trigger-agent 0 --capture agent0.csv --timeout 60

# Step 2: Analyze capture
./ila_capture.py --analyze agent0.csv

# Step 3: Export to waveform viewer
./ila_capture.py --load agent0.csv --export-vcd agent0.vcd
gtkwave agent0.vcd
```

### Workflow 4: Validate FPGA Implementation

```bash
# Step 1: Inject known seed
./vio_control.py --set-lfsr-seed 0xDEADBEEF

# Step 2: Wait for simulation to run
sleep 5

# Step 3: Full comparison
./fpga_compare.py --full-compare --seed 0xDEADBEEF --steps 10 --output-dir validation/

# Step 4: Check results
# Look for "PERFECT MATCH" in output
ls -lh validation/
# Review diff.png and comparison.png
```

### Workflow 5: Batch Regression Testing

```bash
# Run 100 comparisons with random seeds
./fpga_compare.py --batch-test 100 --output-dir regression_results/

# Check summary
# Look for "Passed: 100/100 (100.0%)"

# If failures, investigate
# Failed seeds are printed for manual testing
```

---

## Troubleshooting

### Cannot Connect to Hardware Server

**Symptom:** `Failed to connect to FPGA`

**Solutions:**
1. Check hw_server is running:
   ```bash
   ps aux | grep hw_server
   ```

2. Start hw_server if not running:
   ```bash
   source ~/2025.2/Vivado/.settings64-Vivado.sh
   hw_server
   ```

3. Check FPGA is connected:
   ```bash
   lsusb | grep Xilinx
   ```

4. Try specifying server explicitly:
   ```bash
   ./jtag_inspect.py --hw-server localhost:3121 --read-all
   ```

### No ILA/VIO Cores Found

**Symptom:** `ERROR: No ILA cores found` or `ERROR: No VIO cores found`

**Cause:** FPGA programmed with non-debug bitstream

**Solution:**
1. Rebuild with debug cores:
   ```bash
   cd /home/reson/SlimeSimulator
   vivado -mode batch -source rtl/build_with_debug.tcl
   ```

2. Program FPGA with debug bitstream:
   ```bash
   vivado -mode batch -source rtl/program_fpga.tcl
   ```

### Comparison Shows Mismatches

**Symptom:** `Match percentage: 87.3%` (not 100%)

**Debugging Steps:**

1. **Check if timing-related:**
   - Run multiple comparisons with same seed
   - If results vary → timing issue
   - If results consistent → logic issue

2. **Visual inspection:**
   ```bash
   ./fpga_compare.py --compare-files fpga.bin python.bin --diff diff.png
   # Open diff.png - red/blue pixels show mismatches
   ```

3. **Capture ILA waveform:**
   ```bash
   ./ila_capture.py --trigger-agent 0 --capture debug.csv
   ./ila_capture.py --load debug.csv --export-vcd debug.vcd
   gtkwave debug.vcd
   ```

4. **Check specific pixel:**
   ```bash
   # Find mismatch location in diff.png (e.g., x=45, y=67)
   ./jtag_inspect.py --read-pixel 45 67
   # Compare with Python reference
   ```

### ILA Trigger Timeout

**Symptom:** `ILA trigger timeout`

**Solutions:**

1. **Increase timeout:**
   ```bash
   ./ila_capture.py --trigger-lfsr 0x12345678 --timeout 120
   ```

2. **Check trigger condition is reachable:**
   - LFSR cycles through all values, but may take time
   - Agent 0 happens every frame
   - Frame start happens ~60 times/second

3. **Use broader trigger:**
   ```bash
   # Instead of specific LFSR value, trigger on frame start
   ./ila_capture.py --trigger-frame-start --capture output.csv
   ```

### Monitor Shows Wrong Values

**Symptom:** Monitor displays unexpected values

**Checks:**

1. **Verify FPGA is actually running:**
   ```bash
   ./jtag_inspect.py --read-frame
   # Wait 1 second
   ./jtag_inspect.py --read-frame
   # Frame count should increment
   ```

2. **Check for simulation freeze:**
   ```bash
   ./vio_control.py --read-state
   # Should show PROCESS_AGENTS or similar, not PAUSED
   ```

3. **Unfreeze if needed:**
   ```bash
   ./vio_control.py --unfreeze
   ```

---

## Advanced Topics

### Creating Custom Comparison Scripts

Example: Compare at multiple time points

```python
#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/reson/SlimeSimulator/scripts')
from fpga_compare import full_compare_workflow

seeds = [0x12345678, 0xDEADBEEF, 0xCAFEBABE]

for seed in seeds:
    print(f"\nTesting seed: 0x{seed:08X}")
    success = full_compare_workflow(seed, steps=10, output_dir=f"test_{seed:08X}")
    print(f"Result: {'PASS' if success else 'FAIL'}")
```

### Exporting Data for External Analysis

```bash
# Capture trail map
./jtag_inspect.py --dump-trail-map data.bin

# Process with Python
python3 << EOF
import numpy as np
data = np.fromfile('data.bin', dtype=np.uint8)
data = data.reshape((120, 160))
print(f"Mean intensity: {data.mean():.2f}")
print(f"Max intensity: {data.max()}")
print(f"Std deviation: {data.std():.2f}")
EOF
```

---

## Summary

The JTAG debug tools provide comprehensive access to FPGA internals:

- **jtag_inspect.py** - Low-level memory and register access
- **vio_control.py** - High-level VIO register interface
- **ila_capture.py** - Waveform capture and analysis
- **fpga_compare.py** - Automated validation
- **fpga_debug_monitor.py** - Real-time unified dashboard

**Recommended Quick Start:**
1. Start monitor: `./fpga_debug_monitor.py`
2. Run comparison: `./fpga_compare.py --full-compare`
3. Investigate issues: `./ila_capture.py` and `./jtag_inspect.py`

For questions or issues, see the tool help:
```bash
./jtag_inspect.py --help
./vio_control.py --help
./ila_capture.py --help
./fpga_compare.py --help
./fpga_debug_monitor.py --help
```

---

**End of Guide**
