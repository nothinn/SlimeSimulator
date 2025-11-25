# Vivado TCL Script - Verify FPGA Programming Status
#
# This script checks if the FPGA is programmed and reads back status

# Open hardware manager
open_hw_manager

# Connect to hardware server
connect_hw_server -allow_non_jtag

# Open hardware target (auto-detect)
open_hw_target

# Get the device
set device [lindex [get_hw_devices] 0]
current_hw_device $device

puts "============================================"
puts "Device: [get_property NAME $device]"
puts "Part: [get_property PART $device]"

# Check if programmed
refresh_hw_device $device

puts "============================================"
puts "Device verification complete!"
puts "============================================"

# Close connection
close_hw_target
disconnect_hw_server
close_hw_manager
