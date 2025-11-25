# Build and Test Guide for Slime Simulator

Complete guide for building the Vivado project and running comprehensive tests.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Project Generation](#project-generation)
4. [Building the FPGA Bitstream](#building-the-fpga-bitstream)
5. [Running Tests](#running-tests)
6. [Test Phases Explained](#test-phases-explained)
7. [Interpreting Results](#interpreting-results)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Hardware
- **Basys3 FPGA board** (optional, for hardware testing)
- USB cable for FPGA programming

### Software
- **Vivado** 2019.1 or later
- **Python 3.8+** with packages:
  - numpy
  - matplotlib
- **cocotb** (optional, for RTL simulation)
- **Icarus Verilog or Verilator** (optional, for RTL simulation)

### Installation

```bash
# Install Python dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install numpy matplotlib

# Optional: For RTL simulation
pip install cocotb cocotb-test
```

---

## Quick Start

### 1. Generate Vivado Project

```bash
cd rtl
vivado -mode batch -source generate_xpr.tcl
```

**Output:**
- `vivado_project/slime_simulator.xpr` - Vivado project file
- `generate_xpr_report.txt` - Project generation report

**Time:** ~10 seconds

### 2. Build FPGA Bitstream

```bash
vivado -mode batch -source build.tcl
```

**Output:**
- `vivado_project/slime_simulator.runs/impl_1/slime_top.bit` - FPGA bitstream
- `build_report.txt` - Build summary with timing and utilization

**Time:** 5-15 minutes (depending on machine)

### 3. Run Comprehensive Tests

```bash
# Activate Python environment
source ../.venv/bin/activate

# Run Python reference only (no hardware needed)
python3 comprehensive_test.py --skip-rtl-sim --skip-fpga

# Run with FPGA hardware (if available)
python3 comprehensive_test.py --skip-rtl-sim

# Full test suite (Python + RTL + FPGA)
python3 comprehensive_test.py
```

**Output:**
- `test_results_comprehensive/` - All test data and reports
- `COMPREHENSIVE_TEST_REPORT.md` - Executive summary

**Time:**
- Python only: ~2 minutes
- With FPGA: ~10 minutes
- Full suite: ~15 minutes

---

## Project Generation

### generate_xpr.tcl

This script creates a complete Vivado project from scratch.

**What it does:**
1. Deletes old project if exists
2. Creates new project for Basys3 (xc7a35tcpg236-1)
3. Adds all RTL sources in dependency order
4. Adds memory initialization files (.hex)
5. Adds constraints file
6. Configures synthesis and implementation strategies
7. Enables incremental compile
8. Generates detailed report

**Running:**
```bash
vivado -mode batch -source generate_xpr.tcl
```

**Success criteria:**
- ✓ Exit code 0
- ✓ All source files found
- ✓ Project file created
- ✓ No missing files in report

**Troubleshooting:**
```bash
# Check report for missing files
cat generate_xpr_report.txt

# If files are missing, ensure you're in rtl/ directory
pwd  # Should show: .../SlimeSimulator/rtl

# Verify source files exist
ls src/*.sv
ls src/*.hex
ls constraints/*.xdc
```

---

## Building the FPGA Bitstream

### build.tcl

Complete synthesis → implementation → bitstream generation.

**What it does:**
1. **Prerequisites check:** Verifies project and files exist
2. **Synthesis:** Optimizes RTL to netlist (4 parallel jobs)
3. **Implementation:** Place & route (4 parallel jobs)
4. **Bitstream generation:** Creates .bit file with compression
5. **Report generation:** Timing, utilization, power

**Running:**
```bash
vivado -mode batch -source build.tcl
```

**Build stages:**

| Stage | Duration | Output |
|-------|----------|--------|
| Synthesis | 2-5 min | netlist, utilization report |
| Implementation | 3-8 min | placed & routed design |
| Bitstream | 1-2 min | .bit file |

**Success criteria:**
- ✓ Synthesis completes (100% progress)
- ✓ Implementation completes (100% progress)
- ✓ Bitstream file exists
- ✓ Timing WNS ≥ 0 ns (setup timing met)
- ⚠ WNS < 0 ns means timing violations (design may not work reliably)

**Output files:**
```
vivado_project/
└── slime_simulator.runs/
    ├── synth_1/
    │   ├── slime_top_utilization_synth.txt
    │   └── slime_top_timing_summary_synth.txt
    └── impl_1/
        ├── slime_top.bit                    ← Bitstream
        ├── slime_top_utilization_placed.txt
        ├── slime_top_timing_summary_routed.txt
        └── slime_top_power_routed.txt
```

**Troubleshooting:**

```bash
# Check build log for errors
cat vivado_project/slime_simulator.runs/synth_1/runme.log
cat vivado_project/slime_simulator.runs/impl_1/runme.log

# Check timing report
grep "WNS" build_report.txt

# If timing fails, consider:
# 1. Reducing clock frequency (edit constraints/basys3.xdc)
# 2. Adding pipeline stages
# 3. Using different implementation strategy
```

---

## Running Tests

### Test Architecture

```
comprehensive_test.py (master orchestrator)
    │
    ├─► Phase 1: Python Reference
    │   └── sim/regression_test.py --reference-only
    │
    ├─► Phase 2: RTL Simulation (optional)
    │   └── cocotb testbench (if available)
    │
    ├─► Phase 3: FPGA Hardware (optional)
    │   └── Program FPGA → capture via JTAG
    │
    ├─► Phase 4: Multi-way Comparison
    │   └── Compare Python vs RTL vs FPGA
    │
    ├─► Phase 5: Statistical Analysis
    │   └── Generate metrics and histograms
    │
    └─► Phase 6: Report Generation
        └── Markdown + JSON reports
```

### Basic Usage

**Python reference only (recommended for first test):**
```bash
source ../.venv/bin/activate
python3 comprehensive_test.py --skip-rtl-sim --skip-fpga
```

**Custom iteration points:**
```bash
python3 comprehensive_test.py \
  --iterations 1,10,50,100 \
  --output-dir my_test_results
```

**With FPGA hardware:**
```bash
# 1. Build bitstream first
vivado -mode batch -source build.tcl

# 2. Connect FPGA board

# 3. Run test with FPGA
python3 comprehensive_test.py --skip-rtl-sim
```

### Command-Line Options

```
--output-dir DIR          Output directory (default: test_results_comprehensive)
--iterations 1,5,10       Comma-separated iteration points
--skip-rtl-sim            Skip RTL simulation phase
--skip-fpga               Skip FPGA hardware testing
--fpga-threshold 85.0     Acceptance threshold for FPGA (%)
```

### Test Output Structure

```
test_results_comprehensive/
│
├── COMPREHENSIVE_TEST_REPORT.md     ← Main report
├── test_results.json                ← Machine-readable results
├── statistical_analysis.json        ← Detailed metrics
│
├── python_reference/
│   ├── python_summary.txt
│   ├── iter_001/
│   │   ├── python_trail.bin         ← Raw trail map data
│   │   ├── python_trail.png         ← Visualization
│   │   └── python_metadata.json     ← Run metadata
│   ├── iter_005/
│   ├── iter_010/
│   └── ...
│
├── rtl_simulation/                  (if RTL sim ran)
│   └── ...
│
└── fpga_capture/                    (if FPGA test ran)
    └── ...
```

---

## Test Phases Explained

### Phase 1: Python Reference Model

**Purpose:** Generate ground truth data

**What it does:**
- Runs Python implementation of slime simulator
- Generates trail maps at multiple iteration points (1, 5, 10, 20, 50, 100)
- Saves binary trail data + visualizations
- Records metadata (LFSR state, timing, statistics)

**Time:** ~5 seconds per 100 iterations

**Output example:**
```
Iterations 1:
  Time:           1.098s
  Trail min/max:  0/26
  Trail mean:     0.00
  Active pixels:  22
```

### Phase 2: RTL Simulation (Optional)

**Purpose:** Verify RTL matches Python bit-exactly

**What it does:**
- Runs cocotb testbenches on RTL modules
- Compares LFSR, fixed-point, trig LUT outputs
- Validates agent behavior

**Requirements:**
- cocotb installed
- Icarus Verilog or Verilator
- Makefile in sim/ directory

**Success criteria:** >95% match with Python

### Phase 3: FPGA Hardware (Optional)

**Purpose:** Validate on real hardware

**What it does:**
- Programs bitstream to FPGA
- Runs simulation on hardware
- Captures trail memory via JTAG
- Compares with Python reference

**Requirements:**
- Basys3 board connected
- Vivado with hw_server
- Bitstream built

**Success criteria:** >85% match with Python (allows for hardware rounding)

### Phase 4: Multi-way Comparison

**Purpose:** Compare all implementations

**Generates:**
- Comparison tables (Python vs RTL vs FPGA)
- Difference visualizations
- Match percentages

**Example output:**
```
                Python   RTL Sim   FPGA      Status
──────────────────────────────────────────────────
Iteration 1:    100.0%   99.8%     98.5%     ✓ PASS
Iteration 5:    100.0%   99.9%     98.2%     ✓ PASS
Iteration 10:   100.0%   99.7%     97.8%     ✓ PASS
```

### Phase 5: Statistical Analysis

**Purpose:** Deep dive into differences

**Analyzes:**
- Pixel-by-pixel differences
- Spatial distribution of errors
- Temporal error accumulation
- Histogram of difference magnitudes

**Helps identify:**
- Systematic vs random errors
- Memory corruption signs
- Fixed-point rounding issues
- LFSR divergence

### Phase 6: Report Generation

**Purpose:** Create comprehensive documentation

**Outputs:**
- **COMPREHENSIVE_TEST_REPORT.md:** Executive summary
- **test_results.json:** Machine-readable data
- **Visualizations:** PNG images of trails and diffs
- **Comparison tables:** CSV format

---

## Interpreting Results

### Success Indicators

**Python Reference:**
- ✓ All iterations complete without errors
- ✓ Trail maps generated (non-empty)
- ✓ Active pixels increase with iterations
- ✓ Visualizations show expected patterns

**RTL Simulation:**
- ✓ Match ≥95% with Python
- ✓ Bit-exact LFSR sequences
- ✓ Fixed-point within 1 LSB

**FPGA Hardware:**
- ✓ Match ≥85% with Python (threshold configurable)
- ✓ Match ≥90% within 5 intensity levels
- ✓ No systematic patterns in errors

### Warning Signs

**⚠ Timing violations in build:**
- WNS < 0 ns
- **Impact:** Design may be unreliable
- **Solution:** Reduce clock frequency or add pipeline stages

**⚠ Low match percentage (<85% for FPGA):**
- **Possible causes:**
  - Memory corruption
  - Clock domain crossing issues
  - Fixed-point overflow
  - LFSR seed mismatch
- **Debug:** Check difference visualizations for patterns

**⚠ Systematic error patterns:**
- Errors concentrated in specific regions
- **Likely cause:** Memory addressing bug
- **Debug:** Verify memory interface signals with ILA

**⚠ Exponential error growth:**
- Match % decreases rapidly with iterations
- **Likely cause:** LFSR divergence or state corruption
- **Debug:** Compare LFSR state at each iteration

### Match Percentage Guidelines

| Match % | Interpretation | Action |
|---------|----------------|--------|
| 100% | Perfect (bit-exact) | ✓ Excellent |
| 98-100% | Excellent (within 1-2 LSB) | ✓ Expected for RTL |
| 95-98% | Very good | ✓ Acceptable for hardware |
| 90-95% | Good (hardware tolerances) | ✓ Acceptable for FPGA |
| 85-90% | Acceptable | ⚠ Review differences |
| <85% | Investigate | ✗ Likely issues |

---

## Troubleshooting

### Build Issues

**Problem:** "Project file not found"
```bash
# Solution: Generate project first
vivado -mode batch -source generate_xpr.tcl
```

**Problem:** "Synthesis failed"
```bash
# Check syntax errors
cat vivado_project/slime_simulator.runs/synth_1/runme.log | grep ERROR

# Common issues:
# - Missing files: Check generate_xpr_report.txt
# - Syntax errors: Fix in RTL sources
# - Unsupported constructs: Check Vivado version
```

**Problem:** "Timing not met (WNS < 0)"
```bash
# Option 1: Reduce clock frequency
# Edit constraints/basys3.xdc:
# create_clock -period 10.00 → create_clock -period 12.00  (83 MHz → 100 MHz)

# Option 2: Try different implementation strategy
# Edit build.tcl:
# set_property strategy "Performance_Explore" [get_runs impl_1]

# Option 3: Add pipeline stages (requires RTL changes)
```

### Test Issues

**Problem:** "ModuleNotFoundError: No module named 'numpy'"
```bash
# Activate virtual environment
source ../.venv/bin/activate

# Install dependencies
pip install numpy matplotlib
```

**Problem:** "Python reference generation failed"
```bash
# Check for script errors
python3 sim/regression_test.py --reference-only --iterations 1

# Common issues:
# - Wrong directory: cd to rtl/
# - Missing python_reference.py: Check sim/ directory
```

**Problem:** "FPGA programming failed"
```bash
# Check hardware connection
lsusb | grep Xilinx

# Ensure hw_server is running
vivado -mode batch -source program_fpga.tcl

# Check cable driver
ls /dev/ttyUSB*
```

**Problem:** "Low match percentage"
```bash
# 1. Verify LFSR seed matches
grep "lfsr_seed" test_results_*/*/python_metadata.json

# 2. Check difference images
ls test_results_*/*/diff_*.png

# 3. Look for patterns in errors
# - Random: acceptable (rounding)
# - Systematic: bug (memory addressing)
# - Growing: state divergence
```

### Performance Issues

**Problem:** "Build takes too long"
```bash
# Reduce parallel jobs if system has limited resources
# Edit build.tcl:
# launch_runs synth_1 -jobs 2  # Instead of 4

# Enable incremental compile (already enabled)
# Only rebuilds changed modules
```

**Problem:** "Python test is slow"
```bash
# Reduce iteration points
python3 comprehensive_test.py --iterations 1,5,10

# Disable visualization
# Edit sim/regression_test.py:
# self.visualize = False
```

---

## Advanced Usage

### Custom Testbenches

Create your own test scenarios:

```python
from sim.python_reference import SlimeSimulatorReference

# Custom configuration
sim = SlimeSimulatorReference(
    width=320,        # Smaller for faster tests
    height=240,
    num_agents=500,
    lfsr_seed=0x12345678  # Custom seed
)

sim.init_agents_random()  # Random placement
sim.run(100)
trail = sim.get_trail_map()
```

### Batch Testing

Run multiple configurations:

```bash
for seed in 0xDEADBEEF 0xCAFEBABE 0x12345678; do
  python3 comprehensive_test.py \
    --output-dir "test_seed_${seed}" \
    --iterations 1,10,50
done
```

### Continuous Integration

Add to CI/CD pipeline:

```yaml
# .gitlab-ci.yml
test:
  script:
    - source .venv/bin/activate
    - cd rtl
    - python3 comprehensive_test.py --skip-fpga
    - test -f test_results_comprehensive/COMPREHENSIVE_TEST_REPORT.md
```

---

## File Reference

### Scripts

| File | Purpose | Usage |
|------|---------|-------|
| `generate_xpr.tcl` | Create Vivado project | `vivado -mode batch -source generate_xpr.tcl` |
| `build.tcl` | Build bitstream | `vivado -mode batch -source build.tcl` |
| `comprehensive_test.py` | Master test orchestrator | `python3 comprehensive_test.py` |
| `sim/regression_test.py` | Iteration-based testing | `python3 sim/regression_test.py` |
| `sim/python_reference.py` | Python reference model | Import as module |

### Reports

| File | Description |
|------|-------------|
| `generate_xpr_report.txt` | Project generation summary |
| `build_report.txt` | Build summary with timing |
| `COMPREHENSIVE_TEST_REPORT.md` | Test executive summary |
| `test_results.json` | Machine-readable results |
| `statistical_analysis.json` | Detailed metrics |

---

## Quick Command Reference

```bash
# Complete workflow from scratch
cd SlimeSimulator/rtl

# 1. Generate project
vivado -mode batch -source generate_xpr.tcl

# 2. Build bitstream
vivado -mode batch -source build.tcl

# 3. Run tests
source ../.venv/bin/activate
python3 comprehensive_test.py --skip-rtl-sim --skip-fpga

# 4. View results
cat test_results_comprehensive/COMPREHENSIVE_TEST_REPORT.md
ls test_results_comprehensive/python_reference/iter_*/python_trail.png
```

---

## Getting Help

### Check Logs

```bash
# Project generation
cat generate_xpr_report.txt

# Build
cat build_report.txt

# Vivado build logs
cat vivado_project/slime_simulator.runs/synth_1/runme.log
cat vivado_project/slime_simulator.runs/impl_1/runme.log

# Test results
cat test_results_comprehensive/COMPREHENSIVE_TEST_REPORT.md
```

### Verify Installation

```bash
# Check Vivado
vivado -version

# Check Python
python3 --version
python3 -c "import numpy, matplotlib; print('OK')"

# Check FPGA connection
lsusb | grep -i xilinx
```

### Common Issues

See [Troubleshooting](#troubleshooting) section above.

---

## Summary

This guide covers:
- ✓ Complete project generation and build flow
- ✓ Comprehensive testing at multiple levels
- ✓ Result interpretation and debugging
- ✓ Troubleshooting common issues

For questions or issues, check the logs and reports first, then refer to the troubleshooting section.

**Happy testing!**
