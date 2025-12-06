# Vivado xsim testbench runner
# Usage: vivado -mode batch -source run_xsim.tcl

# Configuration
set PROJ_NAME slime_xsim
set SIM_WORKDIR ./xsim_work
set RTL_FILES {
    ../src/slime_top.sv
    ../src/agent_coordinator.sv
    ../src/agent_processor.sv
    ../src/lfsr.sv
    ../src/fixed_point_mult.sv
    ../src/trig_lut.sv
    ../src/vga_controller.sv
    ../src/debouncer.sv
}
set TB_FILES {
    slime_xsim_tb.sv
}
set TRIG_FILES {
    ../src/sin_lut.hex
    ../src/cos_lut.hex
}

# Create project
file delete -force $SIM_WORKDIR
create_project -force $PROJ_NAME $SIM_WORKDIR -part xc7a35tcpg236-1

# Add source files
foreach f $RTL_FILES {
    if {[file exists $f]} {
        add_files $f
    } else {
        puts "WARNING: File not found: $f"
    }
}

foreach f $TB_FILES {
    if {[file exists $f]} {
        add_files $f
        set_property file_type {SystemVerilog} [get_files $f]
    } else {
        puts "WARNING: File not found: $f"
    }
}

# Copy trig files to both work directory and simulation runtime directory
file mkdir $SIM_WORKDIR/$PROJ_NAME.srcs/sim_1/new
foreach f $TRIG_FILES {
    if {[file exists $f]} {
        file copy -force $f $SIM_WORKDIR/$PROJ_NAME.srcs/sim_1/new/
        # Also copy to current directory for xsim runtime
        file copy -force $f ./
    } else {
        puts "WARNING: Trig file not found: $f"
    }
}

# Set testbench as top
set_property top slime_xsim_tb [get_filesets sim_1]

# Compile
puts "Compiling design..."
update_compile_order -fileset sim_1

# Elaborate and run simulation
puts "Running simulation..."
launch_simulation -mode behavioral
run all

# Don't try to save VCD in batch mode - xsim output goes to log

puts "Simulation complete!"
puts "Check xsim_batch.log for simulation output"
