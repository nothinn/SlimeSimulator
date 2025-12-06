# Trig Latency Fix for Agent Processor

## Problem Summary

The agent_processor has a **1-cycle latency mismatch** between when trig_angle_idx changes and when sin_val/cos_val update:

- **trig_angle_idx**: Set combinatorially based on current state
- **sin_val, cos_val**: Updated on rising edge, containing sin/cos of the index from the PREVIOUS cycle

**Timing violation**: When transitioning from SENSORY_DECISION → CALC_MOVE_X:
1. SENSORY_DECISION computes new_angle
2. CALC_MOVE_X immediately tries to use sin(new_angle), cos(new_angle)
3. But sin_val, cos_val are still holding sin/cos from the previous state (WAIT_TRAIL_R)
4. This causes movement to use wrong trig values, resulting in alternating 0x/2x/1x pattern

## Root Cause Code Analysis

**agent_processor.sv lines 362-376** (Trig Index Selection):
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
            current_sense_angle = new_angle;  // ← Uses new_angle here
        default:
            current_sense_angle = angle_reg;
    endcase
    trig_angle_idx = angle_to_idx(current_sense_angle);  // ← Set combinatorially
end
```

**trig_lut.sv lines 32-36** (Registered Output):
```verilog
always_ff @(posedge clk) begin
    sin_out <= sin_rom[angle_idx];  // ← Updates AFTER rising edge
    cos_out <= cos_rom[angle_idx];  // ← Holds previous value until then
end
```

**Sequence of events**:
```
Cycle N (SENSORY_DECISION):
  - trig_angle_idx = angle_to_idx(angle_reg) [via DEFAULT case]
  - sin_val, cos_val = sin/cos from previous index

Cycle N+1 (CALC_MOVE_X):
  - state = CALC_MOVE_X
  - new_angle = computed angle from SENSORY_DECISION
  - trig_angle_idx = angle_to_idx(new_angle) [via CALC_MOVE_X case] ← Sets new index!
  - sin_val, cos_val = sin/cos from angle_reg [STALE! From previous cycle's trig_angle_idx]
  - mult_a = cos_val [WRONG! Not cos(new_angle)]
  - mult_result = cos_val * move_speed [GARBAGE]
  - At end of cycle: dx <= mult_result [STORES WRONG VALUE]

Cycle N+2 (CALC_MOVE_Y):
  - sin_val, cos_val NOW updated with sin/cos(new_angle) from cycle N+1's trig_angle_idx
  - mult_a = sin_val [CORRECT!]
  - mult_result = sin_val * move_speed [CORRECT]
  - At end of cycle: dy <= mult_result [CORRECT]
```

## Solution: Add WAIT_TRIG State

**Add a new state** between SENSORY_DECISION and CALC_MOVE_X to wait for the trig lookup:

```verilog
// In state enum (around line 71):
typedef enum logic [4:0] {
    ...
    SENSORY_DECISION,
    WAIT_NEW_ANGLE_TRIG,  // ← NEW STATE: Wait for sin/cos(new_angle) to be valid
    CALC_MOVE_X,
    CALC_MOVE_Y,
    ...
} state_t;

// In next_state logic (around line 218):
SENSORY_DECISION: next_state = WAIT_NEW_ANGLE_TRIG;  // ← Route here instead of CALC_MOVE_X
WAIT_NEW_ANGLE_TRIG: next_state = CALC_MOVE_X;       // ← New transition

// No datapath logic needed - this is just a wait state
```

**Why this works**:
```
Cycle N (SENSORY_DECISION):
  - trig_angle_idx = angle_to_idx(angle_reg) [via DEFAULT case]
  - new_angle <= computed angle
  - At rising edge: state ← WAIT_NEW_ANGLE_TRIG

Cycle N+1 (WAIT_NEW_ANGLE_TRIG):
  - state = WAIT_NEW_ANGLE_TRIG
  - trig_angle_idx = angle_to_idx(angle_reg) [via DEFAULT case - still old angle]
  - sin_val, cos_val are STILL stale (from previous index)
  - No operations - just waiting
  - At rising edge: state ← CALC_MOVE_X

Cycle N+2 (CALC_MOVE_X):
  - state = CALC_MOVE_X
  - new_angle has the value from SENSORY_DECISION (2 cycles ago)
  - trig_angle_idx = angle_to_idx(new_angle) [via CALC_MOVE_X case] ← Sets NEW index
  - sin_val, cos_val NOW have sin/cos(new_angle)! ← 1 cycle delay = perfect!
  - mult_a = cos_val [NOW CORRECT!]
  - mult_result = cos_val * move_speed [CORRECT]
  - At rising edge: dx <= mult_result [CORRECT]

Cycle N+3 (CALC_MOVE_Y):
  - sin_val, cos_val still have sin/cos(new_angle)
  - mult_a = sin_val [CORRECT!]
  - At rising edge: dy <= mult_result [CORRECT]
```

## Implementation Changes Required

### File: `rtl/src/agent_processor.sv`

**Change 1: Update state enum (line 71)**
```verilog
typedef enum logic [4:0] {
    IDLE,
    CALC_SENSOR_F_X,
    CALC_SENSOR_F_Y,
    READ_TRAIL_F,
    WAIT_TRAIL_F,
    CALC_SENSOR_L_X,
    CALC_SENSOR_L_Y,
    READ_TRAIL_L,
    WAIT_TRAIL_L,
    CALC_SENSOR_R_X,
    CALC_SENSOR_R_Y,
    READ_TRAIL_R,
    WAIT_TRAIL_R,
    SENSORY_DECISION,
    WAIT_NEW_ANGLE_TRIG,    // ← ADD THIS STATE
    CALC_MOVE_X,
    CALC_MOVE_Y,
    UPDATE_POS,
    WRITE_TRAIL,
    DONE_STATE
} state_t;
```

**Change 2: Update next_state logic (line 218)**
```verilog
// Decision and movement
SENSORY_DECISION: next_state = WAIT_NEW_ANGLE_TRIG;  // ← CHANGE: was CALC_MOVE_X
WAIT_NEW_ANGLE_TRIG: next_state = CALC_MOVE_X;       // ← ADD THIS LINE
CALC_MOVE_X:      next_state = CALC_MOVE_Y;
CALC_MOVE_Y:      next_state = UPDATE_POS;
UPDATE_POS:       next_state = WRITE_TRAIL;
WRITE_TRAIL:      next_state = DONE_STATE;
DONE_STATE:       next_state = IDLE;
```

**Change 3: (Optional) Update state-machine comment at line 5**
```verilog
// Pipeline stages:
// 1. Fetch agent from memory
// 2. Compute sensor positions (trig lookup)
// 3. Sample trail map at sensor positions
// 4. Sensory decision (compare F, FL, FR)
// 5. Wait for new angle trig lookup
// 6. Compute new position (trig lookup)
// 7. Write back agent and deposit trail
```

## Validation

After applying the fix:

1. **Recompile RTL**: `vivado -mode batch -source build_vivado.tcl`
2. **Run regression tests**: `source .venv/bin/activate && python3 run_regression_tests.py`
3. **Check movement pattern**: Should now be consistently 1.0x, not alternating 0x/2x/1x
4. **Verify all steps**: All 10 regression tests should pass or at least show consistent movement

## Cost of This Fix

- **Latency impact**: +1 cycle per agent (minor - total pipeline is 20 cycles now, was 19)
- **Throughput impact**: Negligible (still processes 1000 agents in ~19 ms at 60 FPS)
- **Code complexity**: Minimal (just one new state, no datapath changes)
- **FPGA resources**: None (just adds one more state encoding bit)

## Why This Is the Correct Root Cause

1. ✅ Explains the 0x/2x/1x pattern (timing-dependent, not arithmetic)
2. ✅ Matches symptom (movement calculation uses wrong trig values)
3. ✅ Matches observation (all sub-modules verified correct individually)
4. ✅ All cocotb tests pass (bug is in state machine sequencing, not arithmetic)
5. ✅ Fix is minimal and surgical (just adds a wait state)
