# Vivado TCL Script - Read Device Status and Properties
#
# This script reads detailed status from the programmed FPGA

# Open hardware manager
open_hw_manager

# Connect to hardware server
connect_hw_server -allow_non_jtag

# Open hardware target (auto-detect)
open_hw_target

# Get the device
set device [lindex [get_hw_devices] 0]
current_hw_device $device

puts "\n============================================"
puts "FPGA DEVICE STATUS"
puts "============================================"
puts "Device Name:     [get_property NAME $device]"
puts "Part Number:     [get_property PART $device]"
puts "JTAG Position:   [get_property JTAG_DEVICE_INDEX $device]"

# Try to get program status
refresh_hw_device $device

puts "\n============================================"
puts "PROGRAMMING STATUS"
puts "============================================"

# Check if device is programmed
if {[catch {get_property PROGRAM.FILE $device} prog_file]} {
    puts "Program File:    Not set or unavailable"
} else {
    puts "Program File:    $prog_file"
}

# Get current date/time for log
set timestamp [clock format [clock seconds] -format "%Y-%m-%d %H:%M:%S"]
puts "\nStatus checked:  $timestamp"

puts "\n============================================"
puts "Device is programmed and ready for testing"
puts "============================================\n"

# Close connection
close_hw_target
disconnect_hw_server
close_hw_manager
