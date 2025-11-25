open_hw_manager
connect_hw_server -allow_non_jtag

set targets [get_hw_targets]
if {[llength $targets] > 0} {
    set target [lindex $targets 0]
    open_hw_target $target
    
    set devices [get_hw_devices]
    if {[llength $devices] > 0} {
        set device [lindex $devices 0]
        puts "Device: $device"
        
        # Check programming status
        set startup [get_property STARTUP_STATUS $device]
        puts "STARTUP_STATUS: $startup"
        
        # Get device properties
        set props [list_property $device]
        foreach prop $props {
            if {[string match "*STATUS*" $prop] || [string match "*CONFIG*" $prop]} {
                set val [get_property $prop $device]
                puts "$prop: $val"
            }
        }
    }
    close_hw_target
}

close_hw_manager
