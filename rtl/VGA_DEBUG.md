# VGA Debugging Guide

**Status**: Solid color diagnostic design programmed to FPGA
**Bitstream**: `vivado_project_solid/vga_solid_test.runs/impl_1/vga_solid_color.bit` (269 KB)

---

## Quick Test Procedure

### Step 1: Check LEDs (Power & Clock Verification)
Look at the FPGA board LEDs. You should see:
- **LED[3]** (Reset): Should be ON (bright)
- **LED[4]** (25MHz Clock): Should BLINK rapidly (~6 times per second visible as flicker)
- **LED[6]** (Frame Start): Should BLINK noticeably slower (~1 per second)
- **LED[7]** (Frame Counter): Should BLINK at ~2Hz (alternating on/off)

**If these LEDs are NOT blinking:**
→ Clock generation problem - FPGA may not be running properly

---

### Step 2: Test Color Output
The design displays a solid color based on **SW[2:0]** setting:

| SW[2:0] | Color | Expected Display |
|---------|-------|------------------|
| 000 | Red | Solid red screen |
| 001 | Green | Solid green screen |
| 010 | Blue | Solid blue screen |
| 011 | Yellow | Solid yellow screen |
| 100 | Cyan | Solid cyan screen |
| 101 | Magenta | Solid magenta/pink screen |
| 110 | White | Solid white screen |
| 111 | Blinking | White screen blinking at 30Hz |

**Test Procedure:**
1. Set SW[0]=0, SW[1]=0, SW[2]=0 (Red)
2. Look at monitor - should show solid RED color
3. Try different switch combinations
4. For setting 111 (White Blinking), the screen should pulse on/off

---

## Diagnostic Decision Tree

### Monitor Shows BLACK Screen

**Check 1: Are the LEDs blinking?**
- YES → Go to "Check 2"
- NO → **PROBLEM: FPGA not running**
  - Power cycle the board (unplug, wait 5s, replug)
  - Verify DONE LED on FPGA is lit
  - Try reprogramming bitstream

**Check 2: Try different switch positions**
- Does color change? YES → Go to "Check 3"
- Does color NOT change? → **PROBLEM: Data output blocked**
  - Check VGA cable pin connections
  - Test pin continuity with multimeter

**Check 3: Monitor definitely recognizes HDMI/DVI port?**
- Try connecting monitor to different port
- Try turning monitor input auto-detect on
- Check if monitor shows "No Signal" or stays completely dark

**If still black:** → Likely issue is **VGA color channels not connected**
- Verify pins G19, H19, J19, N19 for Red
- Verify pins J17, H17, G17, D17 for Green
- Verify pins N18, L18, K18, J18 for Blue
- Use multimeter to test continuity from FPGA pins to VGA connector

---

### Monitor Shows Grayscale (Not Colored)

**Possible causes:**
1. Only one color channel working (check if screen is pure red, green, or blue)
2. DAC resistor network issue
3. Pin connection problem

**Test:**
- Set SW to 111 (White) - if you see white/gray, at least some channels work
- Set SW to 001 (Green) - should be pure green if only green channel works
- If only one color displays → That channel's pins are connected, others are not

---

### Monitor Shows COLOR But Wrong Resolution

**Possible causes:**
1. Sync signal timing incorrect
2. Monitor not detecting 640×480 signal
3. Refresh rate mismatch (should be 60Hz)

**Test:**
- Monitor should detect 640×480@60Hz automatically
- Check monitor's input info (usually press "Input" button)
- Try forcing 640×480@60Hz in monitor settings

---

### Monitor Shows Noise/Static Pattern

**Possible causes:**
1. Cable connection loose
2. Ground connection issues
3. Signal integrity problem

**Test:**
- Reseat VGA cable firmly at both ends
- Try different VGA cable
- Check for bent pins in connector

---

## LED Pin Mapping

For reference, the diagnostic design outputs:

```
LED[2:0] = SW[2:0]              // Selected color (should match switch)
LED[3]   = rst_n                // Reset status (should be ON)
LED[4]   = clk_25mhz            // 25MHz clock (should blink)
LED[5]   = pixel_valid          // Active pixels (usually ON)
LED[6]   = frame_start          // Frame sync pulse (blinks ~1Hz)
LED[7]   = frame_counter        // 30Hz blink indicator
LED[8]   = vga_hs               // Horizontal sync signal
LED[9]   = vga_vs               // Vertical sync signal
```

---

## VGA Pin Connections

**Basys3 to VGA Connector (female):**

| Signal | FPGA Pin | VGA Pin | Connector Pin |
|--------|----------|---------|---------------|
| Red[0] | G19 | Red | 1 |
| Red[1] | H19 | Red | 1 |
| Red[2] | J19 | Red | 1 |
| Red[3] | N19 | Red | 1 |
| Green[0] | J17 | Green | 2 |
| Green[1] | H17 | Green | 2 |
| Green[2] | G17 | Green | 2 |
| Green[3] | D17 | Green | 2 |
| Blue[0] | N18 | Blue | 3 |
| Blue[1] | L18 | Blue | 3 |
| Blue[2] | K18 | Blue | 3 |
| Blue[3] | J18 | Blue | 3 |
| H-Sync | P19 | H-Sync | 13 |
| V-Sync | R19 | V-Sync | 14 |
| Ground | GND | Ground | 5,6,7,8,10 |

---

## Advanced Troubleshooting

### Check Sync Signals
- Set SW to 110 (White) for maximum brightness
- Monitor LEDs[8:9] - these show the sync signals
- LED[8] (HSYNC) should blink rapidly (~31.5 kHz)
- LED[9] (VSYNC) should blink slowly (~60 Hz)

### Check Pixel Clock
- LED[4] (clk_25mhz) should blink visibly
- If not blinking: Clock divider may have failed
- Try power cycling FPGA

### Verify FPGA Configuration
Run this command to check FPGA status:
```bash
vivado -mode batch -source check_fpga.tcl 2>&1 | grep -i "status\|startup"
```

---

## If Solid Color Test WORKS

If you see a solid color on screen, the VGA hardware is working! Then:

1. **Reprog ram with VGA test pattern:**
   ```bash
   vivado -mode batch -source program_test.tcl
   ```
   Should display test patterns with color bars, gradients, etc.

2. **If test pattern works, reprogram main design:**
   ```bash
   vivado -mode batch -source program_main.tcl
   ```
   Should display animated slime trail patterns

3. **Button controls for main design:**
   - BTNC: Start/Stop simulation
   - BTNU/BTND: Speed up/down
   - BTNL: Randomize agent positions
   - BTNR: Hard reset

---

## If NOTHING Works

1. **Check FPGA power:**
   - Verify USB cable connection (provides power to Basys3)
   - Check if power LED on board is lit

2. **Check VGA cable:**
   - Try a different cable
   - Test cable on known-working computer
   - Look for bent pins in connectors

3. **Check monitor:**
   - Try different monitor if available
   - Ensure monitor is powered on
   - Check monitor input is set to VGA (not HDMI)

4. **Factory reset FPGA:**
   - Unplug USB from Basys3
   - Wait 10 seconds
   - Plug back in
   - Reprogram

---

## Contact Support

If none of these steps resolve the issue, document:
1. What LEDs are blinking/not blinking
2. Whether monitor shows any signal
3. What happens with different switch settings
4. Whether this is the first time testing VGA or it worked before

---

**Last Updated**: 2025-11-24 13:25 UTC
**Diagnostic Version**: 1.0
