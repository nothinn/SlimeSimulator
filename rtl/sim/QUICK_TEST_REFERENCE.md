# Quick Test Reference

## Running the New Comprehensive Tests

### One-Line Quick Test
```bash
cd rtl/sim && source ../../.venv/bin/activate && make test_modules_comprehensive
```

### Full Test Suite (including legacy tests)
```bash
cd rtl/sim && source ../../.venv/bin/activate && make test_comparison
```

## Individual Module Tests

### Test Trig LUT (1024 sin/cos entries, latency behavior)
```bash
make test_trig_lut_vs_python
```
- Verifies all 1024 sine values match Python
- Verifies all 1024 cosine values match Python
- Confirms 1-cycle registered output latency

### Test Fixed-Point Multiplier (25 test cases)
```bash
make test_fixed_point_mult_vs_python
```
- Basic arithmetic (1.0*1.0, 2.0*2.0, etc.)
- Signed operations (-1.0*1.0, -1.0*-1.0)
- Fractions (0.125*8.0 = 1.0)
- Trig values (sin/cos products)
- Movement calculation (cos*1.0, sin*1.0 for 9 angles)

### Test Agent Processor (reset, initialization, latency compensation)
```bash
make test_agent_processor_vs_python
```
- Reset/initialization behavior
- Verifies WAIT_NEW_ANGLE_TRIG state exists (latency fix)

## Expected Output

All tests should show:
```
** TESTS=2 PASS=2 FAIL=0 **
```

For the comprehensive suite:
```
** TESTS=6 PASS=6 FAIL=0 **
```

## Test Summary

| Module | Test Cases | Status | Command |
|--------|-----------|--------|---------|
| trig_lut | 2 | ✅ PASS | `make test_trig_lut_vs_python` |
| fixed_point_mult | 2 | ✅ PASS | `make test_fixed_point_mult_vs_python` |
| agent_processor | 2 | ✅ PASS | `make test_agent_processor_vs_python` |
| **Total** | **6** | **✅ PASS** | `make test_modules_comprehensive` |

## Files

- **Test Code:** `rtl/sim/test_modules_vs_python.py` (540+ lines)
- **Documentation:** `rtl/sim/TEST_MODULES_VS_PYTHON.md` (detailed guide)
- **Build Config:** `rtl/sim/Makefile` (updated with new targets)
- **Reference:** `rtl/sim/python_reference.py` (Python implementations)

## What These Tests Verify

### Trig LUT
- ✅ All 1024 sine entries bit-exact correct
- ✅ All 1024 cosine entries bit-exact correct
- ✅ 1-cycle registered output latency behavior (critical for 2x bug fix)

### Fixed-Point Multiplier
- ✅ 25 comprehensive test cases
- ✅ Movement magnitude calculation correct (dx = cos*1.0, dy = sin*1.0)
- ✅ Q12.12 arithmetic matches Python exactly

### Agent Processor
- ✅ Reset and initialization working correctly
- ✅ WAIT_NEW_ANGLE_TRIG state present (2x movement bug fix)
- ✅ 20-stage pipeline properly compiled

## Integration with Existing Tests

These tests are separate from the regression test suite:

```
Regression Tests (run_regression_tests.py):
  - Uses Verilator (full RTL simulation, 100k agents)
  - End-to-end testing
  - Python vs RTL comparison with trail maps

Cocotb Unit Tests (test_modules_comprehensive):
  - Uses Icarus Verilog (individual modules)
  - Unit-level testing
  - Bit-exact verification against Python reference
```

Both are complementary and should both pass.

## Troubleshooting

### Tests fail with "module not found" error
- Clean the build directory: `make clean`
- Then run test again

### Icarus warnings about "constant selects"
- These are informational warnings only
- Tests still run correctly
- Not a test failure

### Need to recompile after RTL changes
- Makefile automatically rebuilds
- Run `make clean` first if problems occur

## Next Steps

1. **Commit the changes:**
   ```bash
   git add rtl/sim/test_modules_vs_python.py
   git add rtl/sim/TEST_MODULES_VS_PYTHON.md
   git add rtl/sim/Makefile
   git commit -m "Add comprehensive cocotb testbenches for RTL modules"
   ```

2. **Add to CI/CD pipeline:**
   ```bash
   # Before running regression tests
   make test_modules_comprehensive
   ```

3. **Document in project README:**
   - Add reference to these tests
   - Link to TEST_MODULES_VS_PYTHON.md

## Questions?

Refer to full documentation: `rtl/sim/TEST_MODULES_VS_PYTHON.md`
