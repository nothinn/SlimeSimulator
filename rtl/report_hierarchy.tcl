# Generate hierarchical utilization report
# Usage: vivado -mode batch -source report_hierarchy.tcl

set project_dir "./vivado_project"
set project_name "slime_simulator"

# Open the project
open_project ${project_dir}/${project_name}.xpr

# Open the synthesis run
open_run synth_1

# Generate hierarchical utilization report
report_utilization -hierarchical -hierarchical_depth 3 -file hierarchy_utilization.txt

puts "========================================="
puts "Hierarchical utilization report generated: hierarchy_utilization.txt"
puts "========================================="

close_project
