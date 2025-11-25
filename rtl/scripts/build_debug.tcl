# Vivado TCL Build Script - Debug Version
# Includes ILA, VIO, and JTAG-to-AXI for image capture
#
# Usage:
#   cd rtl
#   vivado -mode batch -source scripts/build_debug.tcl

set project_name "slime_simulator_debug"
set project_dir "./vivado_project_debug"
set part "xc7a35tcpg236-1"

# Create project
create_project $project_name $project_dir -part $part -force

# Add RTL source files
add_files -norecurse {
    src/slime_top_debug.sv
    src/vga_controller.sv
    src/vga_test_pattern.sv
    src/lfsr.sv
    src/fixed_point_mult.sv
    src/trig_lut.sv
    src/debouncer.sv
    src/agent_processor.sv
    src/debug_wrapper.sv
}

# Add hex files
add_files -norecurse {
    src/sin_lut.hex
    src/cos_lut.hex
}

# Add constraints
add_files -fileset constrs_1 -norecurse constraints/basys3.xdc

# Set top module
set_property top slime_top_debug [current_fileset]
update_compile_order -fileset sources_1

# ============================================================================
# Create Debug IPs
# ============================================================================
puts "Creating debug IPs..."

set ip_dir "${project_dir}/ip"
file mkdir $ip_dir

# VIO
create_ip -name vio -vendor xilinx.com -library ip -version 3.0 -module_name debug_vio -dir $ip_dir
set_property -dict [list \
    CONFIG.C_PROBE_IN0_WIDTH {1} \
    CONFIG.C_PROBE_IN1_WIDTH {32} \
    CONFIG.C_PROBE_IN2_WIDTH {8} \
    CONFIG.C_PROBE_OUT0_WIDTH {1} \
    CONFIG.C_PROBE_OUT1_WIDTH {1} \
    CONFIG.C_PROBE_OUT2_WIDTH {1} \
    CONFIG.C_PROBE_OUT3_WIDTH {19} \
    CONFIG.C_NUM_PROBE_IN {3} \
    CONFIG.C_NUM_PROBE_OUT {4} \
] [get_ips debug_vio]
generate_target all [get_ips debug_vio]

# ILA
create_ip -name ila -vendor xilinx.com -library ip -version 6.2 -module_name debug_ila -dir $ip_dir
set_property -dict [list \
    CONFIG.C_PROBE0_WIDTH {4} \
    CONFIG.C_PROBE1_WIDTH {10} \
    CONFIG.C_PROBE2_WIDTH {32} \
    CONFIG.C_PROBE3_WIDTH {8} \
    CONFIG.C_PROBE4_WIDTH {10} \
    CONFIG.C_PROBE5_WIDTH {9} \
    CONFIG.C_PROBE6_WIDTH {1} \
    CONFIG.C_PROBE7_WIDTH {1} \
    CONFIG.C_NUM_OF_PROBES {8} \
    CONFIG.C_DATA_DEPTH {4096} \
    CONFIG.C_EN_STRG_QUAL {1} \
] [get_ips debug_ila]
generate_target all [get_ips debug_ila]

# JTAG-to-AXI
create_ip -name jtag_axi -vendor xilinx.com -library ip -version 1.2 -module_name debug_jtag_axi -dir $ip_dir
set_property -dict [list \
    CONFIG.PROTOCOL {2} \
    CONFIG.M_AXI_DATA_WIDTH {32} \
    CONFIG.M_AXI_ADDR_WIDTH {32} \
] [get_ips debug_jtag_axi]
generate_target all [get_ips debug_jtag_axi]

# ============================================================================
# Synthesis
# ============================================================================
puts "Running synthesis..."
launch_runs synth_1 -jobs 4
wait_on_run synth_1

if {[get_property PROGRESS [get_runs synth_1]] != "100%"} {
    puts "ERROR: Synthesis failed!"
    exit 1
}

# ============================================================================
# Implementation
# ============================================================================
puts "Running implementation..."
launch_runs impl_1 -jobs 4
wait_on_run impl_1

if {[get_property PROGRESS [get_runs impl_1]] != "100%"} {
    puts "ERROR: Implementation failed!"
    exit 1
}

# ============================================================================
# Bitstream
# ============================================================================
puts "Generating bitstream..."
launch_runs impl_1 -to_step write_bitstream -jobs 4
wait_on_run impl_1

# Reports
open_run impl_1
report_utilization -file ${project_dir}/utilization.txt
report_timing_summary -file ${project_dir}/timing.txt

puts "============================================"
puts "Debug build complete!"
puts "Bitstream: ${project_dir}/${project_name}.runs/impl_1/slime_top_debug.bit"
puts ""
puts "Debug features:"
puts "  - ILA: Capture simulation waveforms"
puts "  - VIO: Control capture and freeze"
puts "  - JTAG-to-AXI: Download trail memory"
puts "============================================"
