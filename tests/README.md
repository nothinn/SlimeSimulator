# SlimeSimulator Test Suite

Comprehensive regression testing for the SlimeSimulator FPGA project.

## Directory Structure

```
tests/
├── unit/           # Cocotb unit tests (fast, run on every commit)
├── integration/    # Verilator integration tests (medium, run on PRs)
├── system/         # Full system tests (slow, run nightly)
└── synthesis/      # Vivado synthesis validation (very slow, run on release)
```

## Quick Start

### Run All Unit Tests
```bash
cd tests/unit
make test_all
```

### Run Integration Tests
```bash
cd tests/integration
python test_python_rtl_match.py
```

### Run Full Regression Suite
```bash
./run_all_tests.sh
```

## Test Levels

### Unit Tests (tests/unit/)
- Fast execution (<5 minutes total)
- Test individual RTL modules in isolation
- Use Cocotb for stimulus generation
- Run on every commit via CI

**Modules tested:**
- LFSR (random number generator)
- Fixed-point multiplier
- Trigonometric lookup tables
- VGA controller
- Button debouncer

### Integration Tests (tests/integration/)
- Medium execution (10-30 minutes)
- Test subsystem interactions
- Use Verilator for full RTL simulation
- Compare against Python reference model
- Run on pull requests via CI

**Test scenarios:**
- Agent processor pipeline validation
- Trail map memory consistency
- Python vs RTL bit-exact comparison

### System Tests (tests/system/)
- Long execution (hours)
- Full-scale end-to-end validation
- 1000 agents, 100+ simulation steps
- Performance and stability testing
- Run nightly via CI

### Synthesis Tests (tests/synthesis/)
- Very long execution (30min - 2hrs)
- Vivado synthesis and timing validation
- Resource utilization tracking
- Run on release branches only

## CI/CD Integration

Tests are automatically run via GitHub Actions:

- **On every push:** Unit tests
- **On pull requests:** Unit + Integration tests
- **Nightly (2 AM UTC):** All tests including system tests
- **On release tags:** Full regression + synthesis validation

See `.github/workflows/` for workflow definitions.

## Adding New Tests

### Unit Test Template
```python
import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def test_my_module(dut):
    """Test description"""
    # Test logic here
    assert dut.output.value == expected
```

### Integration Test Template
```python
import sys
sys.path.append('../../rtl/sim')
from python_reference import MyModule

def test_integration():
    # Compare RTL vs Python
    assert rtl_result == python_result
```

## Test Reports

Test results are automatically uploaded as CI artifacts:
- Unit test XML reports
- Integration test comparison data
- System test performance metrics
- Synthesis timing reports

## Troubleshooting

### Common Issues

**Verilator not found:**
```bash
sudo apt-get install verilator
```

**Cocotb import errors:**
```bash
source .venv/bin/activate
pip install cocotb
```

**Vivado not in PATH:**
```bash
source /path/to/Vivado/settings64.sh
```

## Documentation

- [Regression Test Plan](../REGRESSION_TEST_PLAN.md) - Detailed test strategy
- [CLAUDE.md](../CLAUDE.md) - Build and test commands
- [Unit Test Guide](unit/README.md) - Cocotb test details
- [Integration Test Guide](integration/README.md) - Verilator test details
