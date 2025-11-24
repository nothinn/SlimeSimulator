# Build script for VGA Solid Color Diagnostic Test
# Generates a simple solid color output to debug VGA hardware

set project_name "vga_solid_test"
set project_dir "./vivado_project_solid"
set part "xc7a35tcpg236-1"

# Create project
create_project $project_name $project_dir -part $part -force

# Add source files
add_files -norecurse {
    src/vga_solid_color.sv
    src/vga_controller.sv
}

# Add constraints
add_files -fileset constrs_1 -norecurse constraints/basys3.xdc

# Set top module
set_property top vga_solid_color [current_fileset]
update_compile_order -fileset sources_1

# Run synthesis
puts "Running synthesis for solid color test..."
launch_runs synth_1 -jobs 4
wait_on_run synth_1

# Check for synthesis errors
if {[get_property PROGRESS [get_runs synth_1]] ne "100%"} {
    puts "ERROR: Synthesis failed!"
    exit 1
}

# Run implementation
puts "Running implementation..."
launch_runs impl_1 -jobs 4
wait_on_run impl_1

# Generate bitstream
puts "Generating bitstream..."
launch_runs impl_1 -to_step write_bitstream -jobs 4
wait_on_run impl_1

# Report results
set bitstream_file [glob -nocomplain $project_dir/$project_name.runs/impl_1/*.bit]
if {$bitstream_file ne ""} {
    set bitstream_size [file size $bitstream_file]
    puts "SUCCESS: Bitstream generated!"
    puts "File: $bitstream_file"
    puts "Size: [expr {$bitstream_size / 1024}] KB"
} else {
    puts "ERROR: Bitstream not found!"
    exit 1
}

# Generate reports
puts "Generating reports..."
report_timing_summary -file $project_dir/$project_name.runs/impl_1/timing_summary.rpt
report_utilization -file $project_dir/$project_name.runs/impl_1/utilization.rpt

puts "Build complete!"
exit 0
