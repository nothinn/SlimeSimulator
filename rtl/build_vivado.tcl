# Vivado TCL Build Script for Slime Simulator
# Target: Basys3 (Artix-7 XC7A35T-1CPG236C)
#
# Usage:
#   vivado -mode batch -source build_vivado.tcl
# Or in Vivado GUI:
#   source build_vivado.tcl

set project_name "slime_simulator"
set project_dir "./vivado_project"
set part "xc7a35tcpg236-1"

# Create project
create_project $project_name $project_dir -part $part -force

# Add RTL source files
add_files -norecurse {
    src/slime_top.sv
    src/vga_controller.sv
    src/lfsr.sv
    src/fixed_point_mult.sv
    src/trig_lut.sv
    src/debouncer.sv
    src/agent_processor.sv
    src/agent_orchestrator.sv
}

# Add hex files for trig LUT
add_files -norecurse {
    src/sin_lut.hex
    src/cos_lut.hex
}

# Add constraints
add_files -fileset constrs_1 -norecurse constraints/basys3.xdc

# Set top module
set_property top slime_top [current_fileset]

# Update compile order
update_compile_order -fileset sources_1

# Run synthesis
puts "Running synthesis..."
launch_runs synth_1 -jobs 4
wait_on_run synth_1

# Check synthesis status
if {[get_property PROGRESS [get_runs synth_1]] != "100%"} {
    puts "ERROR: Synthesis failed!"
    exit 1
}

puts "Synthesis completed successfully!"

# Run implementation
puts "Running implementation..."
launch_runs impl_1 -jobs 4
wait_on_run impl_1

# Check implementation status
if {[get_property PROGRESS [get_runs impl_1]] != "100%"} {
    puts "ERROR: Implementation failed!"
    exit 1
}

puts "Implementation completed successfully!"

# Generate bitstream
puts "Generating bitstream..."
launch_runs impl_1 -to_step write_bitstream -jobs 4
wait_on_run impl_1

puts "Bitstream generation completed!"

# Report utilization
open_run impl_1
report_utilization -file ${project_dir}/utilization.txt
report_timing_summary -file ${project_dir}/timing.txt

puts "============================================"
puts "Build complete!"
puts "Bitstream: ${project_dir}/${project_name}.runs/impl_1/slime_top.bit"
puts "Utilization report: ${project_dir}/utilization.txt"
puts "Timing report: ${project_dir}/timing.txt"
puts "============================================"
