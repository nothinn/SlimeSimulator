# Python-Based FPGA Validation Scripts

Comprehensive testing suite for validating the FPGA implementation against the Python reference model.

## Overview

This directory contains practical Python-based validation scripts that do not rely on cocotb. These scripts validate the FPGA implementation by:

1. **Generating bit-accurate reference data** from the Python model
2. **Testing individual components** (LFSR, fixed-point, trig, VGA)
3. **Comparing RTL outputs** with Python golden references
4. **Producing detailed reports** in both human-readable and JSON formats

## Quick Start

### Run All Validations (Standard Mode)
```bash
cd /home/reson/SlimeSimulator
python3 scripts/run_all_validations.py
```

### Quick Validation (Fewer Test Cases)
```bash
python3 scripts/run_all_validations.py --quick
```

### Comprehensive Validation (All Tests)
```bash
python3 scripts/run_all_validations.py --comprehensive --save-json
```

## Individual Validation Scripts

### 1. validate_python_reference.py

Validates the Python reference implementation and generates test data.

**Features:**
- Runs simulation for multiple step counts (1, 5, 10, 20, 50, 100)
- Saves LFSR states, fixed-point results, and trail maps
- Exports to JSON and binary formats for RTL comparison
- Tests reproducibility (deterministic behavior)

**Usage:**
```bash
# Standard run with default parameters
python3 scripts/validate_python_reference.py

# Custom seed and step counts
python3 scripts/validate_python_reference.py --steps 1,5,10,50 --seed 0x12345678

# With reproducibility testing
python3 scripts/validate_python_reference.py --test-reproducibility --verbose

# Save JSON report
python3 scripts/validate_python_reference.py --save-json
```

**Output Files:**
- `validation_output/python_reference/index.json` - Master index
- `validation_output/python_reference/steps_NNNN/state.json` - State for N steps
- `validation_output/python_reference/steps_NNNN/trail_map.bin` - Binary trail map
- `validation_output/python_reference/steps_NNNN/trail_map.npy` - NumPy trail map
- `validation_output/python_reference/steps_NNNN/trail_map.png` - Visualization

### 2. validate_lfsr.py

Tests LFSR sequence generation and statistical properties.

**Features:**
- Validates sequences up to 1000+ steps
- Tests bit-exact determinism
- Validates statistical distribution (~50% ones)
- Tests all supported LFSR widths (8, 16, 24, 32, 48, 64 bits)
- Compares with RTL simulation outputs

**Usage:**
```bash
# Test 32-bit LFSR with 1000 steps
python3 scripts/validate_lfsr.py --width 32 --steps 1000

# Test all LFSR widths
python3 scripts/validate_lfsr.py --all-widths

# With statistical tests
python3 scripts/validate_lfsr.py --statistical-tests --verbose

# Compare with RTL output
python3 scripts/validate_lfsr.py --compare-rtl rtl_lfsr_output.txt
```

**Tests Performed:**
- ✓ Initialization (seed applied correctly)
- ✓ Sequence generation (requested length)
- ✓ Determinism (identical runs with same seed)
- ✓ Non-zero states (LFSR never outputs 0)
- ✓ Bit distribution (approximately 50/50)
- ✓ Periodicity (maximal-length sequence)

### 3. validate_fixed_point.py

Tests Q12.12 fixed-point arithmetic implementation.

**Features:**
- Validates conversion accuracy (≤1 LSB error)
- Tests multiplication with various operands
- Tests edge cases: negative numbers, overflow, saturation
- Generates comprehensive test matrices
- Compares with RTL multiplication results

**Usage:**
```bash
# Standard fixed-point tests
python3 scripts/validate_fixed_point.py

# Custom bit widths
python3 scripts/validate_fixed_point.py --int-bits 10 --frac-bits 14

# Comprehensive tests
python3 scripts/validate_fixed_point.py --comprehensive

# Generate multiplication table
python3 scripts/validate_fixed_point.py --generate-table --table-samples 200

# Compare with RTL
python3 scripts/validate_fixed_point.py --compare-rtl rtl_mult_results.txt
```

**Tests Performed:**
- ✓ Conversion accuracy (float ↔ fixed-point)
- ✓ Range limits (min/max representable values)
- ✓ Basic multiplication (standard test cases)
- ✓ Edge cases (zeros, small values, fractions)
- ✓ Overflow handling
- ✓ Clamping/saturation

### 4. validate_trig.py

Validates sin/cos lookup tables.

**Features:**
- Generates all 1024 table entries
- Verifies bit-exact match with RTL ROMs
- Tests mathematical properties (symmetry, periodicity)
- Tests special angles (0°, 45°, 90°, 180°, 270°)
- Exports RTL-compatible .hex files

**Usage:**
```bash
# Standard trig validation
python3 scripts/validate_trig.py

# With symmetry tests
python3 scripts/validate_trig.py --test-symmetry

# All tests
python3 scripts/validate_trig.py --test-all

# Generate RTL hex files
python3 scripts/validate_trig.py --generate-rtl

# Export as CSV
python3 scripts/validate_trig.py --export-csv

# Compare with RTL LUTs
python3 scripts/validate_trig.py --compare-rtl sin_lut.hex cos_lut.hex
```

**Tests Performed:**
- ✓ Table generation (correct sizes)
- ✓ Special angles (0, π/4, π/2, π, 3π/2)
- ✓ Pythagorean identity (sin²+cos²=1)
- ✓ Symmetry properties
- ✓ Monotonicity (increasing/decreasing in quadrants)
- ✓ Range bounds (values in [-1, 1])

### 5. validate_vga.py

Validates VGA timing signals and framebuffer operations.

**Features:**
- Validates 640x480@60Hz timing
- Checks hsync/vsync correctness
- Simulates multiple frames
- Verifies pixel ordering and blanking
- Compares with RTL simulation

**Usage:**
```bash
# Standard VGA validation
python3 scripts/validate_vga.py

# Simulate multiple frames
python3 scripts/validate_vga.py --simulate-frames 10

# Generate timing diagram
python3 scripts/validate_vga.py --generate-diagram

# 800x600 mode
python3 scripts/validate_vga.py --mode 800x600

# Compare with RTL
python3 scripts/validate_vga.py --compare-rtl vga_timing.csv
```

**Tests Performed:**
- ✓ Timing parameters (frame rate, pixel clock)
- ✓ Sync regions (hsync/vsync positioning)
- ✓ Blanking intervals (front/back porch)
- ✓ Frame simulation (pixel counts)

## Output Structure

All validation scripts generate organized output:

```
validation_output/
├── python_reference/
│   ├── index.json
│   ├── steps_0001/
│   ├── steps_0005/
│   └── ...
├── lfsr/
│   ├── lfsr_32bit_1000steps.txt
│   └── lfsr_validation_YYYYMMDD_HHMMSS.json
├── fixed_point/
│   ├── multiplication_table.csv
│   └── fixed_point_validation_YYYYMMDD_HHMMSS.json
├── trig/
│   ├── sin_lut_ref.hex
│   ├── cos_lut_ref.hex
│   ├── trig_lut_table.csv
│   └── trig_validation_YYYYMMDD_HHMMSS.json
├── vga/
│   ├── timing_diagram.txt
│   └── vga_validation_YYYYMMDD_HHMMSS.json
└── master_validation_YYYYMMDD_HHMMSS.json
```

## Common Options

All scripts support these common options:

- `--verbose` - Detailed output during execution
- `--save-json` - Save detailed JSON report
- `--output-dir DIR` - Specify output directory
- `--help` - Show detailed help message

## Integration with RTL Workflow

### Generate Reference Data for RTL Comparison

1. **Generate Python reference outputs:**
```bash
python3 scripts/validate_python_reference.py --steps 10 --seed 0xDEADBEEF
```

2. **Run RTL simulation** (using your preferred tool)

3. **Compare RTL output with Python reference:**
```bash
# Compare LFSR
python3 scripts/validate_lfsr.py --compare-rtl rtl_sim/lfsr_output.txt

# Compare fixed-point multiplication
python3 scripts/validate_fixed_point.py --compare-rtl rtl_sim/mult_results.txt

# Compare trig LUTs
python3 scripts/validate_trig.py --compare-rtl rtl_sim/sin_lut.hex rtl_sim/cos_lut.hex
```

### Expected RTL File Formats

**LFSR Output (lfsr_output.txt):**
```
# LFSR sequence
1: 0xDEADBEEF
2: 0xBD5B7DDE
3: 0x7AB6FBBD
...
```

**Fixed-Point Multiplication (mult_results.txt):**
```
# a_hex, b_hex, result_hex
0x00001000, 0x00002000, 0x00002000
0x00000800, 0x00000800, 0x00000400
...
```

**Trig LUT (sin_lut.hex, cos_lut.hex):**
```
00000000
00000C90
00001920
...
```

**VGA Timing (vga_timing.csv):**
```
# pixel_count, h_count, v_count, hsync, vsync, visible
0, 0, 0, 1, 1, 1
1, 1, 0, 1, 1, 1
...
```

## Troubleshooting

### Import Errors

If you get `ImportError: Could not import slime_simulator.py`:
```bash
# Ensure slime_simulator.py is in project root
cd /home/reson/SlimeSimulator
python3 scripts/validate_python_reference.py
```

### Missing Dependencies

Install required packages:
```bash
pip3 install numpy scipy pillow
```

### Permission Denied

Make scripts executable:
```bash
chmod +x scripts/*.py
```

## Test Reports

### Human-Readable Output

All scripts print formatted test results to stdout:
```
======================================================================
  LFSR Validation
======================================================================
[PASS] Initialization
      seed: 0xDEADBEEF
      initial_state: 0xDEADBEEF
[PASS] Sequence Generation (1000 steps)
[PASS] Determinism (1000 steps)
...
======================================================================
Total: 6/6 tests passed
Success Rate: 100.0%
======================================================================
```

### JSON Reports

With `--save-json`, detailed JSON reports are generated:
```json
{
  "timestamp": "2025-11-25T12:34:56",
  "configuration": {
    "steps": 1000,
    "seed": "0xDEADBEEF"
  },
  "summary": {
    "total_tests": 6,
    "passed": 6,
    "failed": 0
  },
  "tests": [...]
}
```

## Performance

Typical execution times on modern hardware:

- `validate_python_reference.py` - 30-60s (depends on step counts)
- `validate_lfsr.py` - 5-10s (standard), 60s (all widths)
- `validate_fixed_point.py` - 2-5s (standard), 30s (comprehensive)
- `validate_trig.py` - 2-5s (standard), 10s (all tests)
- `validate_vga.py` - 1-3s

**Full suite:** 1-2 minutes (quick), 3-5 minutes (comprehensive)

## Continuous Integration

These scripts are designed for CI/CD integration:

```bash
# CI/CD Example
python3 scripts/run_all_validations.py --save-json
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "✓ All validations passed"
else
    echo "✗ Some validations failed"
    exit 1
fi
```

## Contributing

When adding new validation tests:

1. Follow the existing pattern (class-based validator)
2. Add `--verbose` and `--save-json` support
3. Use consistent error handling
4. Generate both human-readable and JSON output
5. Add to `run_all_validations.py`

## License

Part of the SlimeSimulator project. See main project LICENSE.

## Support

For issues or questions:
1. Check this README
2. Review script `--help` output
3. Examine JSON reports with `--save-json`
4. Check `validation_output/` for detailed logs
