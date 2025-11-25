# ============================================================================
# Vivado Project Generation Script - Production Grade
# Slime Simulator for Basys3 FPGA
#
# Usage:
#   cd /path/to/SlimeSimulator/rtl
#   vivado -mode batch -source generate_xpr.tcl
#
# Output:
#   ./vivado_project/slime_simulator.xpr
#   ./generate_xpr_report.txt
# ============================================================================

set script_start_time [clock seconds]
set project_name "slime_simulator"
set project_dir "./vivado_project"
set part "xc7a35tcpg236-1"
set board "digilentinc.com:basys3:part0:1.1"

puts "\n============================================================================"
puts "Slime Simulator - Vivado Project Generation"
puts "============================================================================"
puts "Project: $project_name"
puts "Part:    $part"
puts "Time:    [clock format $script_start_time -format {%Y-%m-%d %H:%M:%S}]"
puts "============================================================================\n"

# ============================================================================
# Step 1: Clean up old project if exists
# ============================================================================
puts "\[Step 1/7\] Cleaning up old project..."
if {[file exists $project_dir]} {
    puts "  Removing existing project directory: $project_dir"
    file delete -force $project_dir
    puts "  Done."
} else {
    puts "  No existing project found. Proceeding with fresh creation."
}

# ============================================================================
# Step 2: Create new Vivado project
# ============================================================================
puts "\n\[Step 2/7\] Creating new Vivado project..."
create_project $project_name $project_dir -part $part -force

# Try to set board if available
if {[catch {set_property board_part $board [current_project]} err]} {
    puts "  Warning: Basys3 board files not found. Using part only."
    puts "  (This is okay - constraints file will handle pin assignments)"
} else {
    puts "  Board part set: $board"
}

puts "  Project created successfully."

# ============================================================================
# Step 3: Add RTL source files in dependency order
# ============================================================================
puts "\n\[Step 3/7\] Adding RTL source files..."

set rtl_files [list \
    "src/debouncer.sv" \
    "src/lfsr.sv" \
    "src/fixed_point_mult.sv" \
    "src/trig_lut.sv" \
    "src/vga_controller.sv" \
    "src/agent_processor.sv" \
    "src/slime_top.sv" \
]

set files_added 0
set files_missing 0
set missing_files [list]

foreach file $rtl_files {
    if {[file exists $file]} {
        add_files -norecurse $file
        puts "  + Added: $file"
        incr files_added
    } else {
        puts "  ! Missing: $file"
        incr files_missing
        lappend missing_files $file
    }
}

# ============================================================================
# Step 4: Add memory initialization files (HEX files)
# ============================================================================
puts "\n\[Step 4/7\] Adding memory initialization files..."

set mem_files [list \
    "src/sin_lut.hex" \
    "src/cos_lut.hex" \
]

foreach file $mem_files {
    if {[file exists $file]} {
        add_files -norecurse $file
        puts "  + Added: $file"
        incr files_added
    } else {
        puts "  ! Missing: $file"
        incr files_missing
        lappend missing_files $file
    }
}

# ============================================================================
# Step 5: Add constraints
# ============================================================================
puts "\n\[Step 5/7\] Adding constraints file..."

set constraints_file "constraints/basys3.xdc"
if {[file exists $constraints_file]} {
    add_files -fileset constrs_1 -norecurse $constraints_file
    puts "  + Added: $constraints_file"
    incr files_added
} else {
    puts "  ! ERROR: Constraints file missing: $constraints_file"
    incr files_missing
    lappend missing_files $constraints_file
}

# ============================================================================
# Step 6: Configure project settings
# ============================================================================
puts "\n\[Step 6/7\] Configuring project settings..."

# Set top module
puts "  Setting top module: slime_top"
set_property top slime_top [current_fileset]

# Update compile order
puts "  Updating design hierarchy..."
update_compile_order -fileset sources_1

# Set SystemVerilog as the target language
set_property target_language Verilog [current_project]

# Configure synthesis strategy
puts "  Configuring synthesis strategy..."
set_property strategy "Flow_PerfOptimized_high" [get_runs synth_1]
set_property STEPS.SYNTH_DESIGN.ARGS.DIRECTIVE PerformanceOptimized [get_runs synth_1]
set_property STEPS.SYNTH_DESIGN.ARGS.FLATTEN_HIERARCHY rebuilt [get_runs synth_1]
set_property STEPS.SYNTH_DESIGN.ARGS.KEEP_EQUIVALENT_REGISTERS true [get_runs synth_1]
set_property STEPS.SYNTH_DESIGN.ARGS.RETIMING true [get_runs synth_1]

# Configure implementation strategy
puts "  Configuring implementation strategy..."
set_property strategy "Performance_ExploreWithRemap" [get_runs impl_1]
set_property STEPS.OPT_DESIGN.ARGS.DIRECTIVE ExploreWithRemap [get_runs impl_1]
set_property STEPS.PLACE_DESIGN.ARGS.DIRECTIVE ExtraNetDelay_high [get_runs impl_1]
set_property STEPS.PHYS_OPT_DESIGN.ARGS.DIRECTIVE AggressiveExplore [get_runs impl_1]
set_property STEPS.ROUTE_DESIGN.ARGS.DIRECTIVE AggressiveExplore [get_runs impl_1]

# Enable incremental compile
puts "  Enabling incremental compile..."
set_property AUTO_INCREMENTAL_CHECKPOINT 1 [get_runs synth_1]
set_property AUTO_INCREMENTAL_CHECKPOINT 1 [get_runs impl_1]

# Parallel jobs (use 4 cores)
set_property STEPS.SYNTH_DESIGN.ARGS.JOBS 4 [get_runs synth_1]
set_property STEPS.PLACE_DESIGN.ARGS.JOBS 4 [get_runs impl_1]
set_property STEPS.ROUTE_DESIGN.ARGS.JOBS 4 [get_runs impl_1]

# Bitstream generation settings
puts "  Configuring bitstream generation..."
set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design -quiet]
set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design -quiet]
set_property CONFIG_MODE SPIx4 [current_design -quiet]
set_property BITSTREAM.CONFIG.CONFIGRATE 50 [current_design -quiet]

puts "  Configuration complete."

# ============================================================================
# Step 7: Generate reports
# ============================================================================
puts "\n\[Step 7/7\] Generating project report..."

set report_file "generate_xpr_report.txt"
set fp [open $report_file w]

puts $fp "============================================================================"
puts $fp "Vivado Project Generation Report"
puts $fp "============================================================================"
puts $fp "Generated: [clock format [clock seconds] -format {%Y-%m-%d %H:%M:%S}]"
puts $fp ""
puts $fp "Project Information:"
puts $fp "  Name:      $project_name"
puts $fp "  Directory: [file normalize $project_dir]"
puts $fp "  Part:      $part"
puts $fp ""
puts $fp "File Summary:"
puts $fp "  Files added:   $files_added"
puts $fp "  Files missing: $files_missing"
puts $fp ""

if {$files_missing > 0} {
    puts $fp "Missing Files:"
    foreach file $missing_files {
        puts $fp "  ! $file"
    }
    puts $fp ""
}

puts $fp "RTL Sources:"
foreach file $rtl_files {
    if {[file exists $file]} {
        set fsize [file size $file]
        puts $fp "  [format %-40s $file] ([format %8d $fsize] bytes)"
    }
}
puts $fp ""

puts $fp "Memory Files:"
foreach file $mem_files {
    if {[file exists $file]} {
        set fsize [file size $file]
        puts $fp "  [format %-40s $file] ([format %8d $fsize] bytes)"
    }
}
puts $fp ""

puts $fp "Constraints:"
if {[file exists $constraints_file]} {
    set fsize [file size $constraints_file]
    puts $fp "  [format %-40s $constraints_file] ([format %8d $fsize] bytes)"
}
puts $fp ""

puts $fp "Design Hierarchy:"
puts $fp "  Top module: slime_top"
set hierarchy_report [report_compile_order -return_string]
puts $fp "$hierarchy_report"
puts $fp ""

puts $fp "Synthesis Strategy:"
puts $fp "  Strategy:  [get_property strategy [get_runs synth_1]]"
puts $fp "  Directive: [get_property STEPS.SYNTH_DESIGN.ARGS.DIRECTIVE [get_runs synth_1]]"
puts $fp ""

puts $fp "Implementation Strategy:"
puts $fp "  Strategy:          [get_property strategy [get_runs impl_1]]"
puts $fp "  Place directive:   [get_property STEPS.PLACE_DESIGN.ARGS.DIRECTIVE [get_runs impl_1]]"
puts $fp "  Route directive:   [get_property STEPS.ROUTE_DESIGN.ARGS.DIRECTIVE [get_runs impl_1]]"
puts $fp ""

puts $fp "Status:"
if {$files_missing > 0} {
    puts $fp "  ⚠ WARNING: $files_missing file(s) missing"
    puts $fp "  Project created but may not build successfully."
} else {
    puts $fp "  ✓ All source files present"
    puts $fp "  ✓ Project configured and ready for build"
}
puts $fp ""

set elapsed [expr {[clock seconds] - $script_start_time}]
puts $fp "Generation completed in $elapsed seconds."
puts $fp "============================================================================"

close $fp

puts "  Report written to: [file normalize $report_file]"

# ============================================================================
# Summary
# ============================================================================
set elapsed [expr {[clock seconds] - $script_start_time}]

puts "\n============================================================================"
puts "Project Generation Summary"
puts "============================================================================"
puts "  Status:            [expr {$files_missing > 0 ? "⚠ WITH WARNINGS" : "✓ SUCCESS"}]"
puts "  Files added:       $files_added"
puts "  Files missing:     $files_missing"
puts "  Project file:      [file normalize $project_dir/$project_name.xpr]"
puts "  Report file:       [file normalize $report_file]"
puts "  Generation time:   $elapsed seconds"
puts "============================================================================"

if {$files_missing > 0} {
    puts "\n⚠ WARNING: Project created but $files_missing file(s) are missing."
    puts "Please ensure all source files exist before building."
    puts ""
    exit 1
} else {
    puts "\n✓ Project ready for build!"
    puts "Next step: Run 'vivado -mode batch -source build.tcl'"
    puts ""
}
