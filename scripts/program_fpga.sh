#!/bin/bash
# Program FPGA with bitstream via JTAG
# Supports multiple programming methods with fallback

set -e

BITSTREAM="${1:-rtl/vivado_project/slime_simulator.runs/impl_1/slime_top.bit}"
VIVADO_SETUP="${HOME}/2025.2/Vivado/.settings64-Vivado.sh"

if [ ! -f "$BITSTREAM" ]; then
    echo "ERROR: Bitstream not found: $BITSTREAM"
    exit 1
fi

echo "=================================================="
echo "FPGA Programming Script"
echo "=================================================="
echo "Bitstream: $BITSTREAM"
echo "Size: $(ls -lh "$BITSTREAM" | awk '{print $5}')"
echo ""

# Check if Vivado setup exists
if [ ! -f "$VIVADO_SETUP" ]; then
    echo "ERROR: Vivado not found at $VIVADO_SETUP"
    exit 1
fi

# Source Vivado environment
source "$VIVADO_SETUP"

# Create Vivado TCL programming script with better error handling
PROG_TCL=$(mktemp)
trap "rm -f $PROG_TCL" EXIT

BITSTREAM_PATH="$(cd "$(dirname "$BITSTREAM")" && pwd)/$(basename "$BITSTREAM")"

cat > "$PROG_TCL" << EOF
# FPGA Programming Script
puts "Connecting to JTAG..."

# Try to open hardware manager
if {[catch {open_hw_manager} err]} {
    puts "ERROR: Failed to open hardware manager: \$err"
    exit 1
}

# Connect to hardware server
if {[catch {connect_hw_server -quiet} err]} {
    puts "WARNING: Hardware server connection issue: \$err"
    puts "Proceeding anyway..."
}

# Try to open target with retry logic
set max_retries 3
set retry_count 0
set target_opened 0

while {\$retry_count < \$max_retries} {
    if {[catch {open_hw_target} err]} {
        puts "Attempt [expr {\$retry_count + 1}] failed: \$err"
        incr retry_count
        after 500
    } else {
        set target_opened 1
        break
    }
}

if {!\$target_opened} {
    puts "ERROR: Could not open hardware target after \$max_retries attempts"
    catch {close_hw_manager}
    exit 1
}

puts "Target opened successfully"

# Get device and program
if {[catch {set device [lindex [get_hw_devices] 0]} err]} {
    puts "ERROR: No FPGA devices found: \$err"
    catch {close_hw_target}
    catch {close_hw_manager}
    exit 1
}

puts "Programming device: \$device"
puts "Bitstream: $BITSTREAM_PATH"

# Set bitstream and program
if {[catch {set_property PROGRAM.FILE {$BITSTREAM_PATH} \$device} err]} {
    puts "ERROR: Failed to set bitstream: \$err"
    catch {close_hw_target}
    catch {close_hw_manager}
    exit 1
}

if {[catch {program_hw_device \$device} err]} {
    puts "ERROR: Failed to program device: \$err"
    catch {close_hw_target}
    catch {close_hw_manager}
    exit 1
}

puts "Device programmed successfully!"

# Cleanup
catch {close_hw_target}
catch {disconnect_hw_server}
catch {close_hw_manager}
puts "Done"
EOF

echo "Executing Vivado programming..."
echo ""

# Run Vivado with the TCL script
if vivado -mode batch -source "$PROG_TCL" 2>&1; then
    echo ""
    echo "=================================================="
    echo "✅ PROGRAMMING SUCCESSFUL!"
    echo "=================================================="
    echo ""
    echo "Next steps:"
    echo "  1. Check board LEDs (should show some activity)"
    echo "  2. Press BTNC (center button) to start simulation"
    echo "  3. Observe trail patterns on VGA display"
    echo ""
else
    echo ""
    echo "=================================================="
    echo "❌ PROGRAMMING FAILED"
    echo "=================================================="
    echo ""
    echo "Troubleshooting steps:"
    echo "  1. Check USB JTAG cable is connected"
    echo "  2. Verify Basys3 board is powered on"
    echo "  3. Try different USB port"
    echo "  4. Use Vivado GUI for manual programming:"
    echo "     vivado -mode gui"
    echo "     Hardware → Open Hardware Manager → Program Device"
    echo ""
    exit 1
fi
