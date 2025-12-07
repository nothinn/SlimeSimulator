# Vivado TCL Script: Synthesis Validation
# Checks synthesis results for timing, resource utilization, and critical warnings

# Open project
open_project rtl/vivado_project/slime_simulator.xpr

# Run synthesis
reset_run synth_1
launch_runs synth_1 -jobs 4
wait_on_run synth_1

# Check synthesis status
if {[get_property STATUS [get_runs synth_1]] != "synth_design Complete!"} {
    puts "ERROR: Synthesis failed"
    exit 1
}

# Open synthesized design
open_run synth_1

# Check for critical warnings
set critical_warnings [get_msg_config -count -severity {CRITICAL WARNING}]
if {$critical_warnings > 0} {
    puts "ERROR: Found $critical_warnings critical warnings"
    exit 1
}

# Get resource utilization
set lut_used [get_property USED [get_cells -hierarchical -filter {PRIMITIVE_TYPE =~ LUT*}]]
set ff_used [get_property USED [get_cells -hierarchical -filter {PRIMITIVE_TYPE =~ REGISTER*}]]
set bram_used [get_property USED [get_cells -hierarchical -filter {PRIMITIVE_TYPE =~ BLOCKRAM*}]]
set dsp_used [get_property USED [get_cells -hierarchical -filter {PRIMITIVE_TYPE =~ DSP*}]]

# Basys3 (Artix-7 35T) limits
set lut_avail 20800
set ff_avail 41600
set bram_avail 100
set dsp_avail 90

# Calculate utilization percentages
set lut_util [expr {($lut_used * 100.0) / $lut_avail}]
set ff_util [expr {($ff_used * 100.0) / $ff_avail}]
set bram_util [expr {($bram_used * 100.0) / $bram_avail}]
set dsp_util [expr {($dsp_used * 100.0) / $dsp_avail}]

puts "=== Resource Utilization ==="
puts "LUTs:  $lut_used / $lut_avail ($lut_util%)"
puts "FFs:   $ff_used / $ff_avail ($ff_util%)"
puts "BRAMs: $bram_used / $bram_avail ($bram_util%)"
puts "DSPs:  $dsp_used / $dsp_avail ($dsp_util%)"

# Check if utilization is within acceptable limits (80% threshold)
if {$lut_util > 80.0 || $ff_util > 80.0 || $bram_util > 80.0 || $dsp_util > 80.0} {
    puts "WARNING: Resource utilization exceeds 80% threshold"
}

# Generate reports
report_utilization -file tests/synthesis/reports/utilization_synth.rpt
report_timing_summary -file tests/synthesis/reports/timing_synth.rpt

puts "SUCCESS: Synthesis validation passed"
exit 0
