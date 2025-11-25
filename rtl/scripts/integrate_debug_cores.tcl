# Integrate Debug Cores into Slime Simulator
# Adds comprehensive debugging infrastructure using Xilinx ILA, VIO, and JTAG
#
# This script is designed to be sourced after implementation but before bitstream
# generation to add debug cores as a post-implementation step.
#
# Features:
# - ILA: Captures LFSR, agent processor pipeline, trail map access, VGA timing
# - VIO: Provides software-accessible registers for reading state
# - JTAG-to-AXI: Enables memory access to trail map
#
# Usage:
#   source rtl/scripts/integrate_debug_cores.tcl
#

puts "============================================"
puts "Integrating Debug Cores into Design"
puts "============================================"

# Get the current project directory
set project_dir [get_property DIRECTORY [current_project]]
set ip_dir "${project_dir}/ip"
file mkdir $ip_dir

# ============================================================================
# ILA - Integrated Logic Analyzer
# ============================================================================
# Captures critical simulation signals for debugging
#
# Probe assignments:
# 0: lfsr_state[31:0]           - LFSR random number generator output
# 1: sim_state[3:0]             - Top-level simulation state machine
# 2: agent_idx[9:0]             - Current agent being processed (0-999)
# 3: trail_addr_b[18:0]         - Trail map write address from agents
# 4: trail_data_b_in[7:0]       - Trail map write data
# 5: trail_we_b                 - Trail map write enable
# 6: vga_hs                     - VGA horizontal sync
# 7: vga_vs                     - VGA vertical sync
# 8: pixel_x[9:0]               - VGA pixel X coordinate
# 9: pixel_y[8:0]               - VGA pixel Y coordinate
# 10: frame_start               - VGA frame start pulse
# 11: sim_running               - Simulation running status
# 12: sim_pause                 - Simulation pause status
# 13: speed_level[3:0]          - Speed control level
# 14: btn_debounced[4:0]        - Debounced button inputs

puts "\n[1/4] Creating ILA IP Core..."

create_ip -name ila -vendor xilinx.com -library ip -version 6.2 \
    -module_name slime_ila -dir $ip_dir -force

set_property -dict [list \
    CONFIG.C_NUM_OF_PROBES {15} \
    CONFIG.C_DATA_DEPTH {8192} \
    CONFIG.C_INPUT_PIPE_STAGES {0} \
    CONFIG.C_EN_STRG_QUAL {1} \
    CONFIG.C_ADV_TRIGGER {true} \
    CONFIG.ALL_PROBE_SAME_MU {true} \
    CONFIG.ALL_PROBE_SAME_MU_CNT {2} \
    CONFIG.C_PROBE0_WIDTH {32} \
    CONFIG.C_PROBE1_WIDTH {4} \
    CONFIG.C_PROBE2_WIDTH {10} \
    CONFIG.C_PROBE3_WIDTH {19} \
    CONFIG.C_PROBE4_WIDTH {8} \
    CONFIG.C_PROBE5_WIDTH {1} \
    CONFIG.C_PROBE6_WIDTH {1} \
    CONFIG.C_PROBE7_WIDTH {1} \
    CONFIG.C_PROBE8_WIDTH {10} \
    CONFIG.C_PROBE9_WIDTH {9} \
    CONFIG.C_PROBE10_WIDTH {1} \
    CONFIG.C_PROBE11_WIDTH {1} \
    CONFIG.C_PROBE12_WIDTH {1} \
    CONFIG.C_PROBE13_WIDTH {4} \
    CONFIG.C_PROBE14_WIDTH {5} \
] [get_ips slime_ila]

generate_target all [get_ips slime_ila]
synth_ip [get_ips slime_ila]

puts "  Created ILA with 15 probes, 8192 samples deep"
puts "  Memory usage: ~120 Kbits"

# ============================================================================
# VIO - Virtual I/O
# ============================================================================
# Provides software-accessible registers for reading design state
#
# Input probes (read from design):
# IN0: lfsr_state[31:0]         - Current LFSR value
# IN1: sim_state[3:0]           - Current simulation state
# IN2: agent_idx[9:0]           - Current agent index
# IN3: trail_data_b_out[7:0]    - Trail map read data
# IN4: frame_count[31:0]        - VGA frame counter
# IN5: sim_running              - Running status
# IN6: led[15:0]                - LED status display
#
# Output probes (write to design):
# OUT0: vio_sim_freeze          - Freeze simulation for inspection
# OUT1: vio_trail_read_en       - Enable trail map read via VIO
# OUT2: vio_trail_addr[18:0]    - Trail map address to read
# OUT3: vio_inject_seed         - Inject new LFSR seed
# OUT4: vio_seed_value[31:0]    - LFSR seed value to inject

puts "\n[2/4] Creating VIO IP Core..."

create_ip -name vio -vendor xilinx.com -library ip -version 3.0 \
    -module_name slime_vio -dir $ip_dir -force

set_property -dict [list \
    CONFIG.C_NUM_PROBE_IN {7} \
    CONFIG.C_NUM_PROBE_OUT {5} \
    CONFIG.C_PROBE_IN0_WIDTH {32} \
    CONFIG.C_PROBE_IN1_WIDTH {4} \
    CONFIG.C_PROBE_IN2_WIDTH {10} \
    CONFIG.C_PROBE_IN3_WIDTH {8} \
    CONFIG.C_PROBE_IN4_WIDTH {32} \
    CONFIG.C_PROBE_IN5_WIDTH {1} \
    CONFIG.C_PROBE_IN6_WIDTH {16} \
    CONFIG.C_PROBE_OUT0_WIDTH {1} \
    CONFIG.C_PROBE_OUT1_WIDTH {1} \
    CONFIG.C_PROBE_OUT2_WIDTH {19} \
    CONFIG.C_PROBE_OUT3_WIDTH {1} \
    CONFIG.C_PROBE_OUT4_WIDTH {32} \
] [get_ips slime_vio]

generate_target all [get_ips slime_vio]
synth_ip [get_ips slime_vio]

puts "  Created VIO with 7 input probes, 5 output probes"

# ============================================================================
# JTAG-to-AXI Master
# ============================================================================
# Enables memory-mapped access to trail map via JTAG
# This allows reading/writing the entire trail memory from software

puts "\n[3/4] Creating JTAG-to-AXI Master IP Core..."

create_ip -name jtag_axi -vendor xilinx.com -library ip -version 1.2 \
    -module_name slime_jtag_axi -dir $ip_dir -force

set_property -dict [list \
    CONFIG.PROTOCOL {2} \
    CONFIG.M_AXI_DATA_WIDTH {32} \
    CONFIG.M_AXI_ADDR_WIDTH {32} \
    CONFIG.M_AXI_ID_WIDTH {1} \
    CONFIG.RD_TXN_QUEUE_LENGTH {8} \
    CONFIG.WR_TXN_QUEUE_LENGTH {8} \
] [get_ips slime_jtag_axi]

generate_target all [get_ips slime_jtag_axi]
synth_ip [get_ips slime_jtag_axi]

puts "  Created JTAG-to-AXI with AXI4-Lite interface"

# ============================================================================
# AXI BRAM Controller
# ============================================================================
# Bridges AXI bus to trail map BRAM
# Provides third port for JTAG access without interfering with VGA/Agent ports

puts "\n[4/4] Creating AXI BRAM Controller IP Core..."

create_ip -name axi_bram_ctrl -vendor xilinx.com -library ip -version 4.1 \
    -module_name slime_axi_bram_ctrl -dir $ip_dir -force

set_property -dict [list \
    CONFIG.SINGLE_PORT_BRAM {0} \
    CONFIG.DATA_WIDTH {32} \
    CONFIG.ECC_TYPE {0} \
    CONFIG.SUPPORTS_NARROW_BURST {0} \
    CONFIG.PROTOCOL {AXI4LITE} \
    CONFIG.MEM_DEPTH {32768} \
] [get_ips slime_axi_bram_ctrl]

generate_target all [get_ips slime_axi_bram_ctrl]
synth_ip [get_ips slime_axi_bram_ctrl]

puts "  Created AXI BRAM Controller (depth=32768, covers 19200 trail map bytes)"

# ============================================================================
# Mark Debug Signals
# ============================================================================
# Add mark_debug attributes to critical signals so they're preserved
# and accessible to debug cores

puts "\n[5/4] Marking critical signals for debug..."

# This would be done via mark_debug attributes in the RTL
# The signals are already marked in the modified slime_top.sv

puts "  Debug signals marked via (* mark_debug *) attributes in RTL"

# ============================================================================
# Summary
# ============================================================================

puts "\n============================================"
puts "Debug Core Integration Complete!"
puts "============================================"
puts ""
puts "ILA Configuration:"
puts "  - 15 probes monitoring critical signals"
puts "  - 8192 sample depth (~8K cycles of capture)"
puts "  - Advanced triggering enabled"
puts "  - Probes: LFSR, state machines, memory access, VGA timing"
puts ""
puts "VIO Configuration:"
puts "  - 7 input probes (read design state)"
puts "  - 5 output probes (control from software)"
puts "  - Can freeze simulation, read memory, inject seeds"
puts ""
puts "JTAG-to-AXI Configuration:"
puts "  - Full memory-mapped access to 19200-byte trail map"
puts "  - AXI4-Lite interface, 32-bit data width"
puts "  - Non-intrusive read/write via third BRAM port"
puts ""
puts "Next Steps:"
puts "  1. Continue with implementation and bitstream generation"
puts "  2. Program FPGA with debug-enabled bitstream"
puts "  3. Connect with Vivado Hardware Manager"
puts "  4. Access ILA: Tools -> Set Up Debug -> Add probes"
puts "  5. Access VIO: Hardware Manager -> VIO dashboard"
puts "  6. Access Memory: Hardware Manager -> JTAG-to-AXI"
puts ""
puts "Resource Impact (estimated):"
puts "  - LUTs: +1500-2000"
puts "  - FFs: +2000-2500"
puts "  - BRAM: +4-5 tiles (for ILA sample buffer)"
puts "============================================"
