# 2x Movement Bug Investigation Summary

## Executive Summary

The RTL simulator exhibits a 2x movement bug that manifests as **alternating movement scale factors**:
- Some steps: RTL agents move 0x (no movement)
- Other steps: RTL agents move 2x (double movement)
- Some steps: RTL agents move 1x (correct)

**Pattern**: `0x, 2x, 1x, 2x, 1x, 2x, ...` starting from step 0→1

## Sub-Module Verification Results

All individual sub-modules verified against Python reference using cocotb tests:

### ✅ LFSR (32-bit Maximal-Length)
- **Status**: PASS (14 tests, 1000 cycles tested)
- **Test**: `test_rtl_vs_python.test_lfsr_sequence_extended`
- **Result**: Sequence matches Python exactly for 1000 steps
- **Conclusion**: LFSR implementation is bit-exact correct

### ✅ Fixed-Point Multiplication (Q12.12)
- **Status**: PASS (14 tests covering all ranges)
- **Test**: `test_rtl_vs_python.test_fixed_point_multiply_comprehensive`
- **Test Cases**:
  - Basic multiplication (1×1, 2×2, 0.5×0.5, etc.)
  - Zero cases (0×1, 1×0, 0×0)
  - Negative numbers (-1×1, 1×-1, -1×-1)
  - Fractional values (0.25×0.25, 3.14159×2)
  - Trigonometric values (cos/sin × speed)
  - Edge cases (large, small, mixed)
- **Result**: Max error = 0 LSB
- **Conclusion**: Fixed-point multiply is bit-exact correct

### ✅ Trigonometric LUT (Sin/Cos Lookup)
- **Status**: PASS (1024 table entries verified)
- **Test**: `test_rtl_vs_python.test_trig_lut_full_table`
- **Coverage**: All 1024 table entries (0° to ~360°)
- **Result**: sin errors=0, cos errors=0
- **Conclusion**: Trig LUT values match Python exactly

## 2x Bug Root Cause Analysis

Since all sub-modules pass individual verification, **the bug is NOT in**:
- ❌ LFSR random number generation
- ❌ Fixed-point arithmetic (multiply operation)
- ❌ Trig lookup tables

**The bug IS in**:
- 🔍 `agent_processor.sv` - pipeline stage timing or state machine
- 🔍 `agent_coordinator.sv` - agent processing sequencing or result write-back
- 🔍 Inter-module communication or data flow synchronization

## Observed Behavior

### CSV Analysis (from regression_results/3_movement_10steps/trajectory_comparison.csv)

**Step-by-step movement for Agent 0:**
```
Step 0→1: Python ΔX=1.0, RTL ΔX=2.0 (2.00x)
Step 1→2: Python ΔX=1.0, RTL ΔX=0.0 (0.00x)
Step 2→3: Python ΔX=1.0, RTL ΔX=1.0 (1.00x)
Step 3→4: Python ΔX=1.0, RTL ΔX=2.0 (2.00x)
Step 4→5: Python ΔX=1.0, RTL ΔX=1.0 (1.00x)
Step 5→6: Python ΔX=1.0, RTL ΔX=2.0 (2.00x)
...pattern repeats...
```

### Pattern Characteristics

1. **Deterministic**: Same pattern repeats every test run
2. **Alternating**: 2x, 0x alternation interspersed with 1x correct values
3. **Per-step**: Affects all agents the same way in a given step
4. **Persistent**: Continues across 100+ steps in regression tests

## Hypotheses (Ranked by Likelihood)

### Hypothesis 1: Pipeline Register Capture Timing (HIGH)
The movement calculation (CALC_MOVE_X, CALC_MOVE_Y) may be capturing:
- `dx` and `dy` from the WRONG multiply result
- Or using SIN/COS from the wrong trig lookup cycle
- Or applying multiply twice/skip once due to state machine issue

**Why this fits**:
- Alternating pattern suggests registers being updated on wrong cycle
- 2x could be from "double capture" (dx used twice)
- 0x could be from "skip" (dx not updated)

### Hypothesis 2: Agent Write-Back Timing (HIGH)
`agent_coordinator.sv` may be:
- Writing back results from wrong pipeline stage
- Writing results from previous agent into current agent
- Having off-by-one error in result handshake

**Why this fits**:
- Would cause systematic movement errors
- Could alternate if write-back happens at wrong phase

### Hypothesis 3: Trig Lookup Latency Mismatch (MEDIUM)
The trig_lut output is registered (1-cycle latency), but:
- Movement calculation may not account for this properly
- Index may be set one cycle too early/late
- New_angle prediction may be incorrect

**Why this fits**:
- Would cause wrong sin/cos values to be used
- 2x pattern could result from using old+new values

### Hypothesis 4: Multiplier Pipelining (MEDIUM)
If there's any pipelining in the multiply:
- Results captured from wrong pipeline stage
- Or intermediate partial products being used

**Why this fits**:
- Would cause selective value corruption
- But `test_fixed_point_multiply_comprehensive` should catch this

## Recommended Investigation Steps

1. **Add Detailed Waveform Tracing**
   - Log `trig_angle_idx` at each state
   - Monitor `sin_val`, `cos_val` outputs from trig_lut
   - Track `mult_result` at CALC_MOVE_X and CALC_MOVE_Y
   - Log `dx`, `dy` register updates
   - Monitor state machine state changes

2. **Create Minimal Reproduction**
   - Simulate single agent for 5 steps in cocotb
   - Verify movement at each step
   - Identify which state produces wrong result

3. **Verify Trig Lookup Timing**
   - Add test forcing specific angle_idx values
   - Verify sin/cos appear correct cycles later
   - Check if trig lookup is being used correctly in movement

4. **Trace Agent Coordinator**
   - Verify processor outputs are read at right time
   - Verify write-back only happens once per agent
   - Check state machine transitions

## Test Files Created

New comprehensive testbenches for reference:
- `/rtl/sim/test_fixed_point_comprehensive.py` - Exhaustive fixed-point tests
- `/rtl/sim/test_movement_calculation.py` - Movement calculation verification

## Next Steps

1. Run detailed waveform-based debugging on agent_processor
2. Create minimal 1-agent cocotb test to isolate issue
3. Review agent_coordinator write-back logic
4. Check trig_lut integration in movement calculation pipeline
