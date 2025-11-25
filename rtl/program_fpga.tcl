# Vivado TCL Script - Program Basys3 FPGA
#
# Usage:
#   vivado -mode batch -source program_fpga.tcl
#
# Or from command line with hardware manager:
#   vivado -mode batch -source program_fpga.tcl -tclargs path/to/bitstream.bit

set bitfile "vivado_project/slime_simulator.runs/impl_1/slime_top.bit"

# Check for command line argument
if {$argc > 0} {
    set bitfile [lindex $argv 0]
}

puts "Programming FPGA with: $bitfile"

# Open hardware manager
open_hw_manager

# Connect to hardware server
connect_hw_server -allow_non_jtag

# Open hardware target (auto-detect)
open_hw_target

# Get the device
set device [lindex [get_hw_devices] 0]
current_hw_device $device

# Set programming file
set_property PROGRAM.FILE $bitfile $device

# Program the device
program_hw_devices $device

puts "============================================"
puts "FPGA programmed successfully!"
puts "============================================"

# Close connection
close_hw_target
disconnect_hw_server
close_hw_manager
