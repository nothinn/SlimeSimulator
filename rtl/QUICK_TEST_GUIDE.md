# Quick Test Guide - Basys3 Slime Simulator

## FPGA Programming Status: SUCCESS
**Programmed:** 2025-11-24 15:47
**Device:** xc7a35t_0 (Basys3 Artix-7)
**Bitstream:** slime_top.bit

---

## Expected Behavior Summary

### Power-On (Before BTNC)
- VGA: **BLACK SCREEN** (design starts idle)
- LED[4]: **OFF** (not running)
- LED[3:0]: Shows **8** (default speed)

### After Pressing BTNC (Center Button)
- VGA: **GRADIENT PATTERN** appears in top-left corner
  - First 1000 pixels (positions 0-999)
  - Pattern: Dark gray → Medium gray (values 0-231)
  - Updates at ~60 Hz (once per frame)
- LED[4]: **ON** (simulation running)
- LED[15:8]: **Rapidly changing** (LFSR active)

---

## Quick Test Steps

1. **Verify Initial State**
   - VGA should be BLACK
   - LED[4] should be OFF

2. **Start Simulation**
   - Press BTNC (center button)
   - VGA should show pattern immediately
   - LED[4] should turn ON

3. **Test Pause**
   - Flip SW[0] ON → pattern freezes
   - Flip SW[0] OFF → pattern resumes

4. **Test Speed**
   - Press BTNU → LED[3:0] increases (speed up)
   - Press BTND → LED[3:0] decreases (speed down)

5. **Stop Simulation**
   - Press BTNC again
   - VGA returns to BLACK
   - LED[4] turns OFF

---

## Troubleshooting

### VGA is BLACK after pressing BTNC:
1. Check LED[4] - is it ON? (If not, press BTNC again)
2. Check VGA cable connection
3. Check monitor input selection
4. Look carefully at top-left corner - pattern may be subtle

### LEDs not responding:
1. Verify FPGA is programmed (should happen automatically after bitstream load)
2. Try pressing buttons firmly
3. Check that buttons are not mechanically stuck

### Pattern not visible but LEDs working:
1. Adjust monitor brightness/contrast
2. Pattern is in top-left 1000 pixels (very small area)
3. Try different VGA monitor if available

---

## LED Status Reference

| LED | Meaning | Expected |
|-----|---------|----------|
| [3:0] | Speed level | 8 initially, 0-15 range |
| [4] | Simulation running | 0=idle, 1=running |
| [5] | Pause state | 0=running, 1=paused |
| [7:6] | State machine | 0=IDLE, 2=RUN_AGENTS |
| [15:8] | LFSR random | Changes when running |

---

## Control Reference

### Buttons (Active High)
- **BTNC (Center):** Start/Stop simulation
- **BTNU (Up):** Speed up (LED[3:0] increases)
- **BTND (Down):** Speed down (LED[3:0] decreases)
- **BTNL (Left):** Randomize LFSR seed
- **BTNR (Right):** Reserved (not used)

### Switches
- **SW[0]:** Pause (1=paused, 0=running)
- **SW[15:1]:** Not used

---

## Critical Fix Applied

**Previous Issue:** Memory write enable was hardcoded to 0, preventing pattern display

**Fix:** Line 318 in slime_top.sv changed from:
```systemverilog
assign trail_we_b = 1'b0;  // BROKEN - never writes!
```
To:
```systemverilog
assign trail_we_b = (sim_state == SIM_RUN_AGENTS) && !sim_pause;  // FIXED
```

**Result:** Pattern generator can now write to memory, making output visible

---

## What You Should See

```
Power On              Press BTNC           Toggle SW[0]
+---------+          +---------+          +---------+
|         |          |█▓▒░     |          |█▓▒░     |
|  BLACK  |    →     |         |    →     | FROZEN  |
| SCREEN  |          | Pattern |          | Pattern |
|         |          | Updates |          |         |
+---------+          +---------+          +---------+
LED[4]=0             LED[4]=1             LED[4]=1
                                          LED[5]=1
```

---

## Design Parameters

- **Display Resolution:** 640x480 @ 60Hz (VGA)
- **Internal Resolution:** 160x120 (trail map)
- **Number of Agents:** 1000
- **Clock Frequency:** 100 MHz (system), 25 MHz (VGA)
- **Memory:** 4 BRAM tiles (19,200 bytes)
- **Pattern:** Agent index values (0-231) at positions 0-999

---

## For Detailed Information

See: `/home/reson/SlimeSimulator/rtl/FPGA_PROGRAMMING_REPORT.md`

Contains:
- Complete programming log
- Timing and resource analysis
- Detailed troubleshooting guide
- Implementation architecture
- Success criteria checklist
