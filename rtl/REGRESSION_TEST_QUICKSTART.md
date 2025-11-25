# Regression Test Quick Start Guide

## Prerequisites

1. **Python 3.7+** with numpy installed
2. **Vivado** (for FPGA programming) - optional for reference-only testing
3. **FPGA** (Basys3) connected via JTAG - optional for reference-only testing

## Installation

```bash
# Navigate to RTL directory
cd rtl/

# Activate Python virtual environment (if using one)
source ../.venv/bin/activate

# Install dependencies (if not already installed)
pip install numpy pillow  # pillow is optional for visualizations
```

## Quick Start - Python Reference Only

Perfect for developing and testing the framework without FPGA hardware:

```bash
# Generate Python reference trail maps
python regression_test.py --reference-only
```

**Output**:
```
08:45:32 [INFO] Starting RTL Regression Test
08:45:32 [INFO] Configuration: 160x120, 1000 agents, iterations [1, 5, 10, 20]
08:45:32 [STEP] STEP 1: Generate Python Reference Trail Maps
08:45:32 [INFO] Generating Python reference...
08:45:35 [SUCCESS] Generating Python reference completed successfully
08:45:35 [SUCCESS] Reference generation completed successfully
08:45:35 [INFO] Total time: 3.2 seconds
```

Results saved to: `regression_test_results/reference/`

## Quick Start - Full Workflow (with FPGA)

**Note**: Currently requires JTAG2AXI and VIO IP integration in RTL design.

```bash
# Full test: program FPGA and compare
python regression_test.py --bitstream path/to/slime_top.bit
```

## Quick Start - Individual Components

### 1. Generate Reference Only

```bash
python generate_python_ref.py \
    --width 160 --height 120 \
    --agents 1000 \
    --iterations 1,5,10,20 \
    --output-dir my_test/reference
```

### 2. Compare Existing Trail Maps

```bash
python compare_trails.py \
    --reference my_test/reference \
    --rtl my_test/rtl_capture \
    --iterations 1,5,10,20 \
    --visualize
```

### 3. FPGA Control (when hardware ready)

```bash
# Program and capture
python fpga_controller.py \
    --bitstream build/slime_top.bit \
    --iterations 1,5,10,20

# Or capture only (already programmed)
python fpga_controller.py \
    --no-program \
    --iterations 1,5,10,20
```

## Common Use Cases

### Development Testing (No FPGA)

Test changes to Python reference model:

```bash
# Quick test with fewer iterations
python regression_test.py --reference-only --iterations 1,5
```

### Pre-Commit Verification

Run before committing RTL changes:

```bash
# Generate reference baseline
python regression_test.py --reference-only

# Later, after RTL changes and rebuild
python regression_test.py --bitstream new_build/slime_top.bit
```

### Custom Resolution Testing

```bash
python regression_test.py --reference-only \
    --width 320 --height 240 \
    --agents 2000
```

### Extended Test Suite

```bash
python regression_test.py --reference-only \
    --iterations 1,2,5,10,15,20,30,50,100 \
    --visualize
```

### Strict Validation

```bash
python regression_test.py \
    --bitstream build/slime_top.bit \
    --threshold 99.0 \
    --iterations 1,5,10,20,50
```

## Understanding Results

### Test Output Directory Structure

```
regression_test_results/
├── reference/                      # Python reference trail maps
│   ├── trail_iter_001.bin         # Binary trail map files
│   ├── trail_iter_005.bin
│   ├── trail_iter_010.bin
│   ├── trail_iter_020.bin
│   └── final_state.txt            # Agent positions for debugging
├── rtl_capture/                   # RTL captured trail maps
│   ├── trail_iter_001.bin
│   ├── trail_iter_005.bin
│   ├── trail_iter_010.bin
│   └── trail_iter_020.bin
├── visualizations/                # Diff images (if --visualize)
│   ├── diff_iter_001.png
│   ├── diff_iter_005.png
│   ├── diff_iter_010.png
│   └── diff_iter_020.png
├── comparison_report.csv          # Numerical comparison results
├── detailed_analysis.txt          # Full analysis with trends
└── test_summary.txt              # Overall test summary
```

### Reading Comparison Results

#### CSV Format (spreadsheet-friendly)
```csv
iteration,total_pixels,nonzero_ref,nonzero_rtl,matching_pixels,match_percentage,max_diff,mean_diff,rms_diff,status
1,19200,1000,1000,19180,99.90,10,0.034,0.456,PASS
5,19200,5000,4990,19050,99.22,15,0.123,0.789,PASS
```

#### Console Output (human-readable)
```
==========================================================================================
Trail Map Comparison Results
==========================================================================================
Iter |  Written |   Match | MaxDiff | MeanDiff |     RMS | Status
------------------------------------------------------------------------------------------
   1 |     1000 |  99.90% |    10.0 |    0.034 |   0.456 |   PASS
   5 |     5000 |  99.22% |    15.0 |    0.123 |   0.789 |   PASS
  10 |    10000 |  98.50% |    20.0 |    0.234 |   1.234 |   PASS
  20 |    15000 |  97.00% |    25.0 |    0.456 |   2.345 |   PASS
==========================================================================================
```

### Key Metrics Explained

- **Written**: Number of non-zero pixels (where agents deposited trail)
- **Match**: Percentage of pixels that exactly match between reference and RTL
- **MaxDiff**: Maximum absolute difference between any pixel
- **MeanDiff**: Average absolute difference across all pixels
- **RMS**: Root mean square difference (emphasizes larger errors)
- **Status**: PASS if match percentage ≥ threshold (default 95%)

### Expected Match Percentages

| Implementation Stage | Expected Match | Notes |
|---------------------|----------------|-------|
| Test pattern | 0-50% | Current state - pattern generator only |
| Fixed-point agent processor | 95-98% | Some rounding differences |
| Optimized RTL | 98-99.5% | Minimal differences |
| Bit-exact | 99.9%+ | Rare, requires careful design |

## Troubleshooting

### "ModuleNotFoundError: No module named 'numpy'"

```bash
pip install numpy
# or
source ../.venv/bin/activate
```

### "File not found: trail_iter_XXX.bin"

Make sure you generated reference data first:
```bash
python regression_test.py --reference-only
```

### "No hardware targets found"

FPGA not connected or Vivado not in PATH. For development:
```bash
python regression_test.py --reference-only
```

### "WARNING: Memory read not yet implemented"

This is expected - FPGA controller needs JTAG2AXI IP integration.
Framework is ready, but RTL integration is pending.

## Next Steps

1. **Review Results**: Check `regression_test_results/detailed_analysis.txt`
2. **Visualize Differences**: Use `--visualize` flag and view PNG files
3. **Adjust Threshold**: Use `--threshold` if default 95% is too strict/lenient
4. **Integrate with CI**: See `REGRESSION_TEST_README.md` for CI/CD examples

## Getting Help

```bash
# Detailed help for any script
python regression_test.py --help
python generate_python_ref.py --help
python compare_trails.py --help
python fpga_controller.py --help
```

## Example Session

```bash
# 1. Generate reference (takes ~30 seconds)
$ python regression_test.py --reference-only
08:45:32 [INFO] Starting RTL Regression Test
...
08:45:35 [SUCCESS] Reference generation completed successfully

# 2. Check output
$ ls -lh regression_test_results/reference/
total 80K
-rw-rw-r-- 1 user user 19K Nov 24 08:45 trail_iter_001.bin
-rw-rw-r-- 1 user user 19K Nov 24 08:45 trail_iter_005.bin
-rw-rw-r-- 1 user user 19K Nov 24 08:45 trail_iter_010.bin
-rw-rw-r-- 1 user user 19K Nov 24 08:45 trail_iter_020.bin
-rw-rw-r-- 1 user user 15K Nov 24 08:45 final_state.txt

# 3. View trail map (requires Python)
$ python -c "
import numpy as np
import matplotlib.pyplot as plt
trail = np.fromfile('regression_test_results/reference/trail_iter_020.bin', dtype=np.uint8)
trail = trail.reshape(120, 160)
plt.imshow(trail, cmap='hot', interpolation='nearest')
plt.title('Trail Map at Iteration 20')
plt.colorbar()
plt.savefig('trail_preview.png')
print('Saved to trail_preview.png')
"

# 4. Compare with another run
$ python compare_trails.py \
    --reference regression_test_results/reference \
    --rtl another_test/reference \
    --iterations 1,5,10,20
```

## Performance Tips

**Faster Testing**:
- Use fewer agents: `--agents 100`
- Test fewer points: `--iterations 1,5`
- Skip visualization: omit `--visualize`

**Slower but More Thorough**:
- More agents: `--agents 5000`
- More test points: `--iterations 1,2,5,10,15,20,30,50,100`
- Generate visualizations: `--visualize`

## Tips and Best Practices

1. **Always use same seed** (0xDEADBEEF) for reproducibility
2. **Start with reference-only** to validate framework
3. **Use visualizations** to debug unexpected differences
4. **Check trend analysis** in detailed_analysis.txt
5. **Save baselines** when RTL works correctly
6. **Run before committing** to catch regressions early

---

**Quick Command Reference Card**

```bash
# Most common commands
python regression_test.py --reference-only              # Dev testing
python regression_test.py --bitstream build/slime.bit   # Full test
python compare_trails.py --ref ref/ --rtl rtl/ --visualize  # Compare only

# Customization
--iterations 1,5,10,20      # Test points
--threshold 99.0            # Pass criteria
--agents 500                # Fewer agents (faster)
--visualize                 # Generate diff images

# Help
python regression_test.py --help
```

