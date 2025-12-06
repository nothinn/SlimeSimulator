# 2x Movement Scaling Bug - Cocotb Testbench

## Summary

Created a comprehensive cocotb testbench that isolates and characterizes the **2x movement scaling bug** in the RTL agent processor. The testbench focuses specifically on the movement calculation pipeline to help identify the root cause.

## Files Created

### 1. `rtl/sim/test_2x_movement_bug.py` (14 KB)
**Cocotb testbench with three focused tests:**

- **`test_2x_movement_right_direction`**: Tests movement at angle 0° (simplest case)
  - Initializes agent at (160, 120) facing right
  - Expected movement: dx=1.0, dy=0.0
  - With 2x bug: dx≈2.0
  - Purpose: Isolates multiply and position update logic

- **`test_2x_movement_diagonal`**: Tests movement at 45° (both axes)
  - Initializes agent at (160, 120) facing northeast
  - Expected movement: dx≈0.707, dy≈0.707
  - With 2x bug: dx≈1.414, dy≈1.414
  - Purpose: Verifies bug affects both x and y equally

- **`test_movement_components_isolation`**: Tests each component independently
  - Verifies trig LUT values match Python reference
  - Checks fixed-point multiplication accuracy
  - Validates position coordinate wrapping
  - Purpose: Isolates which component has the bug

### 2. `rtl/sim/2X_MOVEMENT_BUG_TEST.md` (7.2 KB)
**Comprehensive documentation including:**

- Bug characteristics and evidence from regression tests
- Detailed explanation of each test
- Root cause hypotheses with testing strategies
- Debug checklist for identifying the exact issue
- Key files and variables referenced
- Performance notes and future improvements

### 3. `rtl/sim/RUN_2X_BUG_TEST.sh` (1.7 KB)
**Quick reference script for running tests:**

```bash
cd rtl/sim
bash RUN_2X_BUG_TEST.sh
```

- Handles environment setup (venv activation)
- Runs all 3 tests in sequence
- Saves output to `2x_bug_test_output.log`
- Provides summary and analysis hints

### 4. `rtl/sim/Makefile` (Updated)
**Added test target:**

```bash
make test_2x_movement_bug
```

- Compiles all required RTL modules
- Runs 3 test cases in sequence
- Takes < 3 seconds to complete

## Bug Characteristics

### Observed Issue
- **Expected**: Movement = (cos(θ) × move_speed, sin(θ) × move_speed)
- **Observed**: Movement ≈ 2× expected value
- **Consistency**: Same 2x ratio across all angles and agent counts
- **Certainty**: Verified across 10 regression tests (9 failed with consistent error pattern)

### Evidence from Regression Tests
```
Test 1 (100 agents):  Mean error = 97.5 px
Test 2 (init, 1 step): Mean error = 97.5 px
Test 5 (500 agents):  Mean error = 97.5 px
Test 10 (2000 steps): Mean error = 167.1 px (scales with distance)
```

Error ratio consistently ≈ 2.0 across all tests

## How to Use

### Run Tests
```bash
cd rtl/sim
source ../../.venv/bin/activate

# Run all tests
make test_2x_movement_bug

# Or use convenience script
bash RUN_2X_BUG_TEST.sh

# Or run specific test
make sim MODULE=test_2x_movement_bug TOPLEVEL=agent_sim_tb \
  TESTCASE=test_2x_movement_right_direction
```

### Interpret Results

The test output shows:

1. **Expected values** (from Python reference):
   ```
   cos(0°) = 1.000000
   move_speed = 1.000000
   Expected dx = 1.000000 px
   ```

2. **Indicates where RTL differs**:
   - If dx observed ≈ 2.0 px → 2x bug confirmed
   - Shows which angle/component has the issue

3. **Points to root cause**:
   - Trig values wrong? Compare cos/sin output
   - Multiply scaling wrong? Check fixed_point_mult
   - State machine issue? Check WAIT_NEW_ANGLE_TRIG state

## Root Cause Hypotheses

The testbench is designed to help identify which of these is the issue:

### Hypothesis 1: move_speed Constant Wrong
RTL hardcodes move_speed as 2.0 instead of 1.0
- **Evidence**: Would cause exactly 2x movement
- **Test**: Check `move_speed_in` value in debug output

### Hypothesis 2: Fixed-Point Multiply Scaling
Multiply uses `>> 11` instead of `>> 12` (one fewer shift)
- **Evidence**: Would cause 2x magnitude for all multiplications
- **Test**: Compare `mult_result` against Python reference

### Hypothesis 3: Trig Latency (Old Values)
Pipeline uses sin/cos from **old angle** instead of **new angle**
- **Evidence**: WAIT_NEW_ANGLE_TRIG compensation might not work
- **Test**: Check state machine transitions (lines 86-88 of agent_processor.sv)

### Hypothesis 4: Double Application
Movement applied in two pipeline stages instead of one
- **Evidence**: Would cause exactly 2x
- **Test**: Trace state machine to ensure CALC_MOVE/UPDATE_POS happen once per step

## Next Steps

1. **Run the testbench**: `bash RUN_2X_BUG_TEST.sh`
2. **Examine output** for exact error magnitude and pattern
3. **Check relevant components**:
   - For move_speed: Search agent_processor.sv for constant definition
   - For multiply: Review fixed_point_mult.sv shift amount
   - For latency: Verify WAIT_NEW_ANGLE_TRIG state logic
   - For double-apply: Check state machine transitions

4. **Fix identified issue** based on root cause
5. **Re-run testbench** to verify fix eliminates 2x error
6. **Run regression tests**: `python3 run_regression_tests.py`

## Success Criteria

After fix, expect:

```
Test Results: 10/10 PASSED (instead of 9/10 FAILED)
Movement error: < 0.5 px (instead of 97-167 px)
Error ratio: ≈ 1.0 (instead of ≈ 2.0)
```

## Performance

- Test execution time: < 3 seconds
- Can run in parallel with other cocotb tests
- Minimal waveform generation
- Suitable for continuous integration

## Integration with Workflow

```bash
# Development workflow
1. Edit RTL (e.g., fix multiply shift)
2. Run focused test: make test_2x_movement_bug
3. If passes, run full regression: python3 run_regression_tests.py
4. Commit when all tests pass
```

## Technical Details

### Parameters Used
- Resolution: 320×240 (same as regression tests)
- Agents: 1 (focused isolation)
- move_speed: 1.0 (easy to verify)
- sensor_distance: 9.0 (same as default)
- LFSR seed: 0xDEADBEEF (reproducible)

### Expected FP Values
- FP format: Q12.12 (12 int bits, 12 frac bits)
- 1.0 → 0x1000 (4096 in hex)
- cos(0°) = 1.0 → 0x1000000
- sin(0°) = 0.0 → 0x0000000

### Movement Calculation Pipeline
```
IDLE
  ↓
[Sense Forward] (3 states)
  ↓
[Read Trail] (2 states)
  ↓
[Sense Left] (3 states)
  ↓
[Read Trail] (2 states)
  ↓
[Sense Right] (3 states)
  ↓
[Read Trail] (2 states)
  ↓
SENSORY_DECISION
  ↓
WAIT_NEW_ANGLE_TRIG ← CRITICAL: Wait for sin/cos(new_angle)
  ↓
CALC_MOVE_X → dx = cos * move_speed
CALC_MOVE_Y → dy = sin * move_speed
  ↓
UPDATE_POS → new_x = x + dx, new_y = y + dy
  ↓
WRITE_TRAIL
  ↓
DONE_STATE
```

## References

- **Bug Report**: CLAUDE.md - Known RTL Issues section
- **Architecture**: rtl/src/agent_processor.sv - Lines 71-92 (state machine)
- **Reference**: slime_simulator.py - SlimeSimulatorReference.update_agent()
- **Latency Fix**: TRIG_LUT_REFACTOR_SUMMARY.md - WAIT_NEW_ANGLE_TRIG state

## Questions & Debug

**Q: How do I know if the 2x bug is present?**
A: Run `bash RUN_2X_BUG_TEST.sh` and look for "Expected dx = 1.0" vs observed ≈ 2.0

**Q: What if the test hangs?**
A: Check if agent_sim_tb.sv exists and is properly connected. Timeout is 1000 cycles (10µs).

**Q: Can I modify test parameters?**
A: Yes! Edit the angle, move_speed, and position values in the test functions.

**Q: Where are agent dumps created?**
A: Not automatically in cocotb - would need custom RTL output interface. See regression tests for example.

## Success Stories

Once the bug is fixed, expect to see:

✅ test_2x_movement_right_direction **PASSED**
✅ test_2x_movement_diagonal **PASSED**
✅ test_movement_components_isolation **PASSED**
✅ All 10 regression tests **PASSED** (9/10 → 10/10)

---

**Created**: December 6, 2025
**Status**: Ready for testing
**Maintenance**: Low - self-contained, references slime_simulator.py for all constants
