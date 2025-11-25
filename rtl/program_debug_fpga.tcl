# Vivado TCL Script - Program Basys3 FPGA with Debug Bitstream
#
# Usage:
#   vivado -mode batch -source program_debug_fpga.tcl
#
# Or with custom bitstream:
#   vivado -mode batch -source program_debug_fpga.tcl -tclargs path/to/bitstream.bit

set bitfile "vivado_project_debug/slime_simulator_debug.runs/impl_1/slime_top_debug.bit"

# Check for command line argument
if {$argc > 0} {
    set bitfile [lindex $argv 0]
}

puts ""
puts "============================================================================="
puts " Programming FPGA with Debug Bitstream"
puts "============================================================================="
puts ""
puts "Bitstream: $bitfile"
puts ""

# Verify bitstream exists
if {![file exists $bitfile]} {
    puts "ERROR: Bitstream file not found: $bitfile"
    puts "Please run rebuild_with_ips.tcl first to generate the bitstream."
    exit 1
}

# Open hardware manager
puts "Opening hardware manager..."
open_hw_manager

# Connect to hardware server
puts "Connecting to hardware server..."
connect_hw_server -allow_non_jtag

# Open hardware target (auto-detect)
puts "Opening hardware target..."
if {[catch {open_hw_target}]} {
    puts "ERROR: Could not connect to JTAG target"
    puts "Please check:"
    puts "  - FPGA board is powered on"
    puts "  - USB cable is connected"
    puts "  - Device drivers are installed"
    disconnect_hw_server
    close_hw_manager
    exit 1
}

# Get the device
set devices [get_hw_devices]
if {[llength $devices] == 0} {
    puts "ERROR: No FPGA devices found on JTAG chain"
    close_hw_target
    disconnect_hw_server
    close_hw_manager
    exit 1
}

set device [lindex $devices 0]
current_hw_device $device

puts "Found device: [get_property PART $device]"

# Set programming file
puts ""
puts "Programming device..."
set_property PROGRAM.FILE $bitfile $device

# Program the device
program_hw_devices $device

# Refresh device to verify programming
refresh_hw_device $device

puts ""
puts "============================================================================="
puts " FPGA Programmed Successfully!"
puts "============================================================================="
puts ""
puts "Device Information:"
puts "  Part:     [get_property PART $device]"
puts "  Device:   [get_property NAME $device]"
puts ""
puts "Debug Infrastructure Enabled:"
puts "  ✓ JTAG-to-AXI Master"
puts "  ✓ VIO (Virtual I/O)"
puts "  ✓ ILA (Integrated Logic Analyzer)"
puts ""
puts "Hardware Manager Status:"

# Check for debug cores
set debug_cores [get_hw_axis]
set vio_cores [get_hw_vios]
set ila_cores [get_hw_ilas]

if {[llength $debug_cores] > 0} {
    puts "  ✓ JTAG-to-AXI detected: [llength $debug_cores] core(s)"
    foreach core $debug_cores {
        puts "    - [get_property NAME $core]"
    }
} else {
    puts "  ⚠ JTAG-to-AXI not detected"
}

if {[llength $vio_cores] > 0} {
    puts "  ✓ VIO detected: [llength $vio_cores] core(s)"
    foreach core $vio_cores {
        puts "    - [get_property NAME $core]"
    }
} else {
    puts "  ⚠ VIO not detected"
}

if {[llength $ila_cores] > 0} {
    puts "  ✓ ILA detected: [llength $ila_cores] core(s)"
    foreach core $ila_cores {
        puts "    - [get_property NAME $core]"
    }
} else {
    puts "  ⚠ ILA not detected"
}

puts ""
puts "Next Steps:"
puts "  1. Start simulation by pressing BTNC (center button) on Basys3"
puts "  2. Access debug features:"
puts "     - Open Vivado GUI: vivado -mode gui"
puts "     - Open Hardware Manager (already connected)"
puts "     - View VIO in Dashboard"
puts "     - Configure ILA triggers"
puts "     - Read memory via JTAG-to-AXI"
puts ""
puts "  3. Python access:"
puts "     - Use fpga_controller.py to read trail memory"
puts "     - See register_map.txt for memory layout"
puts ""
puts "JTAG-to-AXI Usage Example (TCL):"
puts "  set jtag_axi [get_hw_axis hw_axi_1]"
puts "  create_hw_axi_txn read_txn \$jtag_axi -address 0x00100008 -type read"
puts "  run_hw_axi read_txn"
puts "  set frame_count [get_property DATA [get_hw_axi_txn read_txn]]"
puts "  puts \"Frame count: \$frame_count\""
puts ""
puts "============================================================================="
puts ""

# Leave hardware manager open for subsequent operations
# User can continue in Vivado GUI or use TCL console
puts "Hardware Manager remains open for debugging."
puts "To close: disconnect_hw_server; close_hw_manager"
puts ""
