# =============================================================================
# Rebuild Slime Simulator with Debug IPs
# =============================================================================
#
# Purpose: Complete build flow for debug-enabled design
# Assumes: IPs already created (run add_ip_cores.tcl first)
#
# Usage:
#   vivado -mode batch -source rebuild_with_ips.tcl
#
# =============================================================================

set project_name "slime_simulator_debug"
set project_dir "./vivado_project_debug"
set part "xc7a35tcpg236-1"

puts ""
puts "============================================================================="
puts " Rebuilding Slime Simulator with Debug IPs"
puts "============================================================================="
puts ""

# Check if project exists
if {![file exists "${project_dir}/${project_name}.xpr"]} {
    puts "ERROR: Project not found at ${project_dir}/${project_name}.xpr"
    puts "Please run add_ip_cores.tcl first to create the project."
    exit 1
}

# Open existing project
puts "Opening project: ${project_name}"
open_project "${project_dir}/${project_name}.xpr"

# Verify IPs exist
puts ""
puts "Verifying debug IPs..."
set required_ips {debug_jtag_axi debug_vio debug_ila}
set missing_ips {}

foreach ip $required_ips {
    if {[catch {get_ips $ip}]} {
        lappend missing_ips $ip
        puts "  ✗ Missing: $ip"
    } else {
        puts "  ✓ Found: $ip"
    }
}

if {[llength $missing_ips] > 0} {
    puts ""
    puts "ERROR: Missing IP cores: $missing_ips"
    puts "Please run add_ip_cores.tcl first to create the IPs."
    exit 1
}

# Update IP if needed
puts ""
puts "Updating IP cores..."
foreach ip [get_ips] {
    if {[catch {upgrade_ip $ip}]} {
        puts "  $ip: up to date"
    } else {
        puts "  $ip: upgraded"
    }
}

# Generate IP synthesis products if not already done
puts ""
puts "Generating IP synthesis products..."
foreach ip [get_ips] {
    if {![file exists "[get_property IP_DIR [get_ips $ip]]/[get_property NAME [get_ips $ip]].dcp"]} {
        puts "  Generating: $ip"
        generate_target all [get_ips $ip]
        create_ip_run [get_ips $ip]
        launch_runs ${ip}_synth_1 -jobs 4
    } else {
        puts "  Already generated: $ip"
    }
}

# Wait for IP synthesis
foreach ip [get_ips] {
    if {[get_runs -quiet ${ip}_synth_1] != ""} {
        puts "Waiting for ${ip} synthesis..."
        wait_on_run ${ip}_synth_1
    }
}

# Update compile order
puts ""
puts "Updating compile order..."
update_compile_order -fileset sources_1

# Reset runs to ensure clean build
puts ""
puts "Resetting synthesis and implementation runs..."
reset_run synth_1
reset_run impl_1

# =============================================================================
# Synthesis
# =============================================================================
puts ""
puts "============================================================================="
puts " Running Synthesis"
puts "============================================================================="
puts ""

set synth_start_time [clock seconds]
launch_runs synth_1 -jobs 4
wait_on_run synth_1

# Check synthesis result
if {[get_property PROGRESS [get_runs synth_1]] != "100%"} {
    puts ""
    puts "ERROR: Synthesis failed!"
    puts "Check reports in: ${project_dir}/${project_name}.runs/synth_1/"
    exit 1
}

set synth_end_time [clock seconds]
set synth_duration [expr $synth_end_time - $synth_start_time]

puts ""
puts "✓ Synthesis completed successfully in ${synth_duration} seconds"

# Open synthesis run and report utilization
open_run synth_1
puts ""
puts "Post-Synthesis Utilization:"
puts "─────────────────────────────────────────────────────────────────"
report_utilization -hierarchical -hierarchical_depth 1

# =============================================================================
# Implementation
# =============================================================================
puts ""
puts "============================================================================="
puts " Running Implementation"
puts "============================================================================="
puts ""

set impl_start_time [clock seconds]
launch_runs impl_1 -jobs 4
wait_on_run impl_1

# Check implementation result
if {[get_property PROGRESS [get_runs impl_1]] != "100%"} {
    puts ""
    puts "ERROR: Implementation failed!"
    puts "Check reports in: ${project_dir}/${project_name}.runs/impl_1/"
    exit 1
}

set impl_end_time [clock seconds]
set impl_duration [expr $impl_end_time - $impl_start_time]

puts ""
puts "✓ Implementation completed successfully in ${impl_duration} seconds"

# =============================================================================
# Bitstream Generation
# =============================================================================
puts ""
puts "============================================================================="
puts " Generating Bitstream"
puts "============================================================================="
puts ""

set bitstream_start_time [clock seconds]
launch_runs impl_1 -to_step write_bitstream -jobs 4
wait_on_run impl_1

set bitstream_end_time [clock seconds]
set bitstream_duration [expr $bitstream_end_time - $bitstream_start_time]

puts ""
puts "✓ Bitstream generated successfully in ${bitstream_duration} seconds"

# =============================================================================
# Reports
# =============================================================================
puts ""
puts "============================================================================="
puts " Generating Reports"
puts "============================================================================="
puts ""

open_run impl_1

# Create reports directory
file mkdir "${project_dir}/reports"

# Utilization report
puts "Generating utilization report..."
report_utilization -file ${project_dir}/reports/utilization.txt
report_utilization -hierarchical -hierarchical_depth 2 -file ${project_dir}/reports/utilization_hierarchical.txt

# Timing report
puts "Generating timing report..."
report_timing_summary -file ${project_dir}/reports/timing_summary.txt
report_timing -sort_by slack -max_paths 10 -file ${project_dir}/reports/timing_detail.txt

# Power report
puts "Generating power report..."
report_power -file ${project_dir}/reports/power.txt

# Clock report
puts "Generating clock report..."
report_clocks -file ${project_dir}/reports/clocks.txt

# DRC report
puts "Generating DRC report..."
report_drc -file ${project_dir}/reports/drc.txt

puts "✓ Reports generated in ${project_dir}/reports/"

# =============================================================================
# Summary
# =============================================================================
set total_time [expr $bitstream_end_time - $synth_start_time]
set minutes [expr $total_time / 60]
set seconds [expr $total_time % 60]

puts ""
puts "============================================================================="
puts " Build Complete!"
puts "============================================================================="
puts ""
puts "Build Summary:"
puts "  Synthesis Time:     ${synth_duration}s"
puts "  Implementation Time: ${impl_duration}s"
puts "  Bitstream Time:     ${bitstream_duration}s"
puts "  Total Time:         ${minutes}m ${seconds}s"
puts ""
puts "Output Files:"
puts "  Bitstream:          ${project_dir}/${project_name}.runs/impl_1/slime_top_debug.bit"
puts "  Utilization Report: ${project_dir}/reports/utilization.txt"
puts "  Timing Report:      ${project_dir}/reports/timing_summary.txt"
puts "  Power Report:       ${project_dir}/reports/power.txt"
puts ""

# Check timing
set wns [get_property STATS.WNS [get_runs impl_1]]
set whs [get_property STATS.WHS [get_runs impl_1]]

puts "Timing Summary:"
puts "  Worst Negative Slack (WNS): $wns ns"
puts "  Worst Hold Slack (WHS):     $whs ns"
puts ""

if {$wns < 0} {
    puts "⚠ WARNING: Timing constraints not met (negative WNS)"
    puts "  Design may not operate reliably at 100 MHz"
    puts "  Consider reducing clock frequency or optimizing critical paths"
} else {
    puts "✓ Timing constraints met"
}

puts ""
puts "Debug Infrastructure:"
puts "  JTAG-to-AXI:        Enabled (access trail memory via JTAG)"
puts "  VIO:                Enabled (control simulation from Hardware Manager)"
puts "  ILA:                Enabled (capture waveforms at 100 MHz)"
puts ""
puts "Memory Map:"
puts "  Trail Memory:       0x0000_0000 - 0x0004_AFFF (307200 bytes)"
puts "  Control Register:   0x0010_0000"
puts "  Status Register:    0x0010_0004"
puts "  Frame Count:        0x0010_0008"
puts ""
puts "Next Steps:"
puts "  1. Program FPGA:    vivado -mode batch -source program_fpga.tcl"
puts "  2. Open HW Manager: vivado -mode gui"
puts "     - Auto Connect to FPGA"
puts "     - Access VIO and ILA in Dashboard"
puts "     - Use JTAG-to-AXI for memory readout"
puts ""
puts "Documentation:"
puts "  - register_map.txt:          Register definitions"
puts "  - ip_integration_report.txt: Integration details"
puts "  - README.md:                 Project overview"
puts ""
puts "============================================================================="
puts ""

# Close project
close_project
