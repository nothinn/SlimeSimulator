# Regression Testing Framework for SlimeSimulator

## Overview

The regression testing framework provides a CSV-driven system for defining, executing, and validating comprehensive tests across the SlimeSimulator project. Tests can compare RTL vs Python implementations, generate visualizations, and track performance metrics.

## Quick Start

### Run All Tests
```bash
python run_regression_tests.py
```

### Run Specific Test
```bash
python run_regression_tests.py --test-id 1
```

### Run Tests by Type
```bash
python run_regression_tests.py --test-type integration
```

### Skip RTL (Python only)
```bash
python run_regression_tests.py --no-rtl
```

### Verbose Output
```bash
python run_regression_tests.py --verbose
```

## Test Configuration (regression_tests.csv)

### CSV Schema

| Column | Type | Description |
|--------|------|-------------|
| test_id | int | Unique test identifier |
| test_name | string | Human-readable test name |
| test_type | enum | smoke, unit, integration, performance, stress |
| num_agents | int | Number of agents to simulate |
| resolution | string | Canvas size (WIDTHxHEIGHT, e.g., 320x240) |
| num_steps | int | Simulation duration in steps |
| python_enabled | bool | Run Python reference simulation |
| rtl_enabled | bool | Run RTL simulation |
| generate_trajectory_html | bool | Create interactive trajectory viewer |
| generate_trail_map | bool | Create trail map visualization |
| generate_comparison_images | bool | Create side-by-side comparison frames |
| generate_statistics | bool | Generate JSON statistics report |
| output_dir | string | Directory for test outputs |
| description | string | Test purpose and details |

### Test Types

**smoke** - Quick sanity checks, minimal agents/steps
- Fast execution (<30 sec)
- Catches obvious breakages
- Run before every commit

**unit** - Component-level validation
- Tests specific features (init, decay, sensory logic)
- May run Python or RTL only
- Typically small scale (10-100 agents, 0-50 steps)

**integration** - End-to-end RTL vs Python comparison
- Full simulation execution
- Both Python and RTL enabled
- Medium scale (100-500 agents, 10-100 steps)

**performance** - Throughput and scaling tests
- High agent counts (1000+)
- Minimal steps (10-50)
- Measures FPGA efficiency

**stress** - Long-duration stability tests
- Extended simulations (100+ steps)
- May run RTL only
- Validates memory management

### Example Test Entry

```csv
test_id,test_name,test_type,num_agents,resolution,num_steps,python_enabled,rtl_enabled,generate_trajectory_html,generate_trail_map,generate_comparison_images,generate_statistics,output_dir,description
1,smoke_test_100_agents,smoke,100,320x240,10,true,true,true,false,false,false,regression_results/smoke_test,Quick sanity check with 100 agents
```

## Output Structure

Each test generates output in its designated directory:

```
regression_results/
├── test_name/
│   ├── python/                          # Python simulation output
│   │   ├── agent_dump_step_00000.json
│   │   ├── agent_dump_step_00001.json
│   │   └── ...
│   ├── rtl/                             # RTL simulation output
│   │   ├── agent_state_step_00000.json
│   │   ├── agent_state_step_00001.json
│   │   └── ...
│   ├── trajectory_viewer.html           # Interactive viewer (if enabled)
│   ├── trail_map.png                    # Trail visualization (if enabled)
│   ├── comparison_00000.png             # Comparison frames (if enabled)
│   ├── comparison_00001.png
│   ├── comparison_stats.json            # Statistics (if enabled)
│   └── test_statistics.json             # Test metadata
├── REPORT.md                            # Summary report
└── regression_tests.log                 # Full execution log
```

## Test Execution Flow

```
┌─────────────────────────────┐
│  Load Test Config (CSV)     │
└──────────────┬──────────────┘
               │
         ┌─────▼─────┐
         │ Filter    │ (by ID, type, etc.)
         │ Tests     │
         └─────┬─────┘
               │
    ┌──────────▼──────────┐
    │ For Each Test:      │
    └──────────┬──────────┘
               │
     ┌─────────┴─────────┐
     │                   │
┌────▼────┐       ┌──────▼─────┐
│ Python  │       │ RTL        │
│ Sim     │       │ Sim        │
└────┬────┘       └──────┬─────┘
     │                   │
     └─────────┬─────────┘
               │
         ┌─────▼──────┐
         │ Compare    │
         │ Results    │
         └─────┬──────┘
               │
    ┌──────────▼────────────┐
    │ Generate Outputs:     │
    │ - HTML viewer         │
    │ - Trail maps          │
    │ - Comparisons         │
    │ - Statistics          │
    └──────────┬────────────┘
               │
         ┌─────▼──────┐
         │ Generate   │
         │ Report     │
         └────────────┘
```

## Test Result Status

- **PASS** - Test completed successfully, all validations passed
- **FAIL** - Test completed but validation failed (mismatches >tolerance)
- **ERROR** - Test execution error (crashed, missing files, etc.)
- **SKIP** - Test was skipped (due to CLI flags or config)

## Defining Custom Tests

### Example: New Performance Test

```csv
11,scaling_test_2000,performance,2000,320x240,30,false,true,false,false,false,true,regression_results/2000agents_30steps,Test with 2000 agents (max limit)
```

### Example: New Unit Test

```csv
12,agent_wrapping_validation,unit,50,320x240,10,true,true,false,false,false,true,regression_results/wrapping_test,Verify toroidal wrapping at boundaries
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Regression Tests
on: [push, pull_request]
jobs:
  regression:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
      - name: Run smoke tests
        run: python run_regression_tests.py --test-type smoke
      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: regression-results
          path: regression_results/
```

## Troubleshooting

### Tests Not Found
```bash
# Verify CSV exists and is readable
file regression_tests.csv
head regression_tests.csv
```

### RTL Compilation Issues
```bash
# Rebuild Verilator
cd rtl/sim
verilator --cc --exe ... (see CLAUDE.md for full command)
```

### Python Simulation Fails
```bash
# Test Python reference directly
python slime_simulator.py --agents 100 --steps 10 --display
```

### Memory Issues with Large Tests
```bash
# Reduce agent count or steps
python run_regression_tests.py --test-id 6 --no-rtl  # RTL uses more memory
```

## Performance Baseline

Expected execution times (on 2.4 GHz CPU with RTL):

| Test Type | Agents | Steps | Time |
|-----------|--------|-------|------|
| Smoke | 100 | 10 | ~5 sec |
| Unit | 100 | 5 | ~3 sec |
| Integration | 100 | 100 | ~30 sec |
| Performance | 1000 | 20 | ~60 sec |
| Stress | 100 | 200 | ~90 sec |

## Continuous Monitoring

### Run nightly tests
```bash
0 2 * * * cd /path/to/SlimeSimulator && python run_regression_tests.py --test-type integration,performance > /var/log/regression.log 2>&1
```

### Check test results
```bash
tail -50 regression_results/regression_tests.log
cat regression_results/REPORT.md
```

## Key Features

✓ **CSV-based configuration** - Easy to define tests without code changes
✓ **Parallel execution ready** - Can be extended for concurrent test runs
✓ **Comprehensive reporting** - JSON, HTML, and Markdown output formats
✓ **Performance tracking** - Baseline comparisons and regression detection
✓ **Integration flexibility** - Works with CI/CD pipelines
✓ **Output generation** - Automatic creation of visualizations and statistics

## See Also

- `regression_tests.csv` - Test configuration file
- `run_regression_tests.py` - Test execution engine
- `CLAUDE.md` - Full project documentation
- `slime_simulator.py` - Python reference implementation
