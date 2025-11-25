# RTL Regression Testing Framework - Visual Guide

## Complete System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SLIME SIMULATOR RTL                                  │
│                    REGRESSION TEST FRAMEWORK                            │
│                         Version 1.0.0                                   │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  $ python regression_test.py --reference-only                          │
│  $ python regression_test.py --bitstream build/slime_top.bit           │
│  $ python compare_trails.py --reference ref/ --rtl rtl/ --visualize   │
│                                                                         │
└────────────────────────┬────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    MASTER ORCHESTRATOR                                  │
│                    regression_test.py (534 lines)                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  • Parse command-line arguments                                        │
│  • Coordinate workflow execution                                       │
│  • Handle errors gracefully                                            │
│  • Log progress with timestamps                                        │
│  • Generate test summary                                               │
│                                                                         │
└───┬─────────────────────┬─────────────────────┬──────────────────────────┘
    │                     │                     │
    ▼                     ▼                     ▼
┌───────────────┐   ┌────────────────┐   ┌─────────────────┐
│  GENERATE     │   │  FPGA          │   │  COMPARE        │
│  REFERENCE    │   │  CONTROLLER    │   │  TRAILS         │
└───────────────┘   └────────────────┘   └─────────────────┘
```

## Component Details

### Component 1: Python Reference Generator

```
┌─────────────────────────────────────────────────────────────────┐
│  generate_python_ref.py (187 lines)                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Input:                                                         │
│  ├─ width, height (resolution)                                 │
│  ├─ num_agents                                                 │
│  ├─ iterations list [1, 5, 10, 20]                            │
│  ├─ lfsr_seed (0xDEADBEEF)                                     │
│  └─ output_dir                                                 │
│                                                                 │
│  Processing:                                                    │
│  ├─ Initialize SlimeSimulatorReference                         │
│  ├─ Place agents at center                                     │
│  ├─ Run simulation step by step                                │
│  └─ Capture trail maps at specified iterations                 │
│                                                                 │
│  Output:                                                        │
│  ├─ trail_iter_001.bin  (19,200 bytes for 160×120)            │
│  ├─ trail_iter_005.bin                                         │
│  ├─ trail_iter_010.bin                                         │
│  ├─ trail_iter_020.bin                                         │
│  └─ final_state.txt (agent positions, LFSR state)             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Component 2: FPGA Controller

```
┌─────────────────────────────────────────────────────────────────┐
│  fpga_controller.py (452 lines)                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Connection:                                                    │
│  ├─ Connect to FPGA via JTAG                                   │
│  ├─ Open Vivado hardware manager                               │
│  └─ Verify target device                                       │
│                                                                 │
│  Programming:                                                   │
│  ├─ Load bitstream file                                        │
│  ├─ Program FPGA                                               │
│  └─ Verify success                                             │
│                                                                 │
│  Initialization:                                                │
│  ├─ Set LFSR seed via control interface                        │
│  ├─ Trigger simulation start                                   │
│  └─ Wait for ready signal                                      │
│                                                                 │
│  Iteration Loop:                                                │
│  ├─ Wait for frame_start pulse                                 │
│  ├─ Read trail memory via JTAG2AXI                             │
│  ├─ Save to binary file                                        │
│  └─ Repeat for all iterations                                  │
│                                                                 │
│  Status: ⚠️  Framework ready - requires RTL IP integration     │
│          • JTAG2AXI IP for memory access                       │
│          • VIO IP for signal monitoring                        │
│          • Control interface for seed/start                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Component 3: Trail Map Comparator

```
┌─────────────────────────────────────────────────────────────────┐
│  compare_trails.py (536 lines)                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Input:                                                         │
│  ├─ reference_dir/trail_iter_XXX.bin                           │
│  ├─ rtl_dir/trail_iter_XXX.bin                                 │
│  ├─ iterations list                                            │
│  └─ threshold (default 95%)                                    │
│                                                                 │
│  Processing:                                                    │
│  ├─ Load binary trail maps                                     │
│  ├─ Pixel-by-pixel comparison                                  │
│  ├─ Compute statistics:                                        │
│  │  ├─ Match percentage                                        │
│  │  ├─ Max difference                                          │
│  │  ├─ Mean difference                                         │
│  │  ├─ RMS difference                                          │
│  │  └─ Nonzero pixel analysis                                  │
│  ├─ Determine pass/fail                                        │
│  └─ Generate visualizations (optional)                         │
│                                                                 │
│  Output:                                                        │
│  ├─ comparison_report.csv                                      │
│  │  iteration,total_pixels,matching_pixels,match_%,max_diff...│
│  ├─ detailed_analysis.txt                                      │
│  │  Per-iteration breakdown                                    │
│  │  Trend analysis                                             │
│  │  Summary statistics                                         │
│  └─ visualizations/diff_iter_XXX.png (if --visualize)         │
│     🟢 Green  = Matching pixels                                │
│     🔴 Red    = Only in reference                              │
│     🔵 Blue   = Only in RTL                                    │
│     🟡 Yellow = Different values                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
                    ┌──────────────────┐
                    │  User Command    │
                    └────────┬─────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │   regression_test.py         │
              │   Parse arguments            │
              │   Setup directories          │
              └──────────────┬───────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
    ┌─────────┐         ┌─────────┐        ┌─────────┐
    │ STEP 1  │         │ STEP 2  │        │ STEP 3  │
    │ Python  │         │ FPGA    │        │ Compare │
    │ Ref Gen │         │ Capture │        │ Results │
    └────┬────┘         └────┬────┘        └────┬────┘
         │                   │                   │
         ▼                   ▼                   ▼
    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
    │ Reference   │    │ RTL Capture │    │ Analysis    │
    │ Trail Maps  │    │ Trail Maps  │    │ Reports     │
    │             │    │             │    │             │
    │ .bin files  │    │ .bin files  │    │ .csv        │
    │ .txt state  │    │             │    │ .txt        │
    │             │    │             │    │ .png (viz)  │
    └─────────────┘    └─────────────┘    └─────────────┘
         │                   │                   │
         └───────────────────┴───────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Test Summary   │
                    │  PASS / FAIL    │
                    └─────────────────┘
```

## File Format Details

### Binary Trail Map Format

```
┌─────────────────────────────────────────────────────────┐
│  trail_iter_001.bin                                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Format: Raw binary, uint8                             │
│  Layout: Row-major (y, x indexing)                     │
│  Size:   width × height bytes                          │
│                                                         │
│  Example for 160×120:                                  │
│  ┌───────────────────────────────────────┐            │
│  │ Byte    0: Pixel (0,0)                │            │
│  │ Byte    1: Pixel (0,1)                │            │
│  │ ...                                    │            │
│  │ Byte  159: Pixel (0,159)              │            │
│  │ Byte  160: Pixel (1,0)                │            │
│  │ ...                                    │            │
│  │ Byte 19199: Pixel (119,159)           │            │
│  └───────────────────────────────────────┘            │
│                                                         │
│  Total: 19,200 bytes for 160×120                       │
│         76,800 bytes for 320×240                       │
│        307,200 bytes for 640×480                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### CSV Report Format

```
┌─────────────────────────────────────────────────────────────────┐
│  comparison_report.csv                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  iteration | total_pixels | matching_pixels | match_% | ...    │
│  ──────────┼──────────────┼─────────────────┼─────────┼────    │
│      1     |    19200     |     19180       |  99.90  | ...    │
│      5     |    19200     |     19050       |  99.22  | ...    │
│     10     |    19200     |     18950       |  98.70  | ...    │
│     20     |    19200     |     18850       |  98.18  | ...    │
│                                                                 │
│  Additional columns:                                            │
│  • nonzero_ref       - Pixels written in reference             │
│  • nonzero_rtl       - Pixels written in RTL                   │
│  • max_diff          - Maximum absolute difference             │
│  • mean_diff         - Mean absolute difference                │
│  • rms_diff          - Root mean square difference             │
│  • nonzero_match     - Matching non-zero pixels                │
│  • status            - PASS or FAIL                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Workflow Examples

### Workflow 1: Reference-Only (Current)

```
┌────────────────────┐
│  User             │
└─────────┬──────────┘
          │ python regression_test.py --reference-only
          ▼
┌──────────────────────────────────┐
│  regression_test.py              │
│  • Parse arguments               │
│  • Create output directories     │
└─────────┬────────────────────────┘
          │
          ▼
┌──────────────────────────────────┐
│  generate_python_ref.py          │
│  • Init simulator (160×120)      │
│  • Place 1000 agents at center   │
│  • Run 20 iterations             │
│  • Capture at [1,5,10,20]        │
└─────────┬────────────────────────┘
          │
          ▼
┌──────────────────────────────────┐
│  Output Files                    │
│  • trail_iter_001.bin            │
│  • trail_iter_005.bin            │
│  • trail_iter_010.bin            │
│  • trail_iter_020.bin            │
│  • final_state.txt               │
│  • test_summary.txt              │
└──────────────────────────────────┘
          │
          ▼
┌──────────────────────┐
│  SUCCESS             │
│  Time: ~3 seconds    │
└──────────────────────┘
```

### Workflow 2: Full Testing (Future with FPGA)

```
┌────────────────────┐
│  User             │
└─────────┬──────────┘
          │ python regression_test.py --bitstream build/slime_top.bit
          ▼
┌──────────────────────────────────────────┐
│  STEP 1: Generate Reference              │
│  generate_python_ref.py                  │
│  → reference/trail_*.bin                 │
└─────────┬────────────────────────────────┘
          │
          ▼
┌──────────────────────────────────────────┐
│  STEP 2: Program and Capture FPGA        │
│  fpga_controller.py                      │
│  ├─ Connect via JTAG                     │
│  ├─ Program bitstream                    │
│  ├─ Initialize (seed 0xDEADBEEF)         │
│  ├─ Wait for frame_start × 20            │
│  ├─ Read memory via JTAG2AXI             │
│  └─ Save rtl_capture/trail_*.bin         │
└─────────┬────────────────────────────────┘
          │
          ▼
┌──────────────────────────────────────────┐
│  STEP 3: Compare Results                 │
│  compare_trails.py                       │
│  ├─ Load both sets of trail maps         │
│  ├─ Pixel-by-pixel comparison            │
│  ├─ Compute statistics                   │
│  ├─ Generate visualizations              │
│  └─ Create reports:                      │
│     ├─ comparison_report.csv             │
│     ├─ detailed_analysis.txt             │
│     └─ visualizations/*.png              │
└─────────┬────────────────────────────────┘
          │
          ▼
┌──────────────────────┐
│  Test Summary        │
│  • PASS or FAIL      │
│  • Match %           │
│  • Time: ~20s        │
└──────────────────────┘
```

## Visual Comparison Example

```
Iteration 1: 99.97% Match

Reference:              RTL:                   Diff:
┌─────────────┐        ┌─────────────┐        ┌─────────────┐
│             │        │             │        │🟢🟢🟢🟢🟢🟢🟢│
│     ●●●     │        │     ●●●     │        │🟢●●●🟢🟢🟢│
│    ● ● ●    │        │    ● ● ●    │        │🟢● ● ●🟢🟢│
│   ●  ●  ●   │        │   ●  ●  ●   │        │🟢●  ●  ●🟢│
│    ● ● ●    │        │    ● ● ●    │        │🟢● ● ●🟢🟢│
│     ●●●     │        │     ●●●     │        │🟢●●●🟢🔴🟢│  ← Small diff
│             │        │             │        │🟢🟢🟢🟢🟢🟢🟢│
└─────────────┘        └─────────────┘        └─────────────┘

Stats:
  Total pixels:    19,200
  Matching:        19,194 (99.97%)
  Max diff:            3
  Mean diff:       0.012
  Status:           PASS ✓
```

## Documentation Navigation Map

```
                    ┌─────────────────────┐
                    │ REGRESSION_TEST_    │
                    │     INDEX.md        │
                    │  (Start Here!)      │
                    └──────────┬──────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
┌────────────────┐   ┌──────────────────┐   ┌──────────────┐
│ QUICKSTART.md  │   │    README.md     │   │ EXAMPLE_     │
│                │   │                  │   │ OUTPUT.md    │
│ • Setup        │   │ • Architecture   │   │              │
│ • First run    │   │ • Components     │   │ • 9 examples │
│ • Commands     │   │ • File formats   │   │ • Console    │
│ • Troubleshoot │   │ • Workflows      │   │ • CSV/Text   │
│                │   │ • CI/CD          │   │ • Images     │
└────────────────┘   └──────────────────┘   └──────────────┘
          │                    │                    │
          └────────────────────┼────────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ IMPLEMENTATION.md    │
                    │                      │
                    │ • Summary            │
                    │ • Deliverables       │
                    │ • Status             │
                    │ • Next steps         │
                    └──────────────────────┘
```

## Command Reference Card

```
╔════════════════════════════════════════════════════════════════╗
║           REGRESSION TEST QUICK REFERENCE                      ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  Basic Commands:                                               ║
║  ───────────────                                               ║
║                                                                ║
║  # Reference only (no FPGA)                                   ║
║  python regression_test.py --reference-only                   ║
║                                                                ║
║  # Full test with FPGA                                        ║
║  python regression_test.py --bitstream build/slime.bit        ║
║                                                                ║
║  # Compare existing trails                                    ║
║  python compare_trails.py --reference ref/ --rtl rtl/         ║
║                                                                ║
║  Common Options:                                               ║
║  ───────────────                                               ║
║                                                                ║
║  --iterations 1,5,10,20      Test points                      ║
║  --threshold 99.0            Pass criteria (%)                ║
║  --width 160                 Resolution width                 ║
║  --height 120                Resolution height                ║
║  --agents 1000               Number of agents                 ║
║  --seed 0xDEADBEEF           LFSR seed                        ║
║  --visualize                 Generate diff images             ║
║  --quiet                     Suppress output                  ║
║  --help                      Show full help                   ║
║                                                                ║
║  Example Workflows:                                            ║
║  ──────────────────                                            ║
║                                                                ║
║  # Quick dev test                                             ║
║  python regression_test.py --reference-only --iterations 1,5  ║
║                                                                ║
║  # Full validation                                            ║
║  python regression_test.py --bitstream build/slime.bit \     ║
║      --iterations 1,5,10,20,50 --threshold 99.0 --visualize  ║
║                                                                ║
║  # Custom resolution                                          ║
║  python regression_test.py --reference-only \                ║
║      --width 320 --height 240 --agents 2000                  ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
```

## Status Legend

```
✅  Fully implemented and tested
⚠️  Framework ready, requires RTL integration
🔲  Planned future enhancement
❌  Not implemented
```

## File Size Reference

```
Resolution    Bytes/File    4 Files    10 Files
──────────    ──────────    ───────    ────────
160×120        19,200 B      77 KB      192 KB
320×240        76,800 B     307 KB      768 KB
640×480       307,200 B    1,229 KB    3,072 KB
1280×720      921,600 B    3,686 KB    9,216 KB
```

---

**This visual guide provides a comprehensive overview of the RTL Regression Testing Framework.**

**Start with**: REGRESSION_TEST_INDEX.md for full navigation

**First command**: `python regression_test.py --reference-only`

**Framework Version**: 1.0.0
**Status**: Production Ready (Reference Mode)
**Date**: November 24, 2025
