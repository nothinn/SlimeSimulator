# Trig Lookup Latency Analysis

## Problem Statement

The agent_processor uses a **registered trig_lut** with **1-cycle latency**, but there's a potential mismatch in how the latency is accounted for during the SENSORY_DECISION → CALC_MOVE_X → CALC_MOVE_Y → UPDATE_POS pipeline.

## Trig LUT Implementation Details

### trig_lut.sv: Registered Outputs (Lines 32-36)
```verilog
always_ff @(posedge clk) begin
    sin_out <= sin_rom[angle_idx];
    cos_out <= cos_rom[angle_idx];
end
```

**Key fact**: sin_out and cos_out are **registered**, meaning:
- **Cycle N**: angle_idx changes (combinatorial)
- **Cycle N+1**: sin_out/cos_out update with sin/cos of the angle that was indexed in cycle N

### agent_processor.sv: Trig Index Selection (Lines 362-376)
```verilog
always_comb begin
    case (state)
        CALC_SENSOR_F_X, CALC_SENSOR_F_Y:
            current_sense_angle = angle_reg;
        CALC_SENSOR_L_X, CALC_SENSOR_L_Y:
            current_sense_angle = angle_reg + sensor_angle;
        CALC_SENSOR_R_X, CALC_SENSOR_R_Y:
            current_sense_angle = angle_reg - sensor_angle;
        CALC_MOVE_X, CALC_MOVE_Y:
            current_sense_angle = new_angle;  // CRITICAL: new_angle is set in SENSORY_DECISION
        default:
            current_sense_angle = angle_reg;
    endcase
    trig_angle_idx = angle_to_idx(current_sense_angle);  // Combinatorial
end
```

## The Timing Bug

### Timeline Analysis

Let me trace what happens during the critical SENSORY_DECISION → CALC_MOVE_X → CALC_MOVE_Y sequence:

```
CYCLE N (SENSORY_DECISION state):
  - state = SENSORY_DECISION
  - current_sense_angle = angle_reg (SENSORY_DECISION not in trig index case statement!)
  - trig_angle_idx = angle_to_idx(angle_reg)  [1-cycle old angle!]
  - At end of cycle: new_angle <= updated_angle (decision logic)
  - At end of cycle: dx <= mult_result, dy <= mult_result (NO! These don't update in SENSORY_DECISION)

CYCLE N+1 (CALC_MOVE_X state):
  - state = CALC_MOVE_X
  - new_angle has the new angle from SENSORY_DECISION decision
  - current_sense_angle = new_angle [CORRECT - combinatorial]
  - trig_angle_idx = angle_to_idx(new_angle) [CORRECT INDEX SET]
  - mult_a = cos_val, mult_b = move_speed
  - cos_val is STALE! (it's still holding sin/cos from previous state's trig lookup)
  - mult_result = 0 (or garbage) because cos_val hasn't updated yet
  - At end of cycle: dx <= mult_result [WRONG VALUE!]

CYCLE N+2 (CALC_MOVE_Y state):
  - state = CALC_MOVE_Y
  - current_sense_angle = new_angle [still combinatorial]
  - trig_angle_idx is still set (combinatorial)
  - sin_out has NOW updated with sin(new_angle) from the trig lookup we set in CALC_MOVE_X
  - sin_val now has CORRECT sin(new_angle)
  - mult_a = sin_val, mult_b = move_speed
  - mult_result = sin(new_angle) * move_speed [CORRECT VALUE]
  - At end of cycle: dy <= mult_result [CORRECT VALUE]

CYCLE N+3 (UPDATE_POS state):
  - state = UPDATE_POS
  - sin_out has updated AGAIN (with sin of new_angle), but we already captured it in dy
  - dx is STALE (either 0 or previous agent's value)
  - dy is CORRECT (sin * speed from CALC_MOVE_Y)
  - new_x <= x_reg + dx [WRONG because dx is stale!]
  - new_y <= y_reg + dy [CORRECT]
```

## Root Cause Identified

**The bug is NOT in the trig_lut itself - the bug is in the state machine not waiting for the trig_lut output to become valid after setting a new index.**

The current code:
1. Sets `trig_angle_idx` combinatorially in SENSORY_DECISION (to old angle_reg)
2. Moves to CALC_MOVE_X and immediately tries to use sin_val/cos_val
3. But sin_val/cos_val are from the PREVIOUS trig_angle_idx, not the new one
4. The new angle doesn't get looked up until CALC_MOVE_X, and the result doesn't appear until CALC_MOVE_Y
5. This causes movement to use a MIX of old and new trig values

## Why the 2x Pattern Occurs

Looking at the pattern: **0x, 2x, 1x, 2x, 1x, 2x...**

This suggests:
- **Step 0→1 (2x)**: Uses wrong trig values (perhaps from initialization or previous agent)
- **Step 1→2 (0x)**: Uses all zero values (trig lookup stalled?)
- **Step 2→3 (1x)**: Correct
- **Step 3→4 (2x)**: Doubles again (wrong values)
- Repeats pattern...

The alternation suggests that sometimes `cos_val` and `sin_val` are being captured from different cycles, or the trig lookup is returning doubled values in certain states.

## Solution Approach

The fix requires one of two approaches:

### Option A: Add Wait State After Setting Trig Index
When new_angle is computed, wait one additional cycle before using sin/cos:

```verilog
SENSORY_DECISION: next_state = WAIT_NEW_ANGLE;  // NEW STATE
WAIT_NEW_ANGLE:   next_state = CALC_MOVE_X;     // NEW STATE
CALC_MOVE_X:      next_state = CALC_MOVE_Y;
```

This adds 1 cycle latency but ensures sin/cos are valid.

### Option B: Dual-Port Trig Lookup
Pre-compute the new angle's trig values while still in SENSORY_DECISION:
- One port: reads trig for sensor calculations
- Other port: reads trig for movement using pre-computed new_angle

Then CALC_MOVE_X can immediately use the pre-computed values.

### Option C: Pipelined Multiply
Register the trig lookup results into CALC_MOVE_X state, and move the multiply to a dedicated stage.

## Critical Questions to Answer

1. **When exactly does trig_angle_idx change during SENSORY_DECISION→CALC_MOVE_X transition?**
   - It should change from `angle_to_idx(angle_reg)` to `angle_to_idx(new_angle)` combinatorially

2. **What values are sin_val and cos_val actually holding when we enter CALC_MOVE_X?**
   - If they're holding sensor-related trig values, that could explain the 2x error
   - Need to trace what the previous state was

3. **Is the multiply result actually 2x or is dx/dy being captured wrongly?**
   - The symptom is 2x movement, but is the multiply computing 2x or is the result being used twice?

## Next Debugging Steps

1. Create a Verilator testbench that dumps sin_val, cos_val, trig_angle_idx, and mult_result each cycle
2. Trace through a specific agent's movement across steps 0→1→2→3
3. Compare against Python reference to identify exactly when values diverge
4. Implement one of the fixes above once root cause is confirmed
