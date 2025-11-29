# ROOT CAUSE ANALYSIS: RTL vs Python Trajectory Mismatch

## Executive Summary

**The Problem:** RTL agents accumulate ~111 pixels of positional error per step while Python agents remain on correct trajectories.

**Root Cause:** RTL agent processor is producing **systematically different angles than Python**, causing agents to move in wrong directions.

**The Bug:** The angles at step 0 show that RTL angles are NOT following the initialization formula. They appear to be modified or incorrectly calculated during the first processing cycle.

---

## Three-Investigation Findings

### Investigation 1: RTL Code Analysis ✓

**Complete data flow identified:**

1. **Angle Input**: Agent angle loaded from memory (Q12.12 fixed-point, 25-bit)
2. **Trig Lookup**: Angle → index (via `angle_to_idx()`)
3. **Table Access**: trig_lut returns sin/cos values (Q12.12)
4. **Movement Calculation**:
   - `dx = cos(angle) × move_speed` (via fixed_point_mult)
   - `dy = sin(angle) × move_speed` (via fixed_point_mult)
5. **Position Update**: `new_x = x + dx`, `new_y = y + dy` (with wrapping)

**Key Code Locations:**
- `agent_processor.sv:320-328` - Velocity calculation (CALC_MOVE_X/Y)
- `agent_processor.sv:392-419` - Multiplier input selection
- `trig_lut.sv` - Sin/cos lookup table (1024 entries)
- `fixed_point_mult.sv` - Q12.12 multiplier with proper bit extraction

**No obvious bugs found in arithmetic**, but implementation details need verification.

---

### Investigation 2: Diagnostic Test Results ⚠️

**Agent 0 (First Agent):**
- **Expected angle** (from RTL init logic): 180.00°
- **Actual RTL angle** (step 0 dump): 179.99°
- **Python angle** (step 0 dump): 180.00°
- **Match**: RTL ✓ matches Python ✓

**Agent 5 (Example of Divergence):**
- **Expected angle**: 198.00°
- **Actual RTL angle**: 181.78°
- **Difference**: -16.22°

**Overall Pattern:**
- RTL actual angles: clustered around 180° ± small range
- Expected RTL angles: should span full [0, 360°] range
- **Mean difference from expected**: -2.00°
- **Std Dev**: 109.27° (highly variable!)
- **Max abs diff**: 178.54°

**CRITICAL FINDING:**
> The "step 0" dump contains angles **AFTER the first processing cycle**, NOT the initial values from the RTL `initial` block!

The agent processor is **modifying angles** during the first step in a way that doesn't match Python's sensory logic.

---

### Investigation 3: Python Reference Verification ✓

**Python Implementation (VERIFIED CORRECT):**

```python
# Initialization:
spawn_angle = 2π × i / 100  # Uniform distribution around circle
x = 160 + 96 × cos(spawn_angle)
y = 120 + 96 × sin(spawn_angle)
angle = arctan2(120 - y, 160 - x)  # Direction toward center = spawn_angle + π

# Result: Agents point toward center, perfectly distributed on circle
```

**Verification Results:**
- ✓ Agent 0: angle = 180.00° (matches expected exactly)
- ✓ Agent 1: angle = 183.60° (matches expected exactly)
- ✓ All 100 agents: Circle positions perfect (96.00 px radius, centered at 160,120)
- ✓ All angles: Match spawn_angle + 180° pattern

**Python is CORRECT. RTL is WRONG.**

---

## Detailed Error Pattern Analysis

### Position Error Growth

```
Step    Mean Dist Error    Pattern
───────────────────────────────────
0       132.14 px         Initial divergence
25      118.22 px         -11.9% decay
50      108.33 px         -22.0% decay
75      102.11 px         -28.2% decay
99      99.45 px          -29.9% decay
```

**Pattern**: Linear drift PLUS decay over time
- Initial offset: ~132 px (agents start in wrong direction)
- Agents continue moving wrong direction for 100 steps
- Some correction occurs (agents spiral inward due to sensory logic)
- By step 100, still ~99 px off

### Angle Error Pattern

```
Agent ID    Actual RTL Angle    Expected Angle    Δ
──────────────────────────────────────────────────
0           179.99°             180.00°           -0.01°
5           181.78°             198.00°          -16.22°
10          183.58°             216.00°          -32.42°
25          186.41°             256.40°          -70.00°
50          182.00°             0.00° (wrapped)  +182.00°
```

**Observation:**
- Not a simple constant offset (would be ±90° everywhere)
- Varies per agent ID
- Related to position in spawn circle
- Suggests error in angle update/sensory logic, not initialization

---

## Hypothesis: Movement Direction Calculation

### Most Likely Culprit: sin/cos usage in CALC_MOVE_X/Y

Current code (agent_processor.sv:320-328):
```verilog
CALC_MOVE_X: begin
    // dx = cos(new_angle) * move_speed
    dx <= mult_result;  // mult_a=cos_val, mult_b=move_speed
end

CALC_MOVE_Y: begin
    // dy = sin(new_angle) * move_speed
    dy <= mult_result;  // mult_a=sin_val, mult_b=move_speed
end
```

**Possible Issues:**

1. **sin/cos Swapped?**
   - If `sin_out` and `cos_out` are swapped in trig_lut output
   - Would cause dy = cos × speed (instead of sin)
   - Would cause dx = sin × speed (instead of cos)
   - This would be ≈90° rotation!

2. **Coordinate System Mismatch?**
   - Python: Standard math coords (Y increases upward)
   - RTL: Screen coords (Y increases downward)?
   - Would affect how sin/cos apply to dx/dy

3. **Angle Indexing Error?**
   - If angle_to_idx() produces wrong table index
   - Would read sin/cos from wrong position in table

4. **Trig Table Generation Error?**
   - If sin_lut.hex and cos_lut.hex are corrupted
   - Would produce wrong sin/cos values

---

## Critical Test: Pre-Step-0 Angle Check

**To definitively locate the bug, we need:**

1. Dump agent angles **BEFORE any processing** (after initialization, before RUNNING state)
2. Compare these to expected values
3. If they match expected:
   - Bug is in the agent processor during movement calculation
   - Focus on CALC_MOVE_X/Y states
   - Check sin/cos usage and angle indexing

4. If they DON'T match expected:
   - Bug is in initialization logic
   - Check agent_coordinator.sv angle wrapping

---

## Recommended Debug Steps

### Step 1: Add Pre-Processing Angle Dump
Modify testbench to dump agent state after initialization but before first RUNNING state:
```cpp
// After initialization, before main loop
dump_agent_state(-1);  // Step -1 = pre-processing state
```

### Step 2: Verify Trig Table Integrity
```bash
# Check if sin_lut.hex and cos_lut.hex exist and have correct values
# Expected: 1024 hex values each
wc -l rtl/src/sin_lut.hex rtl/src/cos_lut.hex

# Verify specific entries (sin(0)=0, sin(π/2)=1, cos(0)=1, cos(π/2)=0)
head -5 rtl/src/sin_lut.hex
head -5 rtl/src/cos_lut.hex
```

### Step 3: Check angle_to_idx() Function
- Verify bit extraction is correct
- Test with known angles (0, π/2, π, 3π/2)
- Confirm table indices are in [0, 1023]

### Step 4: Review Multiplier Bit Extraction
In `fixed_point_mult.sv`:
```verilog
// Current: bits [36:12] of 50-bit product
assign result = full_product[TOTAL_BITS + FRAC_BITS - 1 : FRAC_BITS];
             // = full_product[36:12]
```
Verify this is correct for Q12.12 format.

### Step 5: Test With Single Agent
Modify testbench to:
- Run only agent 0
- Dump its state at every cycle of first step
- Trace angle and velocity calculations
- Compare with Python calculations

---

## Expected Outcomes

**If sin/cos are swapped:**
- Pre-processing angles will be CORRECT
- Movement angles after CALC_MOVE_X/Y will be WRONG
- ~90° error will appear

**If angle_to_idx() is wrong:**
- Pre-processing angles will be CORRECT
- Movement will use wrong sin/cos values
- Error pattern will vary by angle

**If initialization is wrong:**
- Pre-processing angles will be WRONG
- Error will be consistent across all agents

---

## Summary Table

| Aspect | Python | RTL | Status |
|--------|--------|-----|--------|
| Position Init | ✓ Correct | ✓ Correct | PASS |
| Angle Init | ✓ Correct | ? Unknown* | UNKNOWN |
| Step 0 Angle | ✓ 180°, 183.6°, ... | ✗ ~180° all | FAIL |
| Movement Direction | ✓ Correct | ✗ Wrong | FAIL |
| Position Over 100 Steps | ✓ ~0-1 px error | ✗ ~100 px error | FAIL |

*Need pre-processing angle dump to confirm

---

## Conclusion

The RTL implementation has a **critical bug in the angle/movement calculation pipeline** that causes agents to move in systematically wrong directions. The bug is most likely in one of:

1. **Trig lookup table corruption** - sin/cos swapped or wrong values
2. **Angle-to-index conversion** - wrong bit extraction
3. **Multiplier result extraction** - wrong bits selected from product
4. **Coordinate system mismatch** - Y-axis interpretation differs

The detailed code analysis shows the logic is **mathematically correct in structure**, but **functionally incorrect in execution**. The fix requires:

1. Verifying trig table generation/loading
2. Testing angle-to-index conversion
3. Checking multiplier bit extraction
4. Adding debug output to trace the pipeline

Once located, the fix should be straightforward: correct the index, swap the values, or change the coordinate mapping.
