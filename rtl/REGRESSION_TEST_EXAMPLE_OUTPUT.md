# Regression Test Example Output

This document shows example output from the regression testing framework.

## Example 1: Reference-Only Test (Successful)

### Command
```bash
python regression_test.py --reference-only --iterations 1,5,10,20
```

### Console Output
```
08:45:32 [INFO] ================================================================================
08:45:32 [INFO] Starting RTL Regression Test
08:45:32 [INFO] ================================================================================
08:45:32 [INFO] Configuration: 160x120, 1000 agents, iterations [1, 5, 10, 20]
08:45:32 [STEP] ================================================================================
08:45:32 [STEP] STEP 1: Generate Python Reference Trail Maps
08:45:32 [STEP] ================================================================================
08:45:32 [INFO] Generating Python reference...
08:45:32 [INFO]   Command: /usr/bin/python3 generate_python_ref.py --width 160 --height 120 --agents 1000 --iterations 1,5,10,20 --seed 0xDEADBEEF --output-dir regression_test_results/reference
08:45:32 [INFO] Initializing SlimeSimulatorReference:
08:45:32 [INFO]   Resolution: 160x120
08:45:32 [INFO]   Agents: 1000
08:45:32 [INFO]   Seed: 0xDEADBEEF
08:45:32 [INFO]
08:45:32 [INFO] Running simulation for 20 iterations...
08:45:32 [INFO] Capturing at iterations: [1, 5, 10, 20]
08:45:33 [INFO]   Iter   1:   1024 pixels written (mean=15.3, max=35)
08:45:33 [INFO]            -> regression_test_results/reference/trail_iter_001.bin
08:45:34 [INFO]   Iter   5:   4892 pixels written (mean=12.8, max=48)
08:45:34 [INFO]            -> regression_test_results/reference/trail_iter_005.bin
08:45:35 [INFO]   Iter  10:   9567 pixels written (mean=11.2, max=62)
08:45:35 [INFO]            -> regression_test_results/reference/trail_iter_010.bin
08:45:36 [INFO]   Iter  20:  14123 pixels written (mean=10.5, max=78)
08:45:36 [INFO]            -> regression_test_results/reference/trail_iter_020.bin
08:45:36 [INFO]
08:45:36 [INFO] Generated 4 reference trail maps
08:45:36 [INFO] Output directory: /home/user/SlimeSimulator/rtl/regression_test_results/reference
08:45:36 [SUCCESS] Generating Python reference completed successfully
08:45:36 [SUCCESS] Reference generation completed successfully
08:45:36 [INFO] Total time: 3.8 seconds
08:45:36 [INFO] ================================================================================
```

### Output Files
```
regression_test_results/
└── reference/
    ├── trail_iter_001.bin    (19,200 bytes)
    ├── trail_iter_005.bin    (19,200 bytes)
    ├── trail_iter_010.bin    (19,200 bytes)
    ├── trail_iter_020.bin    (19,200 bytes)
    └── final_state.txt       (detailed agent state)
```

---

## Example 2: Full Workflow (with FPGA) - Hypothetical

### Command
```bash
python regression_test.py --bitstream build/slime_top.bit --iterations 1,5,10,20
```

### Console Output
```
14:23:15 [INFO] ================================================================================
14:23:15 [INFO] Starting RTL Regression Test
14:23:15 [INFO] ================================================================================
14:23:15 [INFO] Configuration: 160x120, 1000 agents, iterations [1, 5, 10, 20]

14:23:15 [STEP] ================================================================================
14:23:15 [STEP] STEP 1: Generate Python Reference Trail Maps
14:23:15 [STEP] ================================================================================
14:23:15 [INFO] Generating Python reference...
14:23:19 [SUCCESS] Generating Python reference completed successfully

14:23:19 [STEP] ================================================================================
14:23:19 [STEP] STEP 2: Program FPGA with Bitstream
14:23:19 [STEP] ================================================================================
14:23:19 [INFO] Bitstream: /home/user/SlimeSimulator/rtl/build/slime_top.bit
14:23:19 [INFO] Programming FPGA...
14:23:20 [FPGA] Connecting to FPGA via JTAG...
14:23:21 [FPGA] Successfully connected to FPGA
14:23:21 [FPGA] Device: xc7a35t_0
14:23:21 [FPGA] Programming bitstream: slime_top.bit
14:23:28 [FPGA] Bitstream programmed successfully
14:23:28 [FPGA] Initializing simulation with seed 0xDEADBEEF
14:23:28 [FPGA] Capturing trail maps at iterations: [1, 5, 10, 20]
14:23:28 [FPGA] Waiting for frame_start signal...
14:23:29 [FPGA]   Iter   1:   1018 pixels written (mean=15.1, max=33)
14:23:29 [FPGA]            -> regression_test_results/rtl_capture/trail_iter_001.bin
14:23:30 [FPGA]   Iter   5:   4885 pixels written (mean=12.6, max=47)
14:23:30 [FPGA]            -> regression_test_results/rtl_capture/trail_iter_005.bin
14:23:31 [FPGA]   Iter  10:   9542 pixels written (mean=11.0, max=60)
14:23:31 [FPGA]            -> regression_test_results/rtl_capture/trail_iter_010.bin
14:23:32 [FPGA]   Iter  20:  14089 pixels written (mean=10.3, max=75)
14:23:32 [FPGA]            -> regression_test_results/rtl_capture/trail_iter_020.bin
14:23:32 [FPGA] Captured 4 trail maps from RTL
14:23:32 [SUCCESS] Programming FPGA completed successfully

14:23:32 [STEP] ================================================================================
14:23:32 [STEP] STEP 3: Compare Reference vs RTL
14:23:32 [STEP] ================================================================================
14:23:32 [INFO] Comparing trail maps...

Comparing trail maps...
  Reference: regression_test_results/reference
  RTL:       regression_test_results/rtl_capture
  Iterations: [1, 5, 10, 20]

==========================================================================================
Trail Map Comparison Results
==========================================================================================
Iter |  Written |   Match | MaxDiff | MeanDiff |     RMS | Status
------------------------------------------------------------------------------------------
   1 |     1024 |  99.97% |     3.0 |    0.012 |   0.234 |   PASS
   5 |     4892 |  99.94% |     5.0 |    0.023 |   0.456 |   PASS
  10 |     9567 |  99.89% |     8.0 |    0.034 |   0.678 |   PASS
  20 |    14123 |  99.82% |    12.0 |    0.045 |   0.891 |   PASS
==========================================================================================

Comparison results saved to: /home/user/SlimeSimulator/rtl/regression_test_results/comparison_report.csv
Detailed analysis saved to: /home/user/SlimeSimulator/rtl/regression_test_results/detailed_analysis.txt

==========================================================================================
OVERALL STATUS: PASS
All iterations met 95.0% match threshold
==========================================================================================

14:23:33 [SUCCESS] Comparison completed successfully
14:23:33 [INFO] Test summary saved to: regression_test_results/test_summary.txt
14:23:33 [INFO] ================================================================================
14:23:33 [SUCCESS] REGRESSION TEST PASSED
14:23:33 [SUCCESS] All iterations met 95.0% match threshold
14:23:33 [SUCCESS] Total time: 17.8 seconds
14:23:33 [INFO] ================================================================================
```

---

## Example 3: Comparison Report (CSV)

**File**: `regression_test_results/comparison_report.csv`

```csv
iteration,total_pixels,nonzero_ref,nonzero_rtl,matching_pixels,match_percentage,max_diff,mean_diff,rms_diff,nonzero_match,status
1,19200,1024,1018,19194,99.96875,3.0,0.012,0.234,1016,PASS
5,19200,4892,4885,19182,99.90625,5.0,0.023,0.456,4878,PASS
10,19200,9567,9542,19172,99.8541666667,8.0,0.034,0.678,9530,PASS
20,19200,14123,14089,19166,99.8229166667,12.0,0.045,0.891,14075,PASS
```

### CSV Loaded in Spreadsheet

| iteration | total_pixels | nonzero_ref | nonzero_rtl | matching_pixels | match_percentage | max_diff | mean_diff | rms_diff | nonzero_match | status |
|-----------|-------------|-------------|-------------|----------------|-----------------|----------|-----------|----------|---------------|--------|
| 1 | 19200 | 1024 | 1018 | 19194 | 99.97% | 3.0 | 0.012 | 0.234 | 1016 | PASS |
| 5 | 19200 | 4892 | 4885 | 19182 | 99.91% | 5.0 | 0.023 | 0.456 | 4878 | PASS |
| 10 | 19200 | 9567 | 9542 | 19172 | 99.85% | 8.0 | 0.034 | 0.678 | 9530 | PASS |
| 20 | 19200 | 14123 | 14089 | 19166 | 99.82% | 12.0 | 0.045 | 0.891 | 14075 | PASS |

---

## Example 4: Detailed Analysis (Text)

**File**: `regression_test_results/detailed_analysis.txt`

```
================================================================================
Detailed Trail Map Comparison Analysis
================================================================================

Reference Directory: /home/user/SlimeSimulator/rtl/regression_test_results/reference
RTL Directory:       /home/user/SlimeSimulator/rtl/regression_test_results/rtl_capture
Resolution:          160x120
Total Pixels:        19200

Summary Statistics:
--------------------------------------------------------------------------------
  Iterations tested:     4
  Iteration range:       1 - 20
  Match % range:         99.82% - 99.97%
  Average match %:       99.89%
  Max diff range:        3.0 - 12.0
  Mean diff range:       0.012 - 0.045

  Tests passed:          4/4
  Tests failed:          0/4

Per-Iteration Analysis:
================================================================================

Iteration   1  [PASS]
--------------------------------------------------------------------------------
  Reference pixels written:     1024
  RTL pixels written:           1018
  Exactly matching pixels:     19194  (99.97%)
  Matching non-zero pixels:     1016
  Maximum difference:            3.0
  Mean difference:             0.012
  RMS difference:              0.234

Iteration   5  [PASS]
--------------------------------------------------------------------------------
  Reference pixels written:     4892
  RTL pixels written:           4885
  Exactly matching pixels:     19182  (99.91%)
  Matching non-zero pixels:     4878
  Maximum difference:            5.0
  Mean difference:             0.023
  RMS difference:              0.456

Iteration  10  [PASS]
--------------------------------------------------------------------------------
  Reference pixels written:     9567
  RTL pixels written:           9542
  Exactly matching pixels:     19172  (99.85%)
  Matching non-zero pixels:     9530
  Maximum difference:            8.0
  Mean difference:             0.034
  RMS difference:              0.678

Iteration  20  [PASS]
--------------------------------------------------------------------------------
  Reference pixels written:    14123
  RTL pixels written:          14089
  Exactly matching pixels:     19166  (99.82%)
  Matching non-zero pixels:    14075
  Maximum difference:           12.0
  Mean difference:             0.045
  RMS difference:              0.891

================================================================================
Trend Analysis:
================================================================================

  Match percentage trend:  stable
  GOOD: Divergence remains stable across iterations.
```

---

## Example 5: Test Summary

**File**: `regression_test_results/test_summary.txt`

```
================================================================================
Slime Simulator RTL Regression Test Summary
================================================================================

Test Date:           2025-11-24 14:23:33
Test Duration:       17.8 seconds
Overall Status:      PASS

Test Configuration:
--------------------------------------------------------------------------------
  Resolution:        160x120
  Number of Agents:  1000
  LFSR Seed:         0xDEADBEEF
  Iterations:        [1, 5, 10, 20]
  Pass Threshold:    95.0%

Output Files:
--------------------------------------------------------------------------------
  Reference Dir:     /home/user/SlimeSimulator/rtl/regression_test_results/reference
  RTL Capture Dir:   /home/user/SlimeSimulator/rtl/regression_test_results/rtl_capture
  Comparison CSV:    /home/user/SlimeSimulator/rtl/regression_test_results/comparison_report.csv
  Detailed Analysis: /home/user/SlimeSimulator/rtl/regression_test_results/detailed_analysis.txt

================================================================================
```

---

## Example 6: Failed Test (Threshold Not Met)

### Console Output
```
14:45:32 [INFO] Starting RTL Regression Test
...
[comparison output]

==========================================================================================
Trail Map Comparison Results
==========================================================================================
Iter |  Written |   Match | MaxDiff | MeanDiff |     RMS | Status
------------------------------------------------------------------------------------------
   1 |     1024 |  99.97% |     3.0 |    0.012 |   0.234 |   PASS
   5 |     4892 |  94.20% |    45.0 |    1.234 |   5.678 |   FAIL  ← Below 95% threshold
  10 |     9567 |  89.50% |    78.0 |    2.456 |  12.345 |   FAIL
  20 |    14123 |  82.30% |   120.0 |    4.567 |  23.456 |   FAIL
==========================================================================================

==========================================================================================
OVERALL STATUS: FAIL
Some iterations did not meet 95.0% match threshold
==========================================================================================

14:45:36 [ERROR] REGRESSION TEST FAILED
14:45:36 [ERROR] Some iterations did not meet 95.0% threshold
14:45:36 [ERROR] Total time: 18.2 seconds
14:45:36 [INFO] ================================================================================
```

**Exit Code**: 1 (failure)

---

## Example 7: Visualization Output

### Command
```bash
python compare_trails.py \
    --reference regression_test_results/reference \
    --rtl regression_test_results/rtl_capture \
    --iterations 1,5,10,20 \
    --visualize
```

### Console Output
```
Comparing trail maps...
...
Generating visualizations...
  regression_test_results/visualizations/diff_iter_001.png
  regression_test_results/visualizations/diff_iter_005.png
  regression_test_results/visualizations/diff_iter_010.png
  regression_test_results/visualizations/diff_iter_020.png
```

### Visualization Color Key
- 🟢 **Green**: Pixels match exactly between reference and RTL
- 🔴 **Red**: Pixels only in reference (RTL is missing trail)
- 🔵 **Blue**: Pixels only in RTL (RTL has extra trail)
- 🟡 **Yellow**: Both have trail but different intensities

### Example Diff Image

```
[Image would show trail patterns with color-coded differences]

For a well-matched simulation:
- Mostly green (matching pixels)
- Scattered red/blue dots (minor differences in agent paths)
- Few yellow areas (intensity differences due to fixed-point rounding)
```

---

## Example 8: Extended Test Suite

### Command
```bash
python regression_test.py --reference-only \
    --iterations 1,2,5,10,15,20,30,50,100 \
    --agents 5000
```

### Performance
- **Time**: ~8 minutes for 100 iterations with 5000 agents
- **Memory**: ~500 MB peak
- **Output**: 9 trail map files (each 19,200 bytes)

### Result Summary
```
==========================================================================================
Iter |  Written |   Match | MaxDiff | MeanDiff |     RMS | Status
------------------------------------------------------------------------------------------
   1 |     5024 |  99.98% |     2.0 |    0.008 |   0.156 |   PASS
   2 |     9856 |  99.96% |     3.0 |    0.012 |   0.234 |   PASS
   5 |    18234 |  99.92% |     5.0 |    0.023 |   0.456 |   PASS
  10 |    19120 |  99.88% |     8.0 |    0.034 |   0.678 |   PASS
  15 |    19180 |  99.85% |    10.0 |    0.041 |   0.789 |   PASS
  20 |    19195 |  99.82% |    12.0 |    0.045 |   0.891 |   PASS
  30 |    19199 |  99.78% |    15.0 |    0.052 |   1.023 |   PASS
  50 |    19200 |  99.72% |    18.0 |    0.063 |   1.234 |   PASS
 100 |    19200 |  99.65% |    22.0 |    0.078 |   1.456 |   PASS
==========================================================================================
OVERALL STATUS: PASS
```

---

## Example 9: Custom Resolution Test

### Command
```bash
python regression_test.py --reference-only \
    --width 320 --height 240 \
    --agents 2000 \
    --iterations 1,10,20
```

### Output
```
Initializing SlimeSimulatorReference:
  Resolution: 320x240
  Agents: 2000
  Seed: 0xDEADBEEF

Running simulation for 20 iterations...
Capturing at iterations: [1, 10, 20]
  Iter   1:   2048 pixels written (mean=15.3, max=35)
           -> regression_test_results/reference/trail_iter_001.bin
  Iter  10:  19234 pixels written (mean=11.2, max=62)
           -> regression_test_results/reference/trail_iter_010.bin
  Iter  20:  28467 pixels written (mean=10.5, max=78)
           -> regression_test_results/reference/trail_iter_020.bin

Generated 3 reference trail maps
```

**File sizes**: 320×240 = 76,800 bytes per trail map

---

## Summary

The regression testing framework provides:
- ✅ Clear, timestamped console output
- ✅ Multiple output formats (CSV, text, images)
- ✅ Pass/fail determination with configurable thresholds
- ✅ Detailed per-iteration analysis
- ✅ Trend analysis across iterations
- ✅ Error handling and informative messages
- ✅ Support for various test configurations

All output is designed to be both human-readable (console, text files) and machine-parseable (CSV) for integration with CI/CD systems.
