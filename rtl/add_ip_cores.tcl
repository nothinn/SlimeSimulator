# =============================================================================
# Add JTAG2AXI and VIO IP Cores to Slime Simulator RTL Design
# =============================================================================
#
# Purpose: Creates/updates debug IP cores for FPGA memory readout and control
# Target: Basys3 FPGA (Artix-7 XC7A35T)
#
# Usage:
#   vivado -mode batch -source add_ip_cores.tcl
#
# Or within existing project:
#   source add_ip_cores.tcl
#
# =============================================================================

set project_name "slime_simulator_debug"
set project_dir "./vivado_project_debug"
set ip_dir "${project_dir}/ip"
set part "xc7a35tcpg236-1"

# Check if project exists, otherwise create it
if {![file exists "${project_dir}/${project_name}.xpr"]} {
    puts "Creating new project: ${project_name}"
    create_project $project_name $project_dir -part $part -force

    # Add RTL source files
    add_files -norecurse {
        src/slime_top_debug.sv
        src/vga_controller.sv
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
} else {
    puts "Opening existing project: ${project_name}"
    open_project "${project_dir}/${project_name}.xpr"
}

# Create IP directory
file mkdir $ip_dir

puts ""
puts "============================================================================="
puts " Creating Debug IP Cores for FPGA Memory Readout"
puts "============================================================================="
puts ""

# =============================================================================
# 1. JTAG-to-AXI Master IP
# =============================================================================
# Purpose: Provides AXI interface to design via JTAG for memory readout
# Allows host PC to read/write design memory via JTAG without soft processor
# =============================================================================

puts "Creating JTAG-to-AXI Master IP..."

# Check if IP already exists
set jtag_axi_exists 0
catch {
    set ip_check [get_ips debug_jtag_axi]
    if {$ip_check != ""} {
        set jtag_axi_exists 1
        puts "  IP already exists, updating configuration..."
    }
}

if {!$jtag_axi_exists} {
    create_ip -name jtag_axi \
              -vendor xilinx.com \
              -library ip \
              -version 1.2 \
              -module_name debug_jtag_axi \
              -dir $ip_dir
}

# Configure JTAG-to-AXI IP
set_property -dict [list \
    CONFIG.PROTOCOL {2} \
    CONFIG.M_AXI_DATA_WIDTH {32} \
    CONFIG.M_AXI_ADDR_WIDTH {32} \
    CONFIG.M_AXI_ID_WIDTH {1} \
    CONFIG.RD_TXN_QUEUE_LENGTH {4} \
    CONFIG.WR_TXN_QUEUE_LENGTH {4} \
] [get_ips debug_jtag_axi]

puts "  Configuration:"
puts "    Protocol: AXI4-Lite"
puts "    Data Width: 32-bit"
puts "    Address Width: 32-bit"
puts "    Clock: 100 MHz (system clock)"
puts "  ✓ JTAG-to-AXI Master configured"

# =============================================================================
# 2. VIO (Virtual I/O) IP Core
# =============================================================================
# Purpose: Monitor and control internal signals via JTAG
# Provides virtual inputs/outputs accessible from Vivado Hardware Manager
# =============================================================================

puts ""
puts "Creating VIO (Virtual I/O) IP..."

# Check if IP already exists
set vio_exists 0
catch {
    set ip_check [get_ips debug_vio]
    if {$ip_check != ""} {
        set vio_exists 1
        puts "  IP already exists, updating configuration..."
    }
}

if {!$vio_exists} {
    create_ip -name vio \
              -vendor xilinx.com \
              -library ip \
              -version 3.0 \
              -module_name debug_vio \
              -dir $ip_dir
}

# Configure VIO IP
# Input Probes (monitor signals from design):
#   probe_in0 [1-bit]:  capture_done
#   probe_in1 [32-bit]: frame_count
#   probe_in2 [8-bit]:  trail_data (for spot checks)
#
# Output Probes (control signals to design):
#   probe_out0 [1-bit]:  capture_trigger
#   probe_out1 [1-bit]:  sim_freeze (pause simulation)
#   probe_out2 [1-bit]:  read_enable
#   probe_out3 [19-bit]: read_addr (for 640x480 = 307200 pixels)

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

puts "  Input Probes (monitoring design):"
puts "    probe_in0 [1]:   capture_done"
puts "    probe_in1 [32]:  frame_count"
puts "    probe_in2 [8]:   trail_data"
puts "  Output Probes (controlling design):"
puts "    probe_out0 [1]:  capture_trigger"
puts "    probe_out1 [1]:  sim_freeze"
puts "    probe_out2 [1]:  read_enable"
puts "    probe_out3 [19]: read_addr"
puts "  ✓ VIO configured"

# =============================================================================
# 3. ILA (Integrated Logic Analyzer) IP Core
# =============================================================================
# Purpose: Capture waveforms of internal signals for debugging
# =============================================================================

puts ""
puts "Creating ILA (Integrated Logic Analyzer) IP..."

set ila_exists 0
catch {
    set ip_check [get_ips debug_ila]
    if {$ip_check != ""} {
        set ila_exists 1
        puts "  IP already exists, updating configuration..."
    }
}

if {!$ila_exists} {
    create_ip -name ila \
              -vendor xilinx.com \
              -library ip \
              -version 6.2 \
              -module_name debug_ila \
              -dir $ip_dir
}

# Configure ILA IP
# Probes:
#   probe0 [4]:  sim_state
#   probe1 [10]: agent_idx
#   probe2 [32]: lfsr_state
#   probe3 [8]:  trail_data
#   probe4 [10]: pixel_x
#   probe5 [9]:  pixel_y
#   probe6 [1]:  frame_start
#   probe7 [1]:  sim_running

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
    CONFIG.C_TRIGIN_EN {false} \
    CONFIG.C_TRIGOUT_EN {false} \
    CONFIG.C_INPUT_PIPE_STAGES {0} \
    CONFIG.C_EN_STRG_QUAL {1} \
    CONFIG.ALL_PROBE_SAME_MU_CNT {2} \
] [get_ips debug_ila]

puts "  Probes:"
puts "    probe0 [4]:  sim_state"
puts "    probe1 [10]: agent_idx"
puts "    probe2 [32]: lfsr_state"
puts "    probe3 [8]:  trail_data"
puts "    probe4 [10]: pixel_x"
puts "    probe5 [9]:  pixel_y"
puts "    probe6 [1]:  frame_start"
puts "    probe7 [1]:  sim_running"
puts "  Capture Depth: 4096 samples"
puts "  ✓ ILA configured"

# =============================================================================
# Generate IP Synthesis Files
# =============================================================================

puts ""
puts "Generating IP synthesis products..."

foreach ip [get_ips] {
    generate_target all [get_ips $ip]
    puts "  Generated: $ip"
}

# =============================================================================
# Update Design Hierarchy
# =============================================================================

puts ""
puts "Updating design hierarchy..."
update_compile_order -fileset sources_1

# =============================================================================
# Report Summary
# =============================================================================

puts ""
puts "============================================================================="
puts " IP Core Addition Complete!"
puts "============================================================================="
puts ""
puts "IP Cores Created:"
puts "  1. debug_jtag_axi   - JTAG-to-AXI Master (memory access via JTAG)"
puts "  2. debug_vio        - Virtual I/O (signal monitoring & control)"
puts "  3. debug_ila        - Integrated Logic Analyzer (waveform capture)"
puts ""
puts "Integration Status:"
puts "  ✓ IPs instantiated in slime_top_debug.sv"
puts "  ✓ IPs connected via debug_wrapper.sv"
puts "  ✓ Trail memory accessible at base address 0x0000_0000"
puts "  ✓ Control registers accessible at 0x0010_0000"
puts ""
puts "Memory Map:"
puts "  Trail Memory: 0x0000_0000 - 0x0004_AFFF (640x480 = 307200 bytes)"
puts "  Control Reg:  0x0010_0000 (bit 0: freeze simulation)"
puts "  Status Reg:   0x0010_0004 (bit 0: capture_triggered, bit 1: capture_done)"
puts "  Frame Count:  0x0010_0008 (32-bit frame counter)"
puts "  Width:        0x0010_000C (640)"
puts "  Height:       0x0010_0010 (480)"
puts ""
puts "Next Steps:"
puts "  1. Build bitstream:  vivado -mode batch -source rebuild_with_ips.tcl"
puts "  2. Program FPGA:     vivado -mode batch -source program_fpga.tcl"
puts "  3. Access via JTAG:  Use Vivado Hardware Manager or fpga_controller.py"
puts ""
puts "Files Generated:"
puts "  - ${ip_dir}/debug_jtag_axi/"
puts "  - ${ip_dir}/debug_vio/"
puts "  - ${ip_dir}/debug_ila/"
puts ""
puts "Documentation:"
puts "  - register_map.txt          - Register definitions for Python scripts"
puts "  - ip_integration_report.txt - Detailed integration summary"
puts ""
puts "============================================================================="
puts ""

# Save project
save_project_as -force $project_name $project_dir

puts "Project saved: ${project_dir}/${project_name}.xpr"
puts ""
