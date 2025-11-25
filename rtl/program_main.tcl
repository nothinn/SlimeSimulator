open_hw_manager
connect_hw_server -allow_non_jtag

set targets [get_hw_targets]
if {[llength $targets] > 0} {
    set target [lindex $targets 0]
    puts "Opening target: $target"
    open_hw_target $target
    
    set devices [get_hw_devices]
    if {[llength $devices] > 0} {
        set device [lindex $devices 0]
        puts "Programming main slime simulator with agent processor..."
        
        set_property PROGRAM.FILE {./vivado_project/slime_simulator.runs/impl_1/slime_top.bit} $device
        program_hw_devices $device
        puts "SUCCESS: Main simulator programmed!"
        
        after 1000
    }
    close_hw_target
}

close_hw_manager
