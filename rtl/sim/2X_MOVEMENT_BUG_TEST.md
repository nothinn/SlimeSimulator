# 2x Movement Scaling Bug - Cocotb Testbench

## Overview

This testbench (`test_2x_movement_bug.py`) is designed to isolate and characterize the 2x movement scaling bug observed in RTL simulations. The bug causes agents to move approximately **2x the expected distance** in each step.

## Bug Characteristics

### Observed Behavior
- **Expected movement**: agent moves by (cos(θ) × move_speed, sin(θ) × move_speed) pixels
- **Observed movement**: agent moves by approximately **2×** the expected distance
- **Consistency**: Bug appears for all angles and agent counts
- **Scale**: Error ratio is consistently ≈ 2.0 across all tests

### Evidence
Regression tests show:
- Test 1 (100 agents, 10 steps): Mean error ≈ 97.5 px
- Test 2 (init validation, 1 step): Mean error ≈ 97.5 px (consistent)
- Test 5 (500 agents, 50 steps): Mean error ≈ 97.5 px (independent of count)

The consistent error magnitude despite different step counts suggests a per-step scaling issue.

## Test Structure

### Three Main Tests

#### 1. `test_2x_movement_right_direction`
**Purpose**: Test movement in the simplest case (0 degrees, cos=1.0, sin=0)

**Setup**:
- Initialize single agent at (160, 120)
- Set angle to 0 (facing right)
- move_speed = 1.0

**Expected Result**:
- dx = 1.0 px (cos(0°) × 1.0)
- dy = 0.0 px (sin(0°) × 1.0)
- New position: (161, 120)

**With 2x Bug**:
- Observed dx ≈ 2.0 px
- New position ≈ (162, 120)

**Why This Test**:
- Simplest case to debug (only one non-zero component)
- Isolates the multiply and position update logic
- Easy to verify with manual inspection

#### 2. `test_2x_movement_diagonal`
**Purpose**: Test movement at 45 degrees (both dx and dy non-zero)

**Setup**:
- Initialize single agent at (160, 120)
- Set angle to 256 (45 degrees)
- move_speed = 1.0

**Expected Result**:
- dx ≈ 0.707 px (cos(45°) × 1.0)
- dy ≈ 0.707 px (sin(45°) × 1.0)
- Movement magnitude ≈ 1.0 px
- New position ≈ (160.707, 120.707)

**With 2x Bug**:
- dx ≈ 1.414 px (2× expected)
- dy ≈ 1.414 px (2× expected)
- Movement magnitude ≈ 2.0 px

**Why This Test**:
- Verifies bug affects both x and y equally
- Confirms it's not axis-specific
- Validates rotation behavior

#### 3. `test_movement_components_isolation`
**Purpose**: Test each movement component independently

**Tests**:
1. TrigLUT values (sin/cos) for reference angles
2. Fixed-point multiplication accuracy
3. Position addition logic

**Verification**:
- Compares RTL trig values against Python reference
- Checks multiply operation for scaling errors
- Validates coordinate wrapping

## How to Run Tests

```bash
cd rtl/sim
source ../../.venv/bin/activate

# Run all 2x movement bug tests
make test_2x_movement_bug

# Or run individual tests
make sim VERILOG_SOURCES="$(SRC_DIR)/agent_sim_tb.sv $(SRC_DIR)/agent_processor.sv $(SRC_DIR)/lfsr.sv $(SRC_DIR)/trig_lut.sv $(SRC_DIR)/fixed_point_mult.sv" \
  MODULE=test_2x_movement_bug TOPLEVEL=agent_sim_tb \
  TESTCASE=test_2x_movement_right_direction
```

## Expected Output

### Successful Test (No Bug)
```
TEST: 2x Movement Bug - Right Direction (angle=0)
================================================================================
Initialized agent at (160.0, 120.0), angle=0 (facing right)

PYTHON REFERENCE CALCULATION
================================================================================
Angle index: 0 (facing right, 0°)
cos(0°) = 1.000000 (FP: 0x1000000)
sin(0°) = 0.000000 (FP: 0x0000000)
move_speed = 1.000000 (FP: 0x0001000)

Expected movement:
  dx = cos * speed = 1.000000 * 1.000000 = 1.000000 px
  dy = sin * speed = 0.000000 * 1.000000 = 0.000000 px

Expected new position after step:
  x = 160.0 + 1.000000 = 161.000000
  y = 120.0 + 0.000000 = 120.000000
```

### With 2x Bug
The test output shows the expected values but notes that RTL produces 2× the movement.

## Root Cause Analysis

### Hypothesis 1: move_speed Constant is Wrong
If `move_speed` is stored as 2.0 instead of 1.0 in RTL, this would exactly explain the 2x bug.

**Test**: Verify move_speed value in RTL simulation
```
Check: dut.move_speed_in.value should be 0x0001000 (1.0 in Q12.12)
```

### Hypothesis 2: Fixed-Point Multiplication Scaling
The multiply operation might be incorrectly scaling the result.

**Normal**: `result = (a × b) >> 12`
**Buggy**: `result = (a × b) >> 11` (one fewer shift)

**Test**: Compare RTL multiply output against Python reference
```python
expected = fp.multiply(cos_val, move_speed)
observed = dut.mult_result.value
```

### Hypothesis 3: Trig Latency Using Stale Values
The trig_lut has registered outputs (1-cycle latency). If the pipeline uses sin/cos from the **old angle** instead of **new angle**, it would apply old movement twice.

**Test**: Verify `WAIT_NEW_ANGLE_TRIG` state is being entered correctly
```
Check: State machine should pause at WAIT_NEW_ANGLE_TRIG for 1 cycle after SENSORY_DECISION
```

### Hypothesis 4: Movement Applied Twice
Pipeline might be applying movement in two different places (during sensing and during position update).

**Test**: Trace pipeline state progression
```
Monitor: CALC_MOVE_X → CALC_MOVE_Y → UPDATE_POS should happen once per step
```

## Test Variables

The `MovementBugTracer` class computes expected values:

```python
tracer = MovementBugTracer(fp)
expected = tracer.compute_expected_movement(
    x=center_x,
    y=center_y,
    angle_idx=0,
    move_speed=fp.to_fixed(1.0)
)

# Expected contains:
# - cos_val, sin_val (from trig LUT)
# - dx, dy (movement deltas)
# - new_x, new_y (updated position)
# - All in both fixed-point and float for readability
```

## Integration with Full Simulation

This isolated test can be combined with regression tests:

```bash
# After fixing: run full regression
python3 run_regression_tests.py

# Verify fix eliminates the 2x error
# Expected: Tests move from "FAILED" to "PASSED" with <0.5px error
```

## Key Files Referenced

- **RTL**: `rtl/src/agent_processor.sv` - State machine and movement logic
- **RTL**: `rtl/src/fixed_point_mult.sv` - Multiplication module
- **RTL**: `rtl/src/trig_lut.sv` - Sine/cosine lookup
- **Python**: `slime_simulator.py` - Reference implementation
- **Test**: `test_2x_movement_bug.py` - This testbench

## Debug Checklist

When the test reveals the exact bug:

- [ ] Check move_speed constant in agent_processor.sv (should be 0x1000)
- [ ] Verify fixed_point_mult output scaling (should be >> 12)
- [ ] Confirm WAIT_NEW_ANGLE_TRIG state exists (line 86 in agent_processor.sv)
- [ ] Check state machine transitions in detailed trace
- [ ] Verify trig values match Python reference
- [ ] Confirm no double-application of movement logic

## Performance Notes

- Single test: < 1 second
- All 3 tests: < 3 seconds
- Can run in parallel with other cocotb tests

## Future Improvements

1. **Direct position readback**: Add RTL interface to directly read agent x, y values
2. **Waveform capture**: Generate VCD dump for waveform analysis
3. **Breakpoint support**: Pause simulation at specific states for inspection
4. **Parametric variants**: Test with different move_speed values (0.5, 2.0, etc.)

## See Also

- `CLAUDE.md` - Project architecture and known issues
- `TRIG_LUT_REFACTOR_SUMMARY.md` - Trig LUT latency fix details
- `regression_tests.csv` - Full regression test configuration
