# Vivado TCL Build Script with Integrated Debug Cores
# Target: Basys3 (Artix-7 XC7A35T-1CPG236C)
#
# This build script creates a production bitstream with permanent debug
# infrastructure integrated. The debug cores (ILA, VIO, JTAG-to-AXI) are
# always present and accessible via Vivado Hardware Manager.
#
# Usage:
#   cd /home/reson/SlimeSimulator
#   vivado -mode batch -source rtl/build_with_debug.tcl
#
# Output:
#   vivado_project_debug/slime_simulator_debug.runs/impl_1/slime_top.bit

set project_name "slime_simulator_debug"
set project_dir "./vivado_project_debug"
set part "xc7a35tcpg236-1"

puts "============================================"
puts "Slime Simulator - Debug Build"
puts "============================================"
puts "Project: $project_name"
puts "Target: Basys3 (Artix-7)"
puts "Debug: ILA + VIO + JTAG-to-AXI enabled"
puts "============================================"

# ============================================================================
# Create Project
# ============================================================================
puts "\n[1/7] Creating Vivado project..."

create_project $project_name $project_dir -part $part -force

# ============================================================================
# Add RTL Source Files
# ============================================================================
puts "\n[2/7] Adding RTL source files..."

add_files -norecurse {
    rtl/src/slime_top.sv
    rtl/src/vga_controller.sv
    rtl/src/lfsr.sv
    rtl/src/fixed_point_mult.sv
    rtl/src/trig_lut.sv
    rtl/src/debouncer.sv
    rtl/src/agent_processor.sv
}

# Add hex files for trig LUT
add_files -norecurse {
    rtl/src/sin_lut.hex
    rtl/src/cos_lut.hex
}

puts "  Added 7 SystemVerilog modules"
puts "  Added 2 hex initialization files"

# ============================================================================
# Add Constraints
# ============================================================================
puts "\n[3/7] Adding constraints..."

add_files -fileset constrs_1 -norecurse rtl/constraints/basys3.xdc

# Set top module
set_property top slime_top [current_fileset]

# Update compile order
update_compile_order -fileset sources_1

puts "  Added basys3.xdc"
puts "  Top module: slime_top"

# ============================================================================
# Create Debug IP Cores
# ============================================================================
puts "\n[4/7] Creating debug IP cores..."

source rtl/scripts/integrate_debug_cores.tcl

puts "  Debug cores created and synthesized"

# ============================================================================
# Prepare for Synthesis
# ============================================================================
puts "\n[5/7] Preparing for synthesis..."

# The debug cores will be instantiated via the IPs we created
# The ILA will automatically insert a debug hub during synthesis
# No pre-synthesis configuration needed

puts "  Debug cores ready for integration"

# ============================================================================
# Run Synthesis
# ============================================================================
puts "\n[6/7] Running synthesis..."
puts "  This may take 5-10 minutes..."

launch_runs synth_1 -jobs 4
wait_on_run synth_1

# Check synthesis status
if {[get_property PROGRESS [get_runs synth_1]] != "100%"} {
    puts "\nERROR: Synthesis failed!"
    puts "Check ${project_dir}/synth_1/runme.log for details"
    exit 1
}

puts "  Synthesis completed successfully!"

# Open synthesized design to get utilization
open_run synth_1

# Report post-synthesis utilization
puts "\n--- Post-Synthesis Utilization ---"
report_utilization -file ${project_dir}/utilization_synth.txt
report_utilization

# ============================================================================
# Run Implementation
# ============================================================================
puts "\n[7/7] Running implementation..."
puts "  Place & Route may take 10-15 minutes..."

launch_runs impl_1 -jobs 4
wait_on_run impl_1

# Check implementation status
if {[get_property PROGRESS [get_runs impl_1]] != "100%"} {
    puts "\nERROR: Implementation failed!"
    puts "Check ${project_dir}/impl_1/runme.log for details"
    exit 1
}

puts "  Implementation completed successfully!"

# ============================================================================
# Generate Bitstream
# ============================================================================
puts "\nGenerating bitstream..."
puts "  This may take 2-3 minutes..."

launch_runs impl_1 -to_step write_bitstream -jobs 4
wait_on_run impl_1

# ============================================================================
# Generate Reports
# ============================================================================
puts "\nGenerating reports..."

open_run impl_1

# Utilization report
report_utilization -file ${project_dir}/utilization_impl.txt
report_utilization -hierarchical -file ${project_dir}/utilization_hierarchical.txt

# Timing report
report_timing_summary -file ${project_dir}/timing_summary.txt
report_timing -sort_by slack -max_paths 10 -file ${project_dir}/timing_detail.txt

# Clock report
report_clocks -file ${project_dir}/clocks.txt

# Power report
report_power -file ${project_dir}/power.txt

# Debug core report
if {[llength [get_debug_cores]] > 0} {
    report_debug_core -file ${project_dir}/debug_cores.txt
}

# ============================================================================
# Parse Reports for Key Metrics
# ============================================================================
puts "\n============================================"
puts "Build Summary"
puts "============================================"

# Get utilization
set slice_luts [get_property SLICE_LUTS [get_property UTILIZATION [current_design]]]
set slice_regs [get_property SLICE_REGISTERS [get_property UTILIZATION [current_design]]]
set bram_tiles [get_property BLOCK_RAM_TILE [get_property UTILIZATION [current_design]]]
set dsp [get_property DSP [get_property UTILIZATION [current_design]]]

puts "\nResource Utilization:"
puts "  LUTs:       [format %6d [expr int($slice_luts)]] / 20800  ([format %5.1f%% [expr $slice_luts * 100.0]])"
puts "  Registers:  [format %6d [expr int($slice_regs)]] / 41600  ([format %5.1f%% [expr $slice_regs * 100.0]])"
puts "  BRAM Tiles: [format %6d [expr int($bram_tiles)]] / 50     ([format %5.1f%% [expr $bram_tiles * 100.0]])"
puts "  DSPs:       [format %6d [expr int($dsp)]] / 90     ([format %5.1f%% [expr $dsp * 100.0]])"

# Get timing
set wns [get_property SLACK [get_timing_paths -max_paths 1]]
set whs [get_property SLACK [get_timing_paths -hold -max_paths 1]]

puts "\nTiming Summary:"
if {$wns >= 0} {
    puts "  Setup (WNS):  [format %+6.3f $wns] ns  \[PASS\]"
} else {
    puts "  Setup (WNS):  [format %+6.3f $wns] ns  \[FAIL\]"
}
if {$whs >= 0} {
    puts "  Hold (WHS):   [format %+6.3f $whs] ns  \[PASS\]"
} else {
    puts "  Hold (WHS):   [format %+6.3f $whs] ns  \[FAIL\]"
}

# Get debug cores info
set ila_count [llength [get_debug_cores -filter {CORE_TYPE == "ILA"}]]
set vio_count [llength [get_debug_cores -filter {CORE_TYPE == "VIO"}]]

puts "\nDebug Infrastructure:"
puts "  ILA Cores:    $ila_count"
puts "  VIO Cores:    $vio_count"
puts "  JTAG-to-AXI:  Present (check IP list)"

puts "\n============================================"
puts "Build Complete!"
puts "============================================"

set bitstream_path "${project_dir}/${project_name}.runs/impl_1/slime_top.bit"
puts "\nGenerated Files:"
puts "  Bitstream:         $bitstream_path"
puts "  Utilization:       ${project_dir}/utilization_impl.txt"
puts "  Timing:            ${project_dir}/timing_summary.txt"
puts "  Debug cores:       ${project_dir}/debug_cores.txt"
puts ""
puts "Programming Command:"
puts "  vivado -mode batch -source rtl/program_fpga.tcl"
puts ""
puts "Debug Access:"
puts "  1. Open Vivado Hardware Manager"
puts "  2. Connect to target (Basys3)"
puts "  3. Program device with $bitstream_path"
puts "  4. ILA: Right-click on hw_ila_1 -> Run Trigger"
puts "  5. VIO: Right-click on hw_vio_1 -> Dashboard"
puts "  6. JTAG-to-AXI: Right-click on hw_axi_1 -> Read/Write"
puts ""
puts "============================================"
puts ""

# Close project
close_project
