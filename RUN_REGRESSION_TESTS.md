# Running Regression Tests

## Prerequisites

You need the Python simulator and Verilator toolchain available.

### 1. Verify Python Simulator

```bash
python slime_simulator.py --agents 10 --steps 5
```

Should complete without errors.

### 2. Verify Verilator is Installed

The regression tests will **automatically compile the RTL binary for each test** with the appropriate parameters (resolution, agents, steps). You just need Verilator installed:

```bash
verilator --version
```

If not installed:
```bash
# Ubuntu/Debian
sudo apt-get install verilator

# macOS
brew install verilator
```

### 3. Optional: Verify run_extended_comparison.sh

Check if the comparison script exists (preferred, faster):

```bash
ls run_extended_comparison.sh
```

If it doesn't exist, the test runner will use manual Verilator compilation.

### Important: RTL Recompilation

Each test case is compiled with its specific parameters:
- **Resolution** - Different canvas sizes (320x240, 640x480, etc.)
- **Agent Count** - Number of agents (100, 500, 1000, etc.)
- **Step Count** - Simulation duration (5, 10, 50, 100, etc.)

This means the first run will take longer due to compilation. Subsequent tests with the same parameters will reuse the compiled binary if available.

## Running Tests

### Run a Single Smoke Test

Quick test to verify everything works:

```bash
python run_regression_tests.py --test-id 1
```

Expected output (first run includes compilation):
```
================================================================================
Test 1: smoke_test_100
Type: smoke | Agents: 100 | Resolution: 320x240 | Steps: 10
================================================================================

[1/3] Running Python simulation...
  Command: python slime_simulator.py --agents 100 ...
  ✓ Python simulation completed

[2/3] Running RTL simulation...
  Compiling RTL for: 320x240, 100 agents, 10 steps
  Using run_extended_comparison.sh (rebuilds RTL with parameters)
  ✓ RTL simulation completed

[3/3] Comparing Python vs RTL...
  Max error: X.XXX px
  Mean error: X.XXX px
  Agents matching: 100/100
  Status: ✓ PASSED
```

**Note**: First run will take ~3-5 minutes due to Verilator compilation. Subsequent tests may be faster if parameters are reused.

### Run All Smoke Tests (Fast)

```bash
python run_regression_tests.py --test-type smoke
```

Takes ~3-5 minutes per test (includes Verilator compilation).

### Run Integration Tests (Full Comparison)

```bash
python run_regression_tests.py --test-type integration
```

Takes ~5-15 minutes per test (includes compilation, depends on agents/steps).

### Run All Tests

```bash
python run_regression_tests.py
```

Runs all 10 tests. Total time: ~2-4 hours depending on hardware and compilation cache.
- First test: 3-5 min (fresh compilation)
- Subsequent tests with same params: 1-3 min (reuse binary)
- Different params: 3-5 min (recompile)

### Run Without RTL (Python Only)

If RTL binary isn't available yet:

```bash
python run_regression_tests.py --no-rtl
```

### Run with Verbose Logging

For detailed debugging:

```bash
python run_regression_tests.py --test-id 1 --verbose
```

## Output

After each test, check the results:

```bash
# View summary
cat regression_results/REPORT.md

# View detailed log
tail -100 regression_results/regression_tests.log

# View specific test results
cat regression_results/smoke_test/test_statistics.json | jq .
```

## Test Status Codes

- **PASS** ✓ - Test passed (RTL matches Python within tolerance)
- **FAIL** ✗ - Test failed (RTL diverged from Python)
- **ERROR** ✗ - Test crashed or binary not found
- **SKIP** - Test was skipped (not enabled or filtered out)

## Troubleshooting

### RTL Binary Not Found

```
RuntimeError: RTL binary not found. Tried: Vslime_top, slime_verilator_full, Vslime_top_agent
```

**Solution**: Build the RTL simulator
```bash
cd rtl/sim
# Use appropriate build command based on your project
# This might be: make verilator, bash build_verilator.sh, etc.
```

### Python Simulator Not Found

```
FileNotFoundError: [Errno 2] No such file or directory: 'slime_simulator.py'
```

**Solution**: Run from project root directory
```bash
cd /home/reson/SlimeSimulator
python run_regression_tests.py
```

### No Agent Dumps in Comparison

```
WARNING: No agent dumps found for comparison
```

**Solution**: Ensure simulators are dumping agent state to:
- Python: `python_agent_dumps/agent_state_step_*.json`
- RTL: `rtl/sim/rtl_agent_dumps/agent_state_step_*.json`

Check that Python and RTL simulators are writing these files.

### Simulation Timeout

```
RuntimeError: RTL simulation timeout (>20 min)
```

**Solution**: Test with fewer agents or steps
```bash
python run_regression_tests.py --test-id 6 --no-rtl  # Use smaller test
```

## Custom Tests

Add your own tests to `regression_tests.csv`:

```csv
11,my_custom_test,integration,200,320x240,50,true,true,true,true,true,true,regression_results/custom,My test description
```

Then run:

```bash
python run_regression_tests.py --test-id 11
```

## Performance Tips

- Start with smoke tests (`--test-type smoke`) for quick validation
- Run unit tests for specific features
- Reserve full integration tests for CI/CD or nightly runs
- Use `--no-rtl` for fast Python-only validation during development

## Next Steps

Once tests are passing, you can:

1. **Integrate with CI/CD** - See `REGRESSION_TESTING_GUIDE.md` for GitHub Actions examples
2. **Add more tests** - Customize `regression_tests.csv` for your needs
3. **Set up nightly runs** - Run full test suite on schedule
4. **Monitor results** - Track error metrics over time

## Files

- `run_regression_tests.py` - Test runner
- `regression_tests.csv` - Test definitions
- `REGRESSION_TESTING_GUIDE.md` - Complete documentation
- `REGRESSION_TESTS_QUICK_START.txt` - Quick reference
- `regression_results/` - Output directory (created on first run)
