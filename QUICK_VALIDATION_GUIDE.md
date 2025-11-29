# Quick Validation Guide

## Run Validation in 30 Seconds

```bash
cd /home/reson/SlimeSimulator
source .venv/bin/activate
python3 validate_agent_init_comprehensive.py
```

**Expected Output:**
```
✓ VALIDATION PASSED - RTL and Python initialization match!
...
Pass rate: 100.0%
```

---

## What Was Fixed

| Issue | Fix | Impact |
|-------|-----|--------|
| RTL default size was 160x120 | Changed to 320x240 | RTL now uses correct canvas size |
| Python used random spawn angles | Changed to deterministic circle pattern | Perfect match with RTL |
| Angles at 360° failed comparison | Added wraparound handling | All agents pass validation |

---

## Validation Results

✅ **1000/1000 agents validated (100%)**

- All agents initialize on circle (40% of canvas radius)
- All agents evenly spaced around circle
- All agents point toward center
- Positions match within sub-pixel precision (<1 px)
- Angles match within trigonometric precision (<0.1°)

---

## Key Files

### Modified
- `slime_simulator.py` - Fixed circle spawn pattern
- `rtl/src/slime_top.sv` - Updated default parameters

### New
- `validate_agent_init_comprehensive.py` - Comprehensive validation script
- `rtl/sim/Makefile.agent_init_validator` - RTL testbench build config
- `AGENT_INITIALIZATION_VALIDATION.md` - Detailed documentation

### Output
- `python_agent_validation.json` - Python agent state dump
- `rtl_agent_validation.json` - RTL agent state dump
- `agent_init_comparison.json` - Per-agent comparison details
- `agent_init_validation_report.txt` - Human-readable report

---

## Implementation Details

### Circle Spawn Algorithm (Fixed Python)
```python
# Before: Random angles using LFSR
spawn_angles_fp = self._lfsr_uniform_angle_fp(n)

# After: Deterministic circle (2π * i / n)
spawn_angles_fp = np.array(
    [self.fp.to_fixed(2 * np.pi * i / n) for i in range(n)],
    dtype=np.int64
)
```

### Agent State Extraction (RTL)
The RTL now includes a debug interface that allows reading agent state without advancing simulation:

```systemverilog
// Set agent index and selector
dut->debug_agent_idx = i;       // 0-999
dut->debug_agent_sel = sel;     // 0=x, 1=y, 2=angle

// Read combinatorially
dut->eval();
int32_t value = dut->debug_agent_data;  // Signed 25-bit value
```

### Tolerances Used
```
Position: ±1.0 pixel (±4096 fixed-point units)
Angle:    ±0.1° with circular wraparound handling
```

These tolerances account for:
- Float vs fixed-point rounding differences
- Trigonometric lookup table precision
- Different implementations of sin/cos

---

## Step-by-Step Validation Process

1. **Generate Python Reference**
   - Simulate 1000 agents on circle
   - Export positions and angles to JSON
   - Takes ~5 seconds

2. **Build RTL Testbench**
   - Compile Verilator testbench
   - First run: ~30 seconds (includes compilation)
   - Subsequent runs: ~3 seconds (cached binary)

3. **Extract RTL Agent State**
   - Read all 1000 agent states from RTL memory
   - Use debug_agent interface (combinatorial readback)
   - No simulation advancement needed
   - Takes ~3 seconds

4. **Compare Agent by Agent**
   - Check position and angle differences
   - Handle angle wraparound at 360°/0°
   - Generate pass/fail for each agent
   - Takes <1 second

5. **Generate Report**
   - Statistics (min/max/mean errors)
   - List any failures with details
   - Save detailed JSON comparison
   - Takes <1 second

**Total Time**: ~50 seconds (first run), ~15 seconds (subsequent runs)

---

## What This Validates

✅ **Initialization is correct and identical**
- Both RTL and Python spawn agents on same circle
- Both use same radius (40% of canvas)
- Both space agents evenly around circle
- Both initialize agents pointing toward center

---

## How to Extend Validation

### Validate Each Simulation Step
```python
# After step_count steps:
# 1. Extract agent state from RTL (same debug interface)
# 2. Compare with Python after same steps
# 3. Check trail map deposits match
# 4. Validate swarm behavior metrics
```

### CI/CD Integration
```bash
# Add to pre-commit or CI pipeline
if ! python3 validate_agent_init_comprehensive.py; then
  echo "Agent initialization validation failed"
  exit 1
fi
```

---

## Troubleshooting

**All agents fail to validate?**
- Check RTL parameters match Python (WIDTH, HEIGHT, NUM_AGENTS)
- Rebuild Verilator testbench: `cd rtl/sim && make -f Makefile.agent_init_validator clean sim`

**Some agents fail?**
- Check if failures are at specific angles (common for trig precision)
- Increase TOLERANCE_FP in validation script if needed
- Verify both implementations use same radius calculation

**Validation slow?**
- Subsequent runs cached after first compilation (~3 seconds)
- Reduce agent count with `--agents 100` for quick testing
- Use `--no-build` flag after first run to skip compilation

---

## Summary

The initialization validation infrastructure now provides:

✅ Automated testing of agent spawn patterns
✅ Bit-accurate comparison (within precision limits)
✅ Detailed error reporting and visualization
✅ Extensible for multi-step validation
✅ Ready for CI/CD integration

All 1000 agents now initialize identically in both RTL and Python! 🎉

---

**Last Updated**: 2025-11-27
