# Validation Scripts - Quick Start Guide

## 1-Minute Quick Start

```bash
cd /home/reson/SlimeSimulator

# Activate Python virtual environment
source .venv/bin/activate

# Run all validation tests (takes ~2 minutes)
python3 scripts/run_all_validations.py

# Or run individual tests
python3 scripts/validate_lfsr.py
python3 scripts/validate_fixed_point.py
python3 scripts/validate_trig.py
python3 scripts/validate_vga.py
python3 scripts/validate_python_reference.py --steps 1,5,10
```

## Expected Output

```
======================================================================
  Master Validation Test Suite
======================================================================
Mode: Standard
Output: validation_output
======================================================================

1/5 Running Python Reference Validation...
2/5 Running LFSR Validation...
3/5 Running Fixed-Point Validation...
4/5 Running Trigonometric LUT Validation...
5/5 Running VGA Timing Validation...

======================================================================
  VALIDATION SUMMARY
======================================================================
  [✓ PASS] validate_python_reference.py
  [✓ PASS] validate_lfsr.py
  [✓ PASS] validate_fixed_point.py
  [✓ PASS] validate_trig.py
  [✓ PASS] validate_vga.py
======================================================================
Passed: 5/5
Success Rate: 100.0%
======================================================================
```

## What Gets Tested?

### LFSR (Random Number Generator)
- ✓ Initialization with seed
- ✓ Sequence generation (deterministic)
- ✓ Statistical distribution (~50/50 bits)
- ✓ Never generates zero state

### Fixed-Point Arithmetic (Q12.12)
- ✓ Float ↔ fixed-point conversion
- ✓ Multiplication accuracy
- ✓ Edge cases (negatives, zeros, overflow)
- ✓ Range limits and clamping

### Trigonometric Lookups
- ✓ 1024-entry sin/cos tables
- ✓ Special angles (0°, 90°, 180°, 270°)
- ✓ Pythagorean identity (sin²+cos²=1)
- ✓ Symmetry properties

### VGA Timing (640x480@60Hz)
- ✓ Correct horizontal/vertical timing
- ✓ Sync signal positioning
- ✓ Blanking intervals
- ✓ Frame rate calculation

### Python Reference
- ✓ Generates reference outputs for 1, 5, 10+ steps
- ✓ Saves trail maps and LFSR states
- ✓ Reproducibility (identical runs)

## Output Files

All validation results go to `validation_output/`:

```
validation_output/
├── lfsr/
│   └── lfsr_32bit_1000steps.txt          # LFSR sequence for comparison
├── fixed_point/
│   └── (test results)
├── trig/
│   ├── sin_lut_ref.hex                   # RTL-compatible sin table
│   ├── cos_lut_ref.hex                   # RTL-compatible cos table
│   └── trig_lut_table.csv                # Human-readable table
├── vga/
│   └── timing_diagram.txt                # VGA timing diagram
└── python_reference/
    ├── index.json                        # Master index
    ├── steps_0001/
    │   ├── state.json                    # Simulation state
    │   ├── trail_map.bin                 # Binary trail map
    │   └── trail_map.png                 # Visualization
    └── steps_0010/
        └── ...
```

## Common Issues

### Import Error
**Problem:** `ModuleNotFoundError: No module named 'numpy'`

**Solution:**
```bash
# Make sure to activate the virtual environment
source .venv/bin/activate

# Or install dependencies
pip3 install numpy scipy pillow
```

### Permission Denied
**Problem:** `Permission denied: './scripts/validate_lfsr.py'`

**Solution:**
```bash
chmod +x scripts/*.py
# Or run with python3 explicitly
python3 scripts/validate_lfsr.py
```

## Advanced Usage

### Compare with RTL Simulation

```bash
# 1. Generate Python reference
python3 scripts/validate_python_reference.py --steps 10 --seed 0xDEADBEEF

# 2. Run your RTL simulation (produces rtl_output.txt)

# 3. Compare
python3 scripts/validate_lfsr.py --compare-rtl rtl_output.txt
```

### Generate RTL Test Vectors

```bash
# Generate sin/cos LUT files for RTL
python3 scripts/validate_trig.py --generate-rtl

# Outputs:
# validation_output/trig/sin_lut_ref.hex
# validation_output/trig/cos_lut_ref.hex
```

### Save Detailed Reports

```bash
# Get JSON reports for all tests
python3 scripts/run_all_validations.py --save-json

# Individual tests
python3 scripts/validate_lfsr.py --save-json
python3 scripts/validate_fixed_point.py --save-json
```

## Integration with Build System

Add to your Makefile or build script:

```makefile
.PHONY: validate
validate:
	@echo "Running validation tests..."
	@cd $(PROJECT_ROOT) && \
	  source .venv/bin/activate && \
	  python3 scripts/run_all_validations.py
	@echo "Validation complete!"

.PHONY: validate-quick
validate-quick:
	@cd $(PROJECT_ROOT) && \
	  source .venv/bin/activate && \
	  python3 scripts/run_all_validations.py --quick
```

## Next Steps

For more details, see:
- `VALIDATION_README.md` - Comprehensive documentation
- Individual script `--help` - Detailed options
- Output JSON files - Test results and data

## Questions?

Each script supports `--help`:
```bash
python3 scripts/validate_lfsr.py --help
python3 scripts/validate_fixed_point.py --help
python3 scripts/validate_trig.py --help
python3 scripts/validate_vga.py --help
python3 scripts/validate_python_reference.py --help
```
