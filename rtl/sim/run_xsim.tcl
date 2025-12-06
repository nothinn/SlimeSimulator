# Vivado xsim testbench runner
# Usage: vivado -mode batch -source run_xsim.tcl

# Configuration
set PROJ_NAME slime_xsim
set SIM_WORKDIR ./xsim_work

# Get current directory and construct absolute paths
set SCRIPT_DIR [file dirname [info script]]
set BASE_DIR [file normalize [file join $SCRIPT_DIR ..]]
set RTL_SRC_DIR [file normalize [file join $BASE_DIR src]]

# Absolute paths for all files
set RTL_FILES [list \
    [file join $RTL_SRC_DIR slime_top.sv] \
    [file join $RTL_SRC_DIR agent_coordinator.sv] \
    [file join $RTL_SRC_DIR agent_processor.sv] \
    [file join $RTL_SRC_DIR lfsr.sv] \
    [file join $RTL_SRC_DIR fixed_point_mult.sv] \
    [file join $RTL_SRC_DIR trig_lut.sv] \
    [file join $RTL_SRC_DIR vga_controller.sv] \
    [file join $RTL_SRC_DIR debouncer.sv] \
]

set TB_FILES [list \
    [file join $SCRIPT_DIR slime_xsim_tb.sv] \
]

set TRIG_FILES [list \
    [file join $RTL_SRC_DIR sin_lut.hex] \
    [file join $RTL_SRC_DIR cos_lut.hex] \
]

puts "Script directory: $SCRIPT_DIR"
puts "RTL source directory: $RTL_SRC_DIR"
puts "Trig files: $TRIG_FILES"

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

# PRE-COPY trig files to work directory BEFORE compilation
# This is critical because $readmemh happens at elaboration time
puts "Pre-copying trig files..."
foreach f $TRIG_FILES {
    set abs_f [file normalize $f]
    catch {file copy -force $abs_f ./}
    catch {file copy -force $abs_f $SIM_WORKDIR/}
    puts "Pre-copied [file tail $abs_f]"
}

# Compile
puts "Compiling design..."
update_compile_order -fileset sim_1

# Elaborate and run simulation
puts "Running simulation..."

# Create simulation subdirectory structure and copy files there too
set XSIM_WORK "$SIM_WORKDIR/$PROJ_NAME.sim/sim_1/behav/xsim"
after 100  ;# Small delay to let files be written

# Also copy to the simulation directory where xsim will execute from
if {[catch {file mkdir $XSIM_WORK}]} {
    puts "Note: xsim directory not yet created (will be created by launch_simulation)"
}

# Launch simulation
launch_simulation -mode behavioral

# Post-copy to xsim runtime directories after simulation is launched
puts "Post-copying trig files to xsim runtime..."
foreach f $TRIG_FILES {
    set abs_f [file normalize $f]

    # Try multiple locations
    catch {file copy -force $abs_f "$SIM_WORKDIR/$PROJ_NAME.sim/sim_1/behav/xsim/"}
    catch {file copy -force $abs_f "$SIM_WORKDIR/$PROJ_NAME.sim/sim_1/behav/"}
    catch {file copy -force $abs_f "./"}

    puts "Post-copied [file tail $abs_f]"
}

puts "Running simulation..."
run all

# Don't try to save VCD in batch mode - xsim output goes to log

puts "Simulation complete!"
puts "Check xsim_batch.log for simulation output"
