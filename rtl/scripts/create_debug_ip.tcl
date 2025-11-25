# Create Debug IPs for Slime Simulator
# Generates: ILA, VIO, JTAG-to-AXI-Master
#
# Usage: Run after creating project
#   source scripts/create_debug_ip.tcl

set ip_dir "./vivado_project/ip"
file mkdir $ip_dir

# ============================================================================
# VIO - Virtual I/O for debug control
# ============================================================================
# Outputs: capture_trigger, sim_freeze, read_enable
# Inputs: capture_done, frame_count

puts "Creating VIO IP..."

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

# Probe definitions:
# IN0: capture_done (1-bit)
# IN1: frame_count (32-bit)
# IN2: trail_data_read (8-bit)
# OUT0: capture_trigger (1-bit)
# OUT1: sim_freeze (1-bit)
# OUT2: read_enable (1-bit)
# OUT3: read_addr (19-bit for 640x480)

generate_target all [get_ips debug_vio]

# ============================================================================
# ILA - Integrated Logic Analyzer for signal capture
# ============================================================================
# Capture key simulation signals for debugging

puts "Creating ILA IP..."

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
    CONFIG.C_TRIGIN_EN {false} \
    CONFIG.C_TRIGOUT_EN {false} \
    CONFIG.C_INPUT_PIPE_STAGES {0} \
    CONFIG.C_EN_STRG_QUAL {1} \
    CONFIG.ALL_PROBE_SAME_MU_CNT {2} \
] [get_ips debug_ila]

# Probe definitions:
# 0: sim_state (4-bit)
# 1: agent_idx (10-bit)
# 2: lfsr_state (32-bit)
# 3: trail_data (8-bit)
# 4: pixel_x (10-bit)
# 5: pixel_y (9-bit)
# 6: frame_start (1-bit)
# 7: sim_running (1-bit)

generate_target all [get_ips debug_ila]

# ============================================================================
# JTAG-to-AXI Master - For reading trail memory
# ============================================================================
# Allows reading BRAM contents via JTAG for image capture

puts "Creating JTAG-to-AXI Master IP..."

create_ip -name jtag_axi -vendor xilinx.com -library ip -version 1.2 -module_name debug_jtag_axi -dir $ip_dir

set_property -dict [list \
    CONFIG.PROTOCOL {2} \
    CONFIG.M_AXI_DATA_WIDTH {32} \
    CONFIG.M_AXI_ADDR_WIDTH {32} \
    CONFIG.M_AXI_ID_WIDTH {1} \
    CONFIG.RD_TXN_QUEUE_LENGTH {4} \
    CONFIG.WR_TXN_QUEUE_LENGTH {4} \
] [get_ips debug_jtag_axi]

generate_target all [get_ips debug_jtag_axi]

# ============================================================================
# AXI BRAM Controller - Interface to trail memory
# ============================================================================

puts "Creating AXI BRAM Controller IP..."

create_ip -name axi_bram_ctrl -vendor xilinx.com -library ip -version 4.1 -module_name debug_axi_bram_ctrl -dir $ip_dir

set_property -dict [list \
    CONFIG.SINGLE_PORT_BRAM {1} \
    CONFIG.DATA_WIDTH {32} \
    CONFIG.ECC_TYPE {0} \
    CONFIG.SUPPORTS_NARROW_BURST {0} \
    CONFIG.PROTOCOL {AXI4LITE} \
] [get_ips debug_axi_bram_ctrl]

generate_target all [get_ips debug_axi_bram_ctrl]

# ============================================================================
# Synthesize all IPs
# ============================================================================

puts "Synthesizing debug IPs..."

foreach ip [get_ips] {
    synth_ip $ip
}

puts "============================================"
puts "Debug IPs created successfully!"
puts "IPs generated in: $ip_dir"
puts ""
puts "Available IPs:"
puts "  - debug_vio: Control capture and read addresses"
puts "  - debug_ila: Capture simulation waveforms"
puts "  - debug_jtag_axi: Read trail memory via JTAG"
puts "  - debug_axi_bram_ctrl: AXI interface to BRAM"
puts "============================================"
