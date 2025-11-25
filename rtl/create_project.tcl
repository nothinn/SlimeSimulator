# Vivado TCL Script - Create Project Only (for GUI editing)
# Target: Basys3 (Artix-7 XC7A35T-1CPG236C)
#
# Usage:
#   vivado -mode batch -source create_project.tcl
#   Then open: vivado_project/slime_simulator.xpr

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

puts "============================================"
puts "Project created: ${project_dir}/${project_name}.xpr"
puts "Open with: vivado ${project_dir}/${project_name}.xpr"
puts "============================================"
