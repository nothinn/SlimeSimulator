# Resource Estimation for Slime Simulator on Basys3

## Basys3 FPGA Resources (Artix-7 XC7A35T-1CPG236C)

| Resource | Available |
|----------|-----------|
| LUTs | 20,800 |
| Flip-Flops | 41,600 |
| Block RAM (36Kb) | 50 (1,800 Kb total) |
| Block RAM (18Kb) | 100 |
| DSP48E1 | 90 |
| I/O Pins | 106 (usable) |

## Design Resource Estimates

### 1. Trail Map Memory (Dominant Resource)

**Requirement:** 640 x 480 x 8 bits = 307,200 bytes = 2,457,600 bits = **2.4 Mb**

**Problem:** This exceeds the 1.8 Mb BRAM available!

**Solutions:**
| Option | Memory Needed | Notes |
|--------|---------------|-------|
| A. Full 640x480 | 2.4 Mb | Requires external SRAM (Basys3 has none) |
| B. Reduced 320x240 | 614 Kb | 34 x 18Kb BRAMs, fits! |
| C. Reduced 160x120 | 154 Kb | 9 x 18Kb BRAMs, plenty of room |
| D. 1-bit trail (B&W) | 307 Kb | 17 x 18Kb BRAMs, fits at full res |

**Recommended:** Option B (320x240) provides good visual quality while fitting in BRAM.

### 2. Agent Memory

**Per agent storage:**
- Position X: 25 bits (Q12.12 fixed-point)
- Position Y: 25 bits
- Angle: 10 bits
- **Total: 60 bits per agent**

| Agents | Memory | BRAMs (18Kb) |
|--------|--------|--------------|
| 100 | 6,000 bits | 1 |
| 500 | 30,000 bits | 2 |
| 1,000 | 60,000 bits | 4 |
| 5,000 | 300,000 bits | 17 |

### 3. Trig Lookup Tables

**Sin/Cos tables:**
- 1024 entries x 25 bits x 2 tables = 51,200 bits = **3 x 18Kb BRAMs**

### 4. Logic Resources

| Module | Est. LUTs | Est. FFs | DSPs |
|--------|-----------|----------|------|
| VGA Controller | 100 | 80 | 0 |
| LFSR (32-bit) | 40 | 32 | 0 |
| Fixed-Point Mult | 50 | 50 | 1-2 |
| Trig LUT | 30 | 50 | 0 |
| Agent Processor | 500 | 300 | 2-4 |
| Debouncer (5x) | 100 | 200 | 0 |
| State Machine | 100 | 80 | 0 |
| Trail Memory Ctrl | 200 | 100 | 0 |
| **Subtotal** | **1,120** | **892** | **3-6** |

### 5. Debug Infrastructure (Optional)

| Module | Est. LUTs | Est. FFs | BRAMs |
|--------|-----------|----------|-------|
| ILA (4K deep, 8 probes) | 500 | 1,000 | 4 |
| VIO (4 in, 4 out) | 200 | 100 | 0 |
| JTAG-to-AXI | 800 | 500 | 0 |
| Debug Wrapper | 300 | 200 | 0 |
| **Debug Total** | **1,800** | **1,800** | **4** |

## Total Resource Summary

### Minimal Build (320x240, 1000 agents, no debug)

| Resource | Used | Available | Utilization |
|----------|------|-----------|-------------|
| LUTs | ~1,500 | 20,800 | 7% |
| Flip-Flops | ~1,200 | 41,600 | 3% |
| BRAM (18Kb) | 38 + 4 + 3 = 45 | 100 | 45% |
| DSP48 | 4 | 90 | 4% |

### Debug Build (320x240, 1000 agents, full debug)

| Resource | Used | Available | Utilization |
|----------|------|-----------|-------------|
| LUTs | ~3,300 | 20,800 | 16% |
| Flip-Flops | ~3,000 | 41,600 | 7% |
| BRAM (18Kb) | 45 + 4 = 49 | 100 | 49% |
| DSP48 | 4 | 90 | 4% |

### Maximum Configuration (320x240, 5000 agents, debug)

| Resource | Used | Available | Utilization |
|----------|------|-----------|-------------|
| LUTs | ~5,000 | 20,800 | 24% |
| Flip-Flops | ~4,500 | 41,600 | 11% |
| BRAM (18Kb) | 38 + 17 + 3 + 4 = 62 | 100 | 62% |
| DSP48 | 6 | 90 | 7% |

## Recommendations

1. **Resolution:** Use 320x240 (quarter resolution) for display, with 2x upscaling for VGA output

2. **Agent Count:** Start with 1000 agents, can increase to ~5000 with current design

3. **Memory Optimization:**
   - Use single-port BRAM for trail map where possible
   - Consider 4-bit trail values (16 intensity levels) to halve memory

4. **Performance:**
   - At 100 MHz, can process ~100,000 agents per frame (60 FPS)
   - 320x240 resolution with 1000 agents is easily achievable

## Required Design Changes

To fit in Basys3 BRAM, modify parameters in `slime_top.sv`:

```systemverilog
module slime_top #(
    parameter NUM_AGENTS   = 1000,
    parameter WIDTH        = 320,    // Changed from 640
    parameter HEIGHT       = 240     // Changed from 480
) (
```

And update VGA controller to upscale 2x:
```systemverilog
// In trail address calculation:
assign trail_addr_a = (pixel_y >> 1) * (WIDTH/2) + (pixel_x >> 1);
```
