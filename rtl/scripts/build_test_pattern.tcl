# Vivado TCL Build Script - VGA Test Pattern Only
# Minimal build for testing VGA output
#
# Usage:
#   cd rtl
#   vivado -mode batch -source scripts/build_test_pattern.tcl

set project_name "vga_test"
set project_dir "./vivado_project_test"
set part "xc7a35tcpg236-1"

# Create project
create_project $project_name $project_dir -part $part -force

# Add only VGA test files
add_files -norecurse {
    src/vga_controller.sv
    src/vga_test_pattern.sv
}

# Add constraints
add_files -fileset constrs_1 -norecurse constraints/basys3.xdc

# Set top module
set_property top vga_test_top [current_fileset]
update_compile_order -fileset sources_1

# Synthesis
puts "Running synthesis..."
launch_runs synth_1 -jobs 4
wait_on_run synth_1

# Implementation
puts "Running implementation..."
launch_runs impl_1 -jobs 4
wait_on_run impl_1

# Bitstream
puts "Generating bitstream..."
launch_runs impl_1 -to_step write_bitstream -jobs 4
wait_on_run impl_1

puts "============================================"
puts "VGA Test build complete!"
puts "Bitstream: ${project_dir}/${project_name}.runs/impl_1/vga_test_top.bit"
puts ""
puts "Test patterns (SW[2:0]):"
puts "  0: Color bars"
puts "  1: Gradient"
puts "  2: Checkerboard"
puts "  3: Border test"
puts "  4: Grid"
puts "  5: RGB bars"
puts "  6: Crosshatch"
puts "  7: Pixel test"
puts "============================================"
