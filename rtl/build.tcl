# ============================================================================
# Vivado Build Script - Complete Synthesis → Implementation → Bitstream
# Slime Simulator for Basys3 FPGA
#
# Usage:
#   cd /path/to/SlimeSimulator/rtl
#   vivado -mode batch -source build.tcl
#
# Prerequisites:
#   - Project must exist (run generate_xpr.tcl first)
#   - OR provide PROJECT_FILE environment variable
#
# Output:
#   ./vivado_project/slime_simulator.runs/impl_1/slime_top.bit
#   ./build_report.txt (comprehensive build summary)
# ============================================================================

set script_start_time [clock seconds]

# ============================================================================
# Configuration
# ============================================================================
set project_name "slime_simulator"
set project_dir "./vivado_project"
set project_file "${project_dir}/${project_name}.xpr"
set top_module "slime_top"

# Check for custom project file
if {[info exists env(PROJECT_FILE)]} {
    set project_file $env(PROJECT_FILE)
    puts "Using custom project file: $project_file"
}

puts "\n============================================================================"
puts "Slime Simulator - Vivado Build Flow"
puts "============================================================================"
puts "Project:   $project_name"
puts "Top:       $top_module"
puts "Started:   [clock format $script_start_time -format {%Y-%m-%d %H:%M:%S}]"
puts "============================================================================\n"

# ============================================================================
# Step 1: Prerequisites Check
# ============================================================================
puts "\[Step 1/5\] Checking prerequisites..."

set prereq_failed 0
set missing_files [list]

# Check if project exists
if {![file exists $project_file]} {
    puts "  ✗ ERROR: Project file not found: $project_file"
    puts "    → Run 'vivado -mode batch -source generate_xpr.tcl' first"
    set prereq_failed 1
} else {
    puts "  ✓ Project file found: $project_file"
}

# Open project
if {!$prereq_failed} {
    puts "  Opening project..."
    open_project $project_file

    # Verify source files
    puts "  Checking source files..."
    set source_files [get_files -filter {USED_IN_SYNTHESIS == 1}]
    set file_count [llength $source_files]

    if {$file_count == 0} {
        puts "  ✗ ERROR: No source files found in project"
        set prereq_failed 1
    } else {
        puts "  ✓ Found $file_count source file(s)"
    }

    # Check for missing files
    foreach file $source_files {
        set file_path [get_property NAME $file]
        if {![file exists $file_path]} {
            puts "  ✗ Missing: $file_path"
            lappend missing_files $file_path
            set prereq_failed 1
        }
    }

    # Verify constraints
    set constraint_files [get_files -of_objects [get_filesets constrs_1]]
    if {[llength $constraint_files] == 0} {
        puts "  ⚠ WARNING: No constraints file found"
    } else {
        puts "  ✓ Constraints file(s) present"
    }
}

if {$prereq_failed} {
    puts "\n✗ Prerequisites check failed. Cannot proceed with build."
    if {[llength $missing_files] > 0} {
        puts "\nMissing files:"
        foreach file $missing_files {
            puts "  - $file"
        }
    }
    exit 1
}

puts "  ✓ All prerequisites satisfied\n"

# ============================================================================
# Step 2: Synthesis
# ============================================================================
puts "\[Step 2/5\] Running synthesis..."
set synth_start_time [clock seconds]

# Reset synthesis run if needed
reset_run synth_1

# Launch synthesis
puts "  Launching synthesis (using 4 parallel jobs)..."
if {[catch {
    launch_runs synth_1 -jobs 4
    wait_on_run synth_1
} err]} {
    puts "  ✗ ERROR: Synthesis launch failed: $err"
    exit 1
}

# Check synthesis result
set synth_status [get_property STATUS [get_runs synth_1]]
set synth_progress [get_property PROGRESS [get_runs synth_1]]

puts "  Synthesis status: $synth_status"
puts "  Progress: $synth_progress"

if {$synth_progress != "100%"} {
    puts "  ✗ ERROR: Synthesis did not complete successfully"
    puts "    Check: ${project_dir}/${project_name}.runs/synth_1/runme.log"
    exit 1
}

# Open synthesized design for reports
open_run synth_1

# Generate synthesis reports
puts "  Generating synthesis reports..."
set synth_util_file "${project_dir}/${project_name}.runs/synth_1/${top_module}_utilization_synth.txt"
set synth_timing_file "${project_dir}/${project_name}.runs/synth_1/${top_module}_timing_summary_synth.txt"

report_utilization -file $synth_util_file
report_timing_summary -max_paths 10 -file $synth_timing_file

# Extract key synthesis metrics
set synth_luts [get_property SLICE_LUTS [get_cells -hierarchical]]
set synth_ffs [get_property SLICE_REGISTERS [get_cells -hierarchical]]

puts "  Resource usage (post-synthesis):"
puts "    LUTs: [llength $synth_luts]"
puts "    FFs:  [llength $synth_ffs]"

# Check for critical warnings
set synth_warnings [get_msg_config -count -severity WARNING -id *]
set synth_critical [get_msg_config -count -severity {CRITICAL WARNING} -id *]

if {$synth_critical > 0} {
    puts "  ⚠ Found $synth_critical critical warning(s)"
}

set synth_elapsed [expr {[clock seconds] - $synth_start_time}]
puts "  ✓ Synthesis completed in $synth_elapsed seconds\n"

# ============================================================================
# Step 3: Implementation
# ============================================================================
puts "\[Step 3/5\] Running implementation..."
set impl_start_time [clock seconds]

# Reset implementation run if needed
reset_run impl_1

# Launch implementation
puts "  Launching implementation (using 4 parallel jobs)..."
if {[catch {
    launch_runs impl_1 -jobs 4
    wait_on_run impl_1
} err]} {
    puts "  ✗ ERROR: Implementation launch failed: $err"
    exit 1
}

# Check implementation result
set impl_status [get_property STATUS [get_runs impl_1]]
set impl_progress [get_property PROGRESS [get_runs impl_1]]

puts "  Implementation status: $impl_status"
puts "  Progress: $impl_progress"

if {$impl_progress != "100%"} {
    puts "  ✗ ERROR: Implementation did not complete successfully"
    puts "    Check: ${project_dir}/${project_name}.runs/impl_1/runme.log"
    exit 1
}

# Open implemented design for reports
open_run impl_1

# Generate implementation reports
puts "  Generating implementation reports..."
set impl_util_file "${project_dir}/${project_name}.runs/impl_1/${top_module}_utilization_placed.txt"
set impl_timing_file "${project_dir}/${project_name}.runs/impl_1/${top_module}_timing_summary_routed.txt"
set impl_power_file "${project_dir}/${project_name}.runs/impl_1/${top_module}_power_routed.txt"

report_utilization -file $impl_util_file
report_timing_summary -max_paths 10 -file $impl_timing_file
report_power -file $impl_power_file

# Extract timing metrics
set wns [get_property SLACK [get_timing_paths -max_paths 1 -nworst 1 -setup]]
set whs [get_property SLACK [get_timing_paths -max_paths 1 -nworst 1 -hold]]

puts "  Timing results:"
puts "    Setup WNS: $wns ns"
puts "    Hold WHS:  $whs ns"

if {$wns < 0} {
    puts "  ⚠ WARNING: Setup timing not met (WNS = $wns ns)"
    puts "    Design may not work reliably at target frequency"
    set timing_met 0
} else {
    puts "  ✓ Timing constraints met"
    set timing_met 1
}

# Extract final resource utilization
set impl_util_report [report_utilization -return_string]

# Parse utilization (this is approximate - actual parsing may vary)
if {[regexp {Slice LUTs[^\d]+(\d+)} $impl_util_report match lut_count]} {
    puts "  Final LUT usage: $lut_count"
} else {
    puts "  Could not extract LUT count"
}

set impl_elapsed [expr {[clock seconds] - $impl_start_time}]
puts "  ✓ Implementation completed in $impl_elapsed seconds\n"

# ============================================================================
# Step 4: Bitstream Generation
# ============================================================================
puts "\[Step 4/5\] Generating bitstream..."
set bitstream_start_time [clock seconds]

# Launch bitstream generation
puts "  Writing bitstream (with compression)..."
if {[catch {
    launch_runs impl_1 -to_step write_bitstream -jobs 4
    wait_on_run impl_1
} err]} {
    puts "  ✗ ERROR: Bitstream generation failed: $err"
    exit 1
}

# Check for bitstream file
set bitstream_file "${project_dir}/${project_name}.runs/impl_1/${top_module}.bit"

if {[file exists $bitstream_file]} {
    set bit_size [file size $bitstream_file]
    puts "  ✓ Bitstream generated: $bitstream_file"
    puts "    Size: [expr {$bit_size / 1024}] KB"
} else {
    puts "  ✗ ERROR: Bitstream file not found at expected location"
    exit 1
}

set bitstream_elapsed [expr {[clock seconds] - $bitstream_start_time}]
puts "  ✓ Bitstream generation completed in $bitstream_elapsed seconds\n"

# ============================================================================
# Step 5: Generate Build Report
# ============================================================================
puts "\[Step 5/5\] Generating build report..."

set report_file "build_report.txt"
set fp [open $report_file w]

puts $fp "============================================================================"
puts $fp "Vivado Build Report"
puts $fp "============================================================================"
puts $fp "Project:    $project_name"
puts $fp "Top module: $top_module"
puts $fp "Built:      [clock format [clock seconds] -format {%Y-%m-%d %H:%M:%S}]"
puts $fp ""
puts $fp "============================================================================"
puts $fp "Build Timeline"
puts $fp "============================================================================"
puts $fp "  Synthesis:      $synth_elapsed seconds"
puts $fp "  Implementation: $impl_elapsed seconds"
puts $fp "  Bitstream:      $bitstream_elapsed seconds"
puts $fp "  Total:          [expr {[clock seconds] - $script_start_time}] seconds"
puts $fp ""
puts $fp "============================================================================"
puts $fp "Timing Summary"
puts $fp "============================================================================"
puts $fp "  Setup WNS: $wns ns"
puts $fp "  Hold WHS:  $whs ns"
puts $fp "  Status:    [expr {$timing_met ? "✓ TIMING MET" : "✗ TIMING FAILED"}]"
puts $fp ""

# Include utilization summary
puts $fp "============================================================================"
puts $fp "Resource Utilization"
puts $fp "============================================================================"
puts $fp [report_utilization -return_string]
puts $fp ""

# Include timing paths
puts $fp "============================================================================"
puts $fp "Critical Paths (Top 10)"
puts $fp "============================================================================"
puts $fp [report_timing_summary -return_string -max_paths 10]
puts $fp ""

puts $fp "============================================================================"
puts $fp "Output Files"
puts $fp "============================================================================"
puts $fp "  Bitstream:    [file normalize $bitstream_file]"
puts $fp "  Utilization:  [file normalize $impl_util_file]"
puts $fp "  Timing:       [file normalize $impl_timing_file]"
puts $fp "  Power:        [file normalize $impl_power_file]"
puts $fp ""

puts $fp "============================================================================"
puts $fp "Build Status"
puts $fp "============================================================================"
if {!$timing_met} {
    puts $fp "  Status: ⚠ COMPLETED WITH TIMING WARNINGS"
    puts $fp ""
    puts $fp "  WARNING: Setup timing not met (WNS = $wns ns)"
    puts $fp "  The design may not operate reliably at the target frequency."
    puts $fp "  Consider:"
    puts $fp "    - Reducing clock frequency"
    puts $fp "    - Adding pipeline stages"
    puts $fp "    - Optimizing critical paths"
} else {
    puts $fp "  Status: ✓ BUILD SUCCESSFUL"
    puts $fp ""
    puts $fp "  All timing constraints met."
    puts $fp "  Bitstream ready for FPGA programming."
}
puts $fp "============================================================================"

close $fp

puts "  Report written to: [file normalize $report_file]"

# ============================================================================
# Final Summary
# ============================================================================
set total_elapsed [expr {[clock seconds] - $script_start_time}]

puts "\n============================================================================"
puts "Build Summary"
puts "============================================================================"
puts "  Status:        [expr {$timing_met ? "✓ SUCCESS" : "⚠ SUCCESS WITH WARNINGS"}]"
puts "  Timing:        [expr {$timing_met ? "✓ MET" : "✗ FAILED"}] (WNS: $wns ns)"
puts "  Bitstream:     [file normalize $bitstream_file]"
puts "  Report:        [file normalize $report_file]"
puts "  Build time:    $total_elapsed seconds ([expr {$total_elapsed / 60}] minutes)"
puts "============================================================================"

if {!$timing_met} {
    puts "\n⚠ WARNING: Timing constraints not met!"
    puts "Design may not operate reliably. Review timing reports."
} else {
    puts "\n✓ Build successful! Bitstream ready for programming."
    puts "Program FPGA with: vivado -mode batch -source program_fpga.tcl"
}
puts ""

# Return timing status as exit code (0 = success, 1 = timing failed)
# Note: We still exit 0 even with timing warnings, as build completed
exit 0
