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

# PRE-COPY trig files to multiple locations BEFORE compilation
# This is critical because $readmemh happens at elaboration time
# xelab will look in:
# 1. Current working directory (where Vivado runs from)
# 2. Same directory as source files
# 3. xsim_work subdirectories
puts "Pre-copying trig files to all search locations..."
foreach f $TRIG_FILES {
    set abs_f [file normalize $f]
    set fname [file tail $f]

    # Copy to current directory (Vivado execution dir)
    catch {file copy -force $abs_f ./}
    puts "  Copied $fname to ./"

    # Copy to xsim_work (will be created by create_project)
    catch {file copy -force $abs_f $SIM_WORKDIR/}
    puts "  Copied $fname to $SIM_WORKDIR/"

    # Copy to source directory (xelab may look here)
    catch {file copy -force $abs_f [file dirname [lindex $RTL_FILES 0]]/}
    puts "  Copied $fname to RTL source directory"
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

# Create a small TCL script to set up environment and run with absolute paths
set RUN_SCRIPT "$SIM_WORKDIR/$PROJ_NAME.sim/sim_1/behav/xsim/run_with_paths.tcl"
catch {file mkdir [file dirname $RUN_SCRIPT]}

set fp [open $RUN_SCRIPT w]
puts $fp "# Auto-generated simulation script with absolute paths"

# Get absolute paths for hex files
foreach f $TRIG_FILES {
    set abs_f [file normalize $f]
    puts $fp "# Hex file: [file tail $abs_f] -> $abs_f"
}

# Change to xsim directory and run
puts $fp "cd [file dirname $RUN_SCRIPT]"
puts $fp "run all"
close $fp

puts "Running simulation with trig files in xsim runtime directory..."
run all

# Don't try to save VCD in batch mode - xsim output goes to log

puts "Simulation complete!"
puts "Check xsim_batch.log for simulation output"
