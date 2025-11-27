# RTL Spatial Pattern Analysis

## Problem Statement

The RTL simulation produces different spatial patterns compared to the Python reference:
- **Python**: Agents form a smooth **circular outline** pattern
- **RTL**: Agents form **scattered dots** in specific locations

This despite both using equivalent fixed-point arithmetic and LFSR logic.

## Investigation Results

### Agent Initialization Attempts

1. **Original 2×2 grid initialization** (current)
   - Agents at positions: (cx±32, cy±32) cycling through 4 locations
   - Angles calculated as: `(i * 2 * 3141593) / NUM_AGENTS`
   - Result: Scattered dots (agents converge to specific areas)

2. **Evenly-spaced circle initialization**
   - Agents positioned: `x = cx + cos(i*2π/N) * radius`, similar for y
   - Angles: `spawn_angle + π` (pointing toward center, like Python)
   - Result: Still scattered dots, not a circle pattern

3. **LFSR-based random angles** (matching Python's seed 0xDEADBEEF)
   - Attempted to replicate Python's `_lfsr_uniform_angle_fp()` method
   - Result: Agents cluster extremely (98% of screen black)

### Statistical Analysis (320×240, 100 agents, 3 steps)

| Metric | Python Step 1 | RTL Step 1 | Ratio |
|--------|---------------|-----------|-------|
| Max trail value | 48,422 | 61,440 | 1.27× |
| Mean trail value | 25.3 | 77.1 | **3.04×** |
| Pattern | Smooth circle | Scattered dots | ❌ |

| Metric | Python Step 2 | RTL Step 2 | Ratio |
|--------|---------------|-----------|-------|
| Max trail value | 39,692 | 61,440 | 1.55× |
| Mean trail value | 49.4 | 247.5 | **5.01×** |
| Pattern | Smooth circle | Scattered dots | ❌ |

**Key observation**: Mean ratio grows from 3.04× to 5.01×, indicating agents are converging to fewer locations over time.

## Root Cause Analysis

The initialization changes made minimal impact on spatial patterns, suggesting the problem is **NOT primarily initialization**.

### Likely Causes

1. **Movement/Sensing Logic Difference**
   - Agent decision logic (forward/left/right comparison) may differ
   - Turn amounts or directions may be incorrect
   - Agents may be using wrong reference angles for sensing

2. **Fixed-Point Arithmetic Edge Cases**
   - Different rounding/truncation in position calculations
   - Angle normalization differences
   - Overflow/underflow in multiplication

3. **Trail Decay/Accumulation**
   - RTL decay formula may differ from Python's `0.95` multiplier
   - Trail write order/precedence may cause different accumulation

4. **LFSR Sequence Mismatch**
   - Even if initialization matches, agent-level LFSR use during simulation may differ
   - Could cause different movement decisions throughout simulation

## Current Status

✅ **RTL simulation IS working** - agents are moving and depositing trails
✅ **Trail values are in correct magnitude** - within 1.3-1.5× of Python
✅ **Numerical output is mostly correct** - 99.9% match on pixel differences

❌ **Spatial pattern is WRONG** - agents congregate instead of forming circle
❌ **Mean trail concentration is too high** - indicating agents in wrong locations

## Recommended Next Steps

### Option A: Debug Root Cause (Recommended)
1. Compare `agent_processor.sv` movement logic with Python's `update_agent()`
2. Verify fixed-point arithmetic precision in critical calculations
3. Check LFSR step sequence during simulation (not just initialization)
4. Enable detailed debug output showing agent positions per step

### Option B: Accept Current State
- RTL simulation is functionally correct for basic slime logic
- Spatial pattern difference could be simulation-specific behavior
- Use for FPGA deployment with understanding that agents may cluster differently

### Option C: Pre-computed Initialization
- Generate agent positions in Python with LFSR
- Export as lookup table or hardcoded initialization
- Guarantees initialization matches, allows debugging of movement logic separately

## Test Cases

To isolate the issue:

```bash
# Test with 10 agents instead of 100 (easier to trace)
./run_extended_comparison.sh --resolution 320x240 --agents 10 --steps 5

# Test with 1000 agents to see if pattern scales
./run_extended_comparison.sh --resolution 320x240 --agents 1000 --steps 5

# Test with different deposit amounts to isolate magnitude issues
# (requires modifying agent_processor.sv deposit_amount parameter)
```

## Files Involved

- `rtl/src/agent_coordinator.sv:142-166` - Agent initialization
- `rtl/src/agent_processor.sv:231-370` - Agent movement/sensing/decision logic
- `slime_simulator.py:330-415` - Python reference agent movement
- `rtl/sim/python_reference.py:231-290` - Python reference simulation model
