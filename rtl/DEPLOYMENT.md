# Slime Simulator FPGA Deployment Guide

## Current Status

### ✅ Builds Complete
- **VGA Test Pattern**: Built successfully (276 KB bitstream)
  - Status: Programmed to FPGA, but no VGA output observed
  - Contains 8 test patterns (color bars, gradient, checkerboard, etc.)

- **Main Slime Simulator**: Built successfully (422 KB bitstream)
  - Status: **Currently programmed to FPGA**
  - Contains full 320×240 simulation with 2× VGA upscaling
  - 64 agents with fixed-point arithmetic
  - Trail diffusion via BRAM

### Build Verification
Both designs synthesized and implemented with:
- ✅ 0 Critical Errors
- ✅ 0 Critical Warnings
- ✅ Timing constraints met (>8ns positive slack)
- ✅ Resource utilization within limits (24 BRAM36 of 50 available)

## Main Design Features

### Control Interface (Buttons)
| Button | Function | Notes |
|--------|----------|-------|
| **BTNC** | Start/Stop Simulation | Toggles between IDLE and RUN_AGENTS states |
| **BTNU** | Increase Speed | Reduces WAIT_FRAME counter (faster updates) |
| **BTND** | Decrease Speed | Increases WAIT_FRAME counter (slower updates) |
| **BTNL** | Randomize Agents | Resets agent positions with LFSR randomization |
| **BTNR** | Reset All | Hard reset (resets entire design) |

### Display Output (VGA 640×480)
- Trail map displayed as green intensity (0-15 bits mapped to brightness)
- Resolution: 320×240 internal, 2× upscaled to fill VGA display
- Each internal pixel displays as 2×2 pixels on VGA

### Status LEDs (LED[15:0])
- **LED[2:0]**: Current agent count (lower 3 bits)
- **LED[7:3]**: State machine status (5 bits)
  - State encoding: See slime_top.sv for state definitions
- **LED[15:8]**: Trail data byte from selected location

## Expected Behavior at Startup

1. **Press BTNR** (Reset)
   - Clears all trail memory
   - Initializes agents at center
   - Status LEDs show initialization progress

2. **Press BTNC** (Start)
   - Agents begin moving and creating trails
   - VGA should show trail patterns building up
   - Watch for growing connected structures (typical slime mold behavior)

3. **Real-time Control**
   - Use BTNU/BTND to change simulation speed
   - Press BTNL to randomize agent positions (forces evolution of new patterns)

## VGA Output Troubleshooting

### If VGA Still Not Working:

1. **Check Physical Connection**
   - Verify VGA cable is securely connected to both FPGA board and monitor
   - Check monitor is powered and displays something from other input
   - Try different VGA cable if available

2. **Check Monitor Settings**
   - Select correct input source (may need to cycle through DVI, HDMI, VGA ports)
   - Check resolution is set to accept 640×480 (or auto-detect)
   - Verify refresh rate setting (design outputs 60Hz)

3. **Check FPGA Status**
   - LEDs should show some activity (especially LED[9] blinking for frame sync)
   - If no LED activity: power cycle FPGA board
   - If LEDs active but no VGA: issue likely with color output circuit or pin connection

4. **Alternative Test Patterns** (if needed)
   - Can reprogram VGA test pattern bitstream for dedicated testing
   - Provides color bars and other diagnostic patterns
   - Located at: `vivado_project_test/vga_test.runs/impl_1/vga_test_top.bit`

### Pin Verification (basys3.xdc)
```
VGA Red:     G19, H19, J19, N19     (vga_r[3:0])
VGA Green:   J17, H17, G17, D17     (vga_g[3:0])
VGA Blue:    N18, L18, K18, J18     (vga_b[3:0])
H-Sync:      P19
V-Sync:      R19
```

## File Locations

```
vivado_project/
  ├── slime_simulator.runs/impl_1/
  │   ├── slime_top.bit              ← Currently programmed bitstream
  │   ├── slime_top_routed.dcp       ← Design checkpoint
  │   └── *.rpt                      ← Timing, utilization reports
  └── slime_simulator.srcs/
      └── sources_1/new/
          ├── slime_top.sv           ← Top module
          ├── vga_controller.sv      ← VGA timing
          ├── agent_processor.sv     ← Agent simulation
          ├── debouncer.sv           ← Button debouncing
          ├── fixed_point_mult.sv    ← Math library
          ├── trig_lut.sv            ← Sine/cosine lookup
          └── lfsr.sv                ← Pseudo-random generator

vivado_project_test/
  └── vga_test.runs/impl_1/
      └── vga_test_top.bit           ← Test pattern bitstream (if needed)

build_vivado.tcl                     ← Main design build script
build_test_pattern.tcl               ← Test pattern build script
```

## Implementation Details

### State Machine (slime_top.sv)
```
IDLE        → Wait for BTNC (start signal)
INIT        → Initialize agents (single cycle)
RUN_AGENTS  → Process all 64 agents through state machine
DIFFUSE     → Apply trail diffusion kernel
WAIT_FRAME  → Synchronize with VGA frame rate
```

### Agent Processing Pipeline
Each of 64 agents executes:
1. Sense trail intensity at current position and neighbors
2. Decide new direction (sensory stage)
3. Apply motor commands (move forward with LFSR-based turning)
4. Deposit trail at new position
5. Repeat

### Trail Memory
- Dual-port BRAM (Block RAM)
- 320×240 = 76,800 locations
- 8-bit intensity per cell
- Uses 24 × RAMB36E1 blocks
- Continuous diffusion with 8 surrounding neighbors

### Timing
- Clock: 100 MHz input (from FPGA board)
- VGA pixel clock: 25 MHz (divided by 4)
- Frame rate: 60 Hz
- Agent processing: ~1-2 frames per cycle in RUN_AGENTS state

## Development Notes

### Known Limitations
- Trail diffusion currently processes neighbors sequentially (not optimized)
- Agent positions stored as 17-bit coordinates (allows wraparound at edges)
- Fixed-point arithmetic: Q12.12 format (12 integer, 12 fractional bits)

### Performance
- 64 simultaneous agents
- 320×240 trail map with diffusion
- 75% LUT utilization
- 50% BRAM utilization
- Timing closure: >8ns positive slack (safe margin)

### LFSR Properties
- Maximal-length pseudo-random sequences
- Deterministic (identical results with same seed)
- Multiple independent LFSRs for agents and diffusion
- Total: 1024-bit state (16 × 64-bit LFSRs)

## Next Steps

If VGA is working:
1. Observe trail patterns forming
2. Test speed controls (BTNU/BTND)
3. Test randomization (BTNL)
4. Let simulation run for several minutes to see pattern development

If VGA is not working:
1. Follow troubleshooting steps above
2. Reprogram with test pattern bitstream if hardware issue suspected
3. Check pin connections on Basys3 board

## Commands to Reprogram

### Main Slime Simulator (current)
```bash
vivado -mode batch -source program_main.tcl
```

### VGA Test Pattern (diagnostic)
```bash
vivado -mode batch -source program_test.tcl
```

Both require `hw_server` to be running:
```bash
hw_server &
```

---
**Last Updated**: 2025-11-24 09:38 UTC
**Vivado Version**: 2025.2
**FPGA Board**: Basys3 (XC7A35T)
**Build Status**: ✅ All builds successful
**Programming Status**: ✅ Main design programmed
