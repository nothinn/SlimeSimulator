# Debug Infrastructure - Quick Reference Card

## Build & Program

```bash
# Build with debug (20-30 min)
cd /home/reson/SlimeSimulator
vivado -mode batch -source rtl/build_with_debug.tcl

# Program FPGA
vivado -mode batch -source rtl/program_fpga.tcl
```

## Hardware Manager Setup

```tcl
open_hw_manager
connect_hw_server
open_hw_target

# Program device
set_property PROGRAM.FILE {vivado_project_debug/.../slime_top.bit} [current_hw_device]
program_hw_devices [current_hw_device]
```

## ILA Quick Commands

### Basic Capture
```tcl
# Trigger immediately
run_hw_ila hw_ila_1
wait_on_hw_ila hw_ila_1
display_hw_ila_data [upload_hw_ila_data hw_ila_1]
```

### Common Triggers
```tcl
# Frame start
set_property TRIGGER_COMPARE_VALUE {eq1'b1} [get_hw_probes frame_start]

# Agent processing
set_property TRIGGER_COMPARE_VALUE {eq4'b0010} [get_hw_probes sim_state]

# Memory write
set_property TRIGGER_COMPARE_VALUE {eq1'b1} [get_hw_probes trail_we_b]

# Specific agent
set_property TRIGGER_COMPARE_VALUE {eq10'd500} [get_hw_probes agent_idx]
```

### Export
```tcl
write_hw_ila_data -csv_file capture.csv hw_ila_1
```

## VIO Quick Commands

### Read State
```tcl
# Frame count
get_property INPUT_VALUE [get_hw_probes frame_count -of_objects [get_hw_vios hw_vio_1]]

# LFSR state
get_property INPUT_VALUE [get_hw_probes lfsr_state -of_objects [get_hw_vios hw_vio_1]]

# Simulation state
get_property INPUT_VALUE [get_hw_probes sim_state -of_objects [get_hw_vios hw_vio_1]]
```

### Control Simulation
```tcl
# Freeze
set_property OUTPUT_VALUE 1 [get_hw_probes vio_sim_freeze]
commit_hw_vio [get_hw_vios hw_vio_1]

# Resume
set_property OUTPUT_VALUE 0 [get_hw_probes vio_sim_freeze]
commit_hw_vio [get_hw_vios hw_vio_1]
```

### Read Memory via VIO
```tcl
# Read pixel at (x, y)
set addr [expr {$y * 160 + $x}]
set_property OUTPUT_VALUE $addr [get_hw_probes vio_trail_addr]
set_property OUTPUT_VALUE 1 [get_hw_probes vio_trail_read_en]
commit_hw_vio [get_hw_vios hw_vio_1]

after 100
get_property INPUT_VALUE [get_hw_probes trail_data_b_out]
```

## JTAG-to-AXI Quick Commands

### Read Memory
```tcl
# Single pixel
set addr [expr {$y * 160 + $x}]
create_hw_axi_txn read_px [get_hw_axis hw_axi_1] -address $addr -len 1 -type read
run_hw_axi read_px
get_property DATA [get_hw_axi_txns read_px]

# Entire memory
create_hw_axi_txn dump [get_hw_axis hw_axi_1] -address 0 -len 19200 -type read
run_hw_axi dump
set fp [open "dump.bin" w]; fconfigure $fp -translation binary
puts -nonewline $fp [get_property DATA [get_hw_axi_txns dump]]
close $fp
```

### Write Memory
```tcl
# Single pixel
set addr [expr {$y * 160 + $x}]
create_hw_axi_txn write_px [get_hw_axis hw_axi_1] -address $addr -data 255 -type write
run_hw_axi write_px
```

## Signal Map

### ILA Probes (15)
| # | Signal | Width | Purpose |
|---|--------|-------|---------|
| 0 | lfsr_state | 32 | Random number |
| 1 | sim_state | 4 | State machine |
| 2 | agent_idx | 10 | Current agent |
| 3 | trail_addr_b | 19 | Memory address |
| 4 | trail_data_b_in | 8 | Write data |
| 5 | trail_we_b | 1 | Write enable |
| 6 | vga_hs | 1 | Hsync |
| 7 | vga_vs | 1 | Vsync |
| 8 | pixel_x | 10 | X coord |
| 9 | pixel_y | 9 | Y coord |
| 10 | frame_start | 1 | Frame pulse |
| 11 | sim_running | 1 | Running flag |
| 12 | sim_pause | 1 | Pause flag |
| 13 | speed_level | 4 | Speed setting |
| 14 | btn_debounced | 5 | Buttons |

### VIO Inputs (7)
| # | Signal | Width | Purpose |
|---|--------|-------|---------|
| 0 | lfsr_state | 32 | LFSR value |
| 1 | sim_state | 4 | State |
| 2 | agent_idx | 10 | Agent index |
| 3 | trail_data_b_out | 8 | Read data |
| 4 | frame_count | 32 | Frame # |
| 5 | sim_running | 1 | Running |
| 6 | led | 16 | LED status |

### VIO Outputs (5)
| # | Signal | Width | Purpose |
|---|--------|-------|---------|
| 0 | vio_sim_freeze | 1 | Freeze sim |
| 1 | vio_trail_read_en | 1 | Read enable |
| 2 | vio_trail_addr | 19 | Read address |
| 3 | vio_inject_seed | 1 | Seed trigger |
| 4 | vio_seed_value | 32 | Seed value |

## Memory Map

**Trail Map:** 160×120 pixels (19,200 bytes)
- **Address:** `y * 160 + x`
- **Range:** 0x0000 - 0x4AFF
- **Value:** 0-255 (trail intensity)

**Reverse:**
- `x = addr % 160`
- `y = addr / 160`

## State Machine Values

```
sim_state:
  0 = IDLE
  1 = INIT
  2 = RUN_AGENTS
  3 = DIFFUSE
  4 = WAIT_FRAME
```

## Resources

- **Full Guide:** `/home/reson/SlimeSimulator/rtl/DEBUG_INFRASTRUCTURE.md`
- **Summary:** `/home/reson/SlimeSimulator/rtl/DEBUG_SUMMARY.txt`
- **Build:** `/home/reson/SlimeSimulator/rtl/build_with_debug.tcl`
- **Integration:** `/home/reson/SlimeSimulator/rtl/scripts/integrate_debug_cores.tcl`
