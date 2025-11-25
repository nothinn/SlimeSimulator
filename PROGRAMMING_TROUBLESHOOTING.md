# FPGA Programming Troubleshooting Guide

## Common Issues & Solutions

### Issue 1: "No FPGA devices found" or "Could not open hardware target"

**Cause:** Basys3 board not detected or JTAG connection not established

**Solutions:**

1. **Check Physical Connection**
   ```bash
   # Verify USB device is detected
   lsusb | grep -i xilinx
   # Should show something like: "Future Technology Devices International Ltd FT2232H..."
   ```

2. **Check USB Port**
   - Try different USB port (preferably USB 3.0)
   - Avoid USB hubs if possible
   - Try directly to PC motherboard USB

3. **Power the Board**
   - Ensure Basys3 has power via USB or external adapter
   - Look for green LED on board (power indicator)
   - Check for any red error LEDs

4. **Reset the Board**
   - Unplug USB cable
   - Wait 5 seconds
   - Plug USB back in
   - Wait for device to enumerate (check `lsusb`)

5. **Check Vivado Path**
   ```bash
   ls -la ~/2025.2/Vivado/.settings64-Vivado.sh
   # If not found, adjust VIVADO_SETUP path in script
   ```

---

### Issue 2: "ERROR: Failed to program device"

**Cause:** Device detected but programming failed

**Solutions:**

1. **Verify Bitstream File**
   ```bash
   ls -lh rtl/vivado_project/slime_simulator.runs/impl_1/slime_top.bit
   # Should be ~439 KB
   ```

2. **Try Different Bitstream**
   ```bash
   # Try VGA test pattern (simpler design)
   ./scripts/program_fpga.sh rtl/vivado_project_solid/vga_solid_test.runs/impl_1/vga_solid_color.bit
   ```

3. **Use Vivado GUI**
   ```bash
   source ~/2025.2/Vivado/.settings64-Vivado.sh
   vivado -mode gui
   # Navigate: Hardware → Open Hardware Manager → Program Device
   ```

---

### Issue 3: "ERROR: Failed to open hardware manager"

**Cause:** Vivado environment not properly initialized

**Solutions:**

1. **Manually Source Vivado**
   ```bash
   source ~/2025.2/Vivado/.settings64-Vivado.sh
   echo $VIVADO_HLS  # Should output vivado path
   ```

2. **Check Vivado Installation**
   ```bash
   which vivado
   # Should show: /home/reson/2025.2/Vivado/bin/vivado
   ```

3. **Try Interactive Mode**
   ```bash
   source ~/2025.2/Vivado/.settings64-Vivado.sh
   vivado &  # Opens GUI (easier to debug)
   ```

---

## Alternative Programming Methods

### Method 1: Vivado GUI (Most Reliable)

```bash
source ~/2025.2/Vivado/.settings64-Vivado.sh
vivado -mode gui &
```

**Steps:**
1. Open Vivado GUI
2. Click "Open Hardware Manager"
3. Click "Open Target"
4. Select Basys3 device
5. Program with bitstream file
6. Watch for "Done" message

**Advantages:** Visual feedback, easier to debug

---

### Method 2: Manual TCL Script

**Create file: `program_manual.tcl`**

```tcl
open_hw_manager
connect_hw_server
open_hw_target

set device [lindex [get_hw_devices] 0]
puts "Found device: $device"

set_property PROGRAM.FILE {/home/reson/SlimeSimulator/rtl/vivado_project/slime_simulator.runs/impl_1/slime_top.bit} $device
program_hw_device $device

puts "Programming complete!"
close_hw_target
disconnect_hw_server
close_hw_manager
```

**Run it:**
```bash
source ~/2025.2/Vivado/.settings64-Vivado.sh
vivado -mode batch -source program_manual.tcl
```

---

### Method 3: Using xsdb (Xilinx System Debugger)

```bash
source ~/2025.2/Vivado/.settings64-Vivado.sh

# List connected devices
xsdb -eval "connect; targets"

# Program device (replace DEVICE_NAME)
xsdb -eval "connect; targets DEVICE_NAME; source_file rtl/vivado_project/slime_simulator.runs/impl_1/slime_top.bit"
```

---

## Debugging Commands

### Check USB Connection
```bash
# List all USB devices
lsusb

# Monitor USB events (run in separate terminal)
usbmon

# Check dmesg for FTDI driver messages
dmesg | grep -i ftdi
```

### Check JTAG Chain
```bash
source ~/2025.2/Vivado/.settings64-Vivado.sh
vivado -mode batch -source - << 'EOF'
open_hw_manager
connect_hw_server
get_hw_targets
close_hw_manager
EOF
```

### Verify Bitstream
```bash
# Check file exists and has reasonable size
ls -lh rtl/vivado_project/slime_simulator.runs/impl_1/slime_top.bit

# Should output something like:
# -rw-r--r-- 1 user user 439K Nov 25 15:25 slime_top.bit
```

---

## Step-by-Step Diagnostic

Run this to test connectivity:

```bash
#!/bin/bash
set -e

echo "1. Checking Vivado installation..."
source ~/2025.2/Vivado/.settings64-Vivado.sh
echo "✓ Vivado sourced"

echo ""
echo "2. Checking bitstream..."
ls -lh rtl/vivado_project/slime_simulator.runs/impl_1/slime_top.bit
echo "✓ Bitstream found"

echo ""
echo "3. Checking USB device..."
lsusb | grep -i xilinx && echo "✓ Basys3 detected" || echo "✗ Basys3 NOT detected"

echo ""
echo "4. Testing JTAG connection..."
vivado -mode batch -source - 2>&1 << 'EOF' | grep -E "(target|device|ERROR)" || echo "Testing..."
open_hw_manager
connect_hw_server -quiet
if {[catch {open_hw_target} err]} {
    puts "ERROR: $err"
} else {
    puts "SUCCESS: Hardware target opened"
    close_hw_target
}
disconnect_hw_server
close_hw_manager
EOF

echo ""
echo "Diagnostic complete!"
```

---

## If All Else Fails

### 1. Reset Everything
```bash
# Kill any stuck vivado processes
pkill -f vivado

# Power cycle board
# (Unplug USB, wait 10 seconds, plug back in)

# Retry
./scripts/program_fpga.sh
```

### 2. Update Vivado Tools
```bash
source ~/2025.2/Vivado/.settings64-Vivado.sh

# Run hardware server in foreground to see errors
hw_server -d
```

### 3. Use JTAG Programmer Directly
```bash
# If OpenOCD is installed
sudo openocd -f interface/ftdi/digilent_hs1.cfg -f board/digilent_basys3.cfg
```

---

## Success Indicators

When programming works, you should see:

```
==================================================
FPGA Programming Script
==================================================
Bitstream: rtl/vivado_project/slime_simulator.runs/impl_1/slime_top.bit
Size: 439K

Executing Vivado programming...

Connecting to JTAG...
Target opened successfully
Programming device: ...
Device programmed successfully!
Done

==================================================
✅ PROGRAMMING SUCCESSFUL!
==================================================

Next steps:
  1. Check board LEDs (should show some activity)
  2. Press BTNC (center button) to start simulation
  3. Observe trail patterns on VGA display
```

---

## Post-Programming Verification

After successful programming:

1. **Check LEDs**
   - LED[4] should light/blink (running indicator)
   - LED[3:0] should show 0000 (speed level 0)
   - Some other LEDs should show LFSR state

2. **Test Controls**
   - Press BTNC: LED[4] should toggle on/off
   - Press BTNU: LED[3:0] should increment
   - Press BTNL: Pattern should change

3. **Check VGA Output**
   - Monitor should show some activity
   - Random dots should be visible
   - Press BTNC to start movement

---

## Getting Help

If stuck, run this diagnostic and share output:

```bash
#!/bin/bash
echo "=== DIAGNOSTIC INFO ==="
echo "Vivado version:"
vivado -version

echo ""
echo "USB devices:"
lsusb

echo ""
echo "Bitstream info:"
ls -lh rtl/vivado_project/slime_simulator.runs/impl_1/slime_top.bit

echo ""
echo "Environment:"
echo "PATH=$PATH" | head -1
echo "VIVADO_HLS=$VIVADO_HLS"
```

---

## Summary

| Issue | Solution |
|-------|----------|
| Device not found | Check USB cable, power, different port |
| Programming fails | Try GUI, verify bitstream, check path |
| No response | Power cycle board, kill vivado, retry |
| Unknown error | Run diagnostic, check dmesg, reinstall drivers |

**Most reliable method:** Use Vivado GUI (`vivado -mode gui`) for manual programming

