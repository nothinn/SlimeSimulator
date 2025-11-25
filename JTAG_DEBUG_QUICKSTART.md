# JTAG Debug Tools - Quick Start Guide

**Status:** Ready to use once debug-enabled bitstream is programmed

## What You Now Have

Five Python tools for real-time FPGA debugging and inspection:

1. **jtag_inspect.py** - Memory and state inspection
2. **ila_capture.py** - Waveform capture
3. **vio_control.py** - Register read/write
4. **fpga_compare.py** - FPGA vs Python validation
5. **fpga_debug_monitor.py** - Real-time dashboard

## Setup (Do This First)

### 1. Verify Tools Are Installed
```bash
cd /home/reson/SlimeSimulator
ls -la scripts/jtag_*.py scripts/*_monitor.py scripts/*_capture.py
```

All 5 tools should be present.

### 2. Check Python Dependencies
```bash
source .venv/bin/activate
python3 -c "import numpy, PIL; print('OK')"
```

If missing, install:
```bash
pip install numpy pillow
```

### 3. Start Vivado Hardware Server
```bash
source ~/2025.2/Vivado/.settings64-Vivado.sh
hw_server > /dev/null 2>&1 &
```

Verify it's running:
```bash
netstat -an | grep 3121  # Port 3121 should be listening
```

### 4. Program FPGA with Debug Bitstream
```bash
cd /home/reson/SlimeSimulator
python3 scripts/fpga_programmer.py \
  --bitstream rtl/vivado_project_debug/slime_simulator_debug.runs/impl_1/slime_top.bit
```

Expected output:
```
[...] FPGA programmed successfully!
```

## Quick Tests (5 Minutes)

### Test 1: Verify FPGA is Running
```bash
cd /home/reson/SlimeSimulator/scripts
./vio_control.py --read-all
```

Expected output:
```
VIO Register Status:
  LFSR State:      0x12345678
  Sim State:       2 (PROCESS_AGENTS)
  Agent Index:     450
  Frame Count:     1234
  ...
```

### Test 2: Take a Snapshot
```bash
./fpga_debug_monitor.py --snapshot
```

Shows:
```
FPGA Debug Monitor - Snapshot
SYSTEM STATUS:
  LFSR State:       0x12345678
  Agent Index:      450/999
  Frame Count:      1234
  Frame Rate:       60.1 FPS
  ...
```

### Test 3: Capture Trail Map
```bash
./jtag_inspect.py --dump-trail-map fpga.bin
```

Creates `fpga.bin` (19,200 bytes) containing the trail map.

### Test 4: Export as PNG
```bash
./jtag_inspect.py --dump-trail-png fpga.png
```

Creates `fpga.png` - visual display of trail intensity.

### Test 5: Compare with Python
```bash
./fpga_compare.py --full-compare --seed 0xDEADBEEF --steps 10
```

Outputs:
```
FPGA vs Python Comparison
  Total Pixels: 19200
  Matched:      19200 (100.0%)
  Max Error:    0
  Mean Error:   0.0
  Status:       PASS
```

## Common Workflows

### Workflow 1: Daily Validation

Run this to verify FPGA is working correctly:

```bash
#!/bin/bash
cd /home/reson/SlimeSimulator/scripts

echo "1. Checking FPGA connectivity..."
./vio_control.py --read-all | head -5

echo "2. Capturing trail map..."
./jtag_inspect.py --dump-trail-png fpga_now.png

echo "3. Running Python reference..."
cd ..
python3 slime_simulator.py > /tmp/python_ref.log

echo "4. Comparing..."
cd scripts
./fpga_compare.py --compare-files fpga.bin ../validation_outputs/*.bin
```

### Workflow 2: Debugging Specific Issue

When you see something wrong on VGA display:

```bash
cd /home/reson/SlimeSimulator/scripts

# 1. Freeze simulation to inspect
./vio_control.py --freeze

# 2. Take snapshots at different times
./fpga_debug_monitor.py --snapshot > debug1.txt
sleep 1
./fpga_debug_monitor.py --snapshot > debug2.txt

# 3. Compare LFSR values
grep "LFSR" debug1.txt
grep "LFSR" debug2.txt

# 4. Unfreeze
./vio_control.py --unfreeze
```

### Workflow 3: Performance Analysis

Measure and verify frame rate:

```bash
cd /home/reson/SlimeSimulator/scripts

# Monitor for 30 seconds
for i in {1..30}; do
  ./vio_control.py --read-all | grep "Frame Rate"
  sleep 1
done
```

Expected: Constant 60 FPS (±0.1 Hz)

### Workflow 4: Capture ILA Waveform

Debug specific agent processing:

```bash
cd /home/reson/SlimeSimulator/scripts

# Trigger when processing agent 0
./ila_capture.py --trigger-agent 0 --capture waveform.csv

# Wait for capture...
# Once complete, examine
head -20 waveform.csv

# Export to waveform viewer
./ila_capture.py --load waveform.csv --export-vcd waveform.vcd
```

Open `waveform.vcd` in GTKWave or similar viewer.

### Workflow 5: Batch Regression Testing

Test multiple seeds for consistency:

```bash
cd /home/reson/SlimeSimulator/scripts

for seed in 0x00000001 0x12345678 0xDEADBEEF 0xFFFFFFFF; do
  echo "Testing seed $seed..."
  ./fpga_compare.py --full-compare --seed $seed --steps 20
done
```

All should pass with 100% match.

## Tool Reference

### jtag_inspect.py

**Read all status:**
```bash
./jtag_inspect.py --read-all
```

**Dump trail map:**
```bash
./jtag_inspect.py --dump-trail-map output.bin
./jtag_inspect.py --dump-trail-png output.png
```

**Read specific pixel:**
```bash
./jtag_inspect.py --read-pixel 160 120
```

**Compare with Python:**
```bash
./jtag_inspect.py --compare fpga.bin python.bin
```

### vio_control.py

**Read all registers:**
```bash
./vio_control.py --read-all
```

**Control simulation:**
```bash
./vio_control.py --freeze              # Pause agents
./vio_control.py --unfreeze            # Resume
```

**Inject LFSR seed:**
```bash
./vio_control.py --set-lfsr-seed 0x12345678
```

**Live monitoring:**
```bash
./vio_control.py --monitor             # Updates 1 Hz
./vio_control.py --monitor --rate 0.5  # Updates 2 Hz
```

### ila_capture.py

**Capture on condition:**
```bash
./ila_capture.py --trigger-agent 0 --capture out.csv
./ila_capture.py --trigger-lfsr 0x12345678 --capture out.csv
```

**Analyze captured data:**
```bash
./ila_capture.py --analyze out.csv
```

**Export to VCD:**
```bash
./ila_capture.py --load out.csv --export-vcd out.vcd
```

### fpga_compare.py

**Full end-to-end comparison:**
```bash
./fpga_compare.py --full-compare --seed 0xDEADBEEF --steps 10
```

**Compare two files:**
```bash
./fpga_compare.py --compare-files fpga.bin python.bin
```

**Generate visual diff:**
```bash
./fpga_compare.py --compare-files fpga.bin python.bin --diff diff.png
```

**Batch testing:**
```bash
./fpga_compare.py --batch-test 100 --output-dir results/
```

### fpga_debug_monitor.py

**Single snapshot:**
```bash
./fpga_debug_monitor.py --snapshot
```

**Continuous monitoring:**
```bash
./fpga_debug_monitor.py              # 1 Hz updates
./fpga_debug_monitor.py --rate 0.5   # 2 Hz updates
```

**Include trail preview:**
```bash
./fpga_debug_monitor.py --show-trail
```

**Save to file:**
```bash
./fpga_debug_monitor.py --log-file debug.log
```

## What You Can Inspect

### Via VIO (Real-Time Access)

- **LFSR State** - Current 32-bit random value
- **Simulation State** - IDLE/INIT/PROCESS_AGENTS/DIFFUSE/WAIT_FRAME
- **Agent Index** - Which of 1000 agents is being processed (0-999)
- **Frame Counter** - Total frames since boot
- **Frame Rate** - Calculated FPS from frame counter
- **LED Status** - What LEDs are currently displaying
- **Trail Map Pixel** - Read any of 19,200 pixels

### Via ILA (Waveform Capture)

- LFSR output transitions
- State machine changes
- Agent processing progress
- Trail memory reads/writes
- VGA timing signals (hsync, vsync)
- Button/switch changes

### Via JTAG-to-AXI (Memory Access)

- Complete 160×120 trail map (19,200 bytes)
- Binary or PNG export
- Pixel-by-pixel readback

## Troubleshooting

### Error: "Failed to connect to FPGA"
```bash
# Check if FPGA is programmed
python3 scripts/fpga_programmer.py --check-only

# Check if hardware server is running
netstat -an | grep 3121

# Restart hardware server
pkill -f hw_server
sleep 1
source ~/2025.2/Vivado/.settings64-Vivado.sh
hw_server > /dev/null 2>&1 &
```

### Error: "JTAG chain not found"
```bash
# Verify USB connection
lsusb | grep Digilent

# Restart Vivado
source ~/2025.2/Vivado/.settings64-Vivado.sh
vivado -mode batch -source rtl/program_fpga.tcl
```

### Trail map looks corrupted
```bash
# Freeze simulation and read again
./vio_control.py --freeze
./jtag_inspect.py --dump-trail-map debug.bin
./jtag_inspect.py --dump-trail-png debug.png

# Compare with Python
python3 slime_simulator.py --steps 10
./fpga_compare.py --compare-files debug.bin validation_outputs/*/trail.bin
```

### Frame rate not 60 FPS
```bash
# Check for timing violations
cat rtl/build_debug.log | grep "slack"

# Monitor frame rate over time
./vio_control.py --monitor | grep "Frame Rate"

# Check if simulation is paused
./vio_control.py --read-all | grep "sim_running"
```

## Tips & Tricks

### Capture Trail at Specific Step
```bash
# Run Python to step N
python3 slime_simulator.py --steps 100 --save-trail ref_step100.bin

# Read FPGA frame counter
fpga_frames=$(./vio_control.py --read-all | grep "Frame" | awk '{print $NF}')

# Wait until FPGA reaches same step (100 frames)
while [ $(./vio_control.py --read-all | grep "Frame" | awk '{print $NF}') -lt $fpga_frames ]; do
  sleep 0.1
done

# Freeze and capture
./vio_control.py --freeze
./jtag_inspect.py --dump-trail-map fpga_step100.bin
./vio_control.py --unfreeze

# Compare
./fpga_compare.py --compare-files fpga_step100.bin ref_step100.bin
```

### Generate Animated Comparison
```bash
for step in 10 20 50 100; do
  echo "Step $step..."
  python3 slime_simulator.py --steps $step --save-trail ref_$step.bin
  # Wait for FPGA to reach same step
  ./fpga_compare.py --compare-files fpga.bin ref_$step.bin --diff diff_$step.png
done
```

### Profile Agent Processing Time
```bash
# Capture ILA with agent 0 trigger
./ila_capture.py --trigger-agent 0 --capture agent0.csv

# Load and analyze
./ila_capture.py --load agent0.csv --analyze

# Expected: ~19 clock cycles per agent at 100 MHz = 190 ns per agent
```

## Next Steps After Verification

1. **If all tests pass (100% match):**
   - Design is bit-accurate ✓
   - Can proceed with production testing
   - Integrate with higher-level system

2. **If tests show differences:**
   - Use ILA to capture exact signal timing
   - Compare with Python reference step-by-step
   - Debug specific failing agent or state
   - Check constraint file compliance

3. **For performance optimization:**
   - Monitor frame rate (should be 60 FPS)
   - Check resource utilization
   - Profile memory access patterns
   - Consider pipelining enhancements

## File Locations

```
Scripts (ready to use):
  /home/reson/SlimeSimulator/scripts/jtag_inspect.py
  /home/reson/SlimeSimulator/scripts/ila_capture.py
  /home/reson/SlimeSimulator/scripts/vio_control.py
  /home/reson/SlimeSimulator/scripts/fpga_compare.py
  /home/reson/SlimeSimulator/scripts/fpga_debug_monitor.py

Bitstreams:
  /home/reson/SlimeSimulator/rtl/vivado_project_debug/slime_simulator_debug.runs/impl_1/slime_top.bit

Documentation:
  /home/reson/SlimeSimulator/scripts/JTAG_TOOLS_GUIDE.md (full reference)
  /home/reson/SlimeSimulator/JTAG_DEBUG_QUICKSTART.md (this file)
```

## Support

For detailed information on each tool, see:
- `scripts/JTAG_TOOLS_GUIDE.md` - Complete reference
- Tool help: `./tool_name.py --help`
- Debug build log: `rtl/build_debug.log`

---

**Status: Tools Ready, Awaiting Debug Bitstream**

Once the debug-enabled bitstream is programmed, use these tools to inspect every aspect of the FPGA implementation.
