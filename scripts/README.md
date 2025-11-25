# SlimeSimulator Automation Scripts

This directory contains Python automation scripts for building, testing, programming, and validating the SlimeSimulator FPGA design.

## Overview

The automation suite consists of five main scripts:

1. **`run_full_validation.py`** - Master script that orchestrates the complete workflow
2. **`vivado_build.py`** - Builds FPGA designs using Vivado in batch mode
3. **`test_runner.py`** - Runs cocotb simulation tests
4. **`fpga_programmer.py`** - Programs the FPGA via JTAG
5. **`image_capture.py`** - Captures and compares trail map images

## Prerequisites

### Required Tools
- Python 3.6+
- Xilinx Vivado (for builds and programming)
- Icarus Verilog (for simulation)
- cocotb (for testing)
- GNU Make

### Python Packages
```bash
pip install numpy pillow cocotb
```

### Environment Setup
Before running scripts that interact with Vivado:
```bash
source /path/to/Vivado/2024.1/settings64.sh
```

## Quick Start

### 1. Run All Tests
```bash
./scripts/test_runner.py --suite basic
```

### 2. Build and Program FPGA
```bash
./scripts/vivado_build.py main
./scripts/fpga_programmer.py
```

### 3. Full Validation Workflow
```bash
./scripts/run_full_validation.py all
```

## Detailed Usage

### Master Validation Script

`run_full_validation.py` orchestrates the complete validation workflow.

**Basic Usage:**
```bash
# Run specific steps
./scripts/run_full_validation.py tests
./scripts/run_full_validation.py build-main program
./scripts/run_full_validation.py tests compare

# Run everything
./scripts/run_full_validation.py all

# Dry run (show what would be done)
./scripts/run_full_validation.py all --dry-run

# Verbose output
./scripts/run_full_validation.py all --verbose
```

**Available Steps:**
- `tests` - Run cocotb test suite
- `build-vga` - Build VGA test pattern
- `build-simple` - Build simplified design
- `build-main` - Build full design
- `program` - Program FPGA
- `compare` - Compare FPGA vs Python reference
- `all` - Run all steps

**Options:**
- `--test-suite {basic,comparison,integration,all}` - Select test suite
- `--build-type {vga,simple,main,debug}` - Select build type
- `--compare-steps N` - Number of simulation steps for comparison
- `--compare-agents N` - Number of agents for comparison
- `--dry-run` - Show what would be done without executing
- `--verbose` - Show detailed output from all scripts
- `--continue-on-error` - Continue even if a step fails

**Examples:**
```bash
# Quick test-driven workflow
./scripts/run_full_validation.py tests build-main program

# Full validation with all tests
./scripts/run_full_validation.py all --test-suite all

# Build VGA test and program
./scripts/run_full_validation.py build-vga program

# Dry run to preview
./scripts/run_full_validation.py all --dry-run
```

### Vivado Build Script

`vivado_build.py` automates Vivado builds in batch mode.

**Basic Usage:**
```bash
# Build main design
./scripts/vivado_build.py main

# Build with options
./scripts/vivado_build.py main --verbose --save-json

# Clean and rebuild
./scripts/vivado_build.py simple --clean
```

**Build Types:**
- `main` - Full slime simulator with agent processor
- `simple` - Simplified version with trail animation
- `vga` - VGA test pattern (diagnostic)
- `debug` - Debug build with instrumentation

**Options:**
- `--rtl-dir PATH` - Path to RTL directory (default: ../rtl)
- `--clean` - Clean previous build before starting
- `--dry-run` - Show what would be done
- `--verbose` - Show all Vivado output
- `--save-json` - Save build results to JSON

**Output:**
- Bitstream file: `rtl/vivado_project*/*/impl_1/*.bit`
- Build logs: `rtl/build_logs/`
- Timing/utilization reports: `rtl/vivado_project*/`

**Examples:**
```bash
# Build main design with verbose output
./scripts/vivado_build.py main --verbose

# Clean rebuild of simple design
./scripts/vivado_build.py simple --clean --save-json

# VGA test build
./scripts/vivado_build.py vga
```

### Test Runner Script

`test_runner.py` runs cocotb simulation tests.

**Basic Usage:**
```bash
# Run single test
./scripts/test_runner.py lfsr

# Run multiple tests
./scripts/test_runner.py lfsr trig vga

# Run test suite
./scripts/test_runner.py --suite basic

# List available tests
./scripts/test_runner.py --list
```

**Available Tests:**
- `lfsr` - LFSR random number generator
- `fixed_point` - Fixed-point multiplication
- `trig` - Trigonometry LUT
- `vga` - VGA controller
- `trail_map` - Trail map integration
- `rtl_vs_python_lfsr` - LFSR RTL vs Python comparison
- `rtl_vs_python_fp` - Fixed-point RTL vs Python comparison
- `rtl_vs_python_trig` - Trig LUT RTL vs Python comparison

**Test Suites:**
- `basic` - Basic component tests (lfsr, fixed_point, trig, vga)
- `comparison` - RTL vs Python comparison tests
- `integration` - Integration tests (trail_map)
- `all` - All available tests

**Options:**
- `--suite {basic,comparison,integration,all}` - Run test suite
- `--list` - List available tests
- `--sim-dir PATH` - Simulation directory (default: ../rtl/sim)
- `--clean` - Clean artifacts before running
- `--dry-run` - Show what would be done
- `--verbose` - Show all test output
- `--save-json` - Save results to JSON
- `--output FILE` - Output JSON file path

**Examples:**
```bash
# Run basic tests with verbose output
./scripts/test_runner.py --suite basic --verbose

# Run comparison tests and save JSON
./scripts/test_runner.py --suite comparison --save-json

# Clean and run all tests
./scripts/test_runner.py --suite all --clean

# Run specific tests
./scripts/test_runner.py lfsr fixed_point trig
```

### FPGA Programmer Script

`fpga_programmer.py` programs Xilinx FPGAs via Vivado Hardware Manager.

**Basic Usage:**
```bash
# Auto-detect latest bitstream and program
./scripts/fpga_programmer.py

# Program specific bitstream
./scripts/fpga_programmer.py --bitstream path/to/design.bit

# Check if FPGA is connected
./scripts/fpga_programmer.py --check-only

# Program and read device info
./scripts/fpga_programmer.py --info
```

**Options:**
- `--bitstream FILE` - Path to bitstream file (.bit)
- `--rtl-dir PATH` - Path to RTL directory (default: ../rtl)
- `--check-only` - Only check if FPGA is connected
- `--info` - Read device information after programming
- `--dry-run` - Show what would be done
- `--verbose` - Show all Vivado output

**Examples:**
```bash
# Program with auto-detected bitstream
./scripts/fpga_programmer.py --verbose

# Program specific build
./scripts/fpga_programmer.py --bitstream rtl/vivado_project/slime_simulator.runs/impl_1/slime_top.bit

# Check FPGA connection
./scripts/fpga_programmer.py --check-only

# Dry run
./scripts/fpga_programmer.py --dry-run
```

**Troubleshooting:**
- **"No hardware targets found"** - Check USB connection
- **"Vivado not found"** - Source settings64.sh
- **Cable driver issues** - Install Xilinx cable drivers

### Image Capture Script

`image_capture.py` captures trail maps from FPGA and compares with Python reference.

**Basic Usage:**
```bash
# Generate Python reference
./scripts/image_capture.py reference --steps 10

# Capture from FPGA (requires debug infrastructure)
./scripts/image_capture.py capture

# Compare two trail maps
./scripts/image_capture.py compare --fpga fpga.bin --ref ref.bin

# Full workflow
./scripts/image_capture.py full --steps 10 --agents 100
```

**Modes:**
- `reference` - Generate Python reference trail map
- `capture` - Capture from FPGA via JTAG
- `compare` - Compare FPGA and reference trail maps
- `full` - Full workflow (generate, capture, compare)

**Options:**
- `--fpga FILE` - FPGA trail map file (for compare mode)
- `--ref FILE` - Reference trail map file (for compare mode)
- `--steps N` - Number of simulation steps (default: 10)
- `--agents N` - Number of agents (default: 100)
- `--width N` - Trail map width (default: 160)
- `--height N` - Trail map height (default: 120)
- `--tolerance N` - Comparison tolerance (default: 5)
- `--output-dir PATH` - Output directory for images
- `--save-images` - Save comparison images (requires PIL)
- `--dry-run` - Show what would be done
- `--verbose` - Verbose output

**Examples:**
```bash
# Generate reference with 20 steps
./scripts/image_capture.py reference --steps 20 --agents 200

# Full workflow with image saving
./scripts/image_capture.py full --steps 10 --save-images

# Compare existing files
./scripts/image_capture.py compare \
  --fpga fpga_trail.bin \
  --ref reference_trail.bin \
  --save-images

# Custom resolution
./scripts/image_capture.py reference \
  --width 640 --height 480 \
  --steps 5
```

**Note:** JTAG capture requires debug infrastructure (ILA/VIO) in the FPGA design. The current implementation provides a framework that needs to be connected to your specific debug implementation.

## Common Workflows

### Development Workflow

```bash
# 1. Run tests to verify changes
./scripts/test_runner.py --suite basic

# 2. Build the design
./scripts/vivado_build.py main --clean

# 3. Program the FPGA
./scripts/fpga_programmer.py

# 4. Test on hardware (if debug infrastructure available)
./scripts/image_capture.py full --steps 10
```

### Quick Validation

```bash
# Run everything with one command
./scripts/run_full_validation.py all
```

### Testing Only

```bash
# Run all tests
./scripts/test_runner.py --suite all --save-json

# Run specific test with verbose output
./scripts/test_runner.py trail_map --verbose
```

### Build and Deploy

```bash
# Build and program in one go
./scripts/run_full_validation.py build-main program
```

### Comparison Testing

```bash
# Generate reference and compare
./scripts/image_capture.py reference --steps 20
./scripts/image_capture.py capture
./scripts/image_capture.py compare --fpga captured.bin --ref reference.bin
```

## Output and Logs

All scripts generate timestamped log files:

- **Test logs:** `rtl/sim/test_logs/`
- **Build logs:** `rtl/build_logs/`
- **Programming logs:** `rtl/programming_logs/`
- **Capture logs:** `output_images/logs/`
- **Validation logs:** `validation_logs/`

JSON results (when `--save-json` is used):
- Test results
- Build statistics (timing, utilization)
- Comparison metrics

## Dry Run Mode

All scripts support `--dry-run` to preview actions without executing:

```bash
# Preview what would happen
./scripts/run_full_validation.py all --dry-run
./scripts/vivado_build.py main --dry-run
./scripts/test_runner.py --suite all --dry-run
```

## Verbose Mode

Use `--verbose` or `-v` for detailed output:

```bash
# See all Vivado output
./scripts/vivado_build.py main --verbose

# See all test output
./scripts/test_runner.py lfsr --verbose

# Verbose validation
./scripts/run_full_validation.py all --verbose
```

## Troubleshooting

### Common Issues

1. **"Vivado not found in PATH"**
   ```bash
   source /path/to/Vivado/2024.1/settings64.sh
   ```

2. **"cocotb not found"**
   ```bash
   pip install cocotb
   ```

3. **"No hardware targets found"**
   - Check USB cable connection
   - Verify FPGA is powered on
   - Install Xilinx cable drivers

4. **Build fails with timing violations**
   - Check timing reports in `rtl/vivado_project/timing.txt`
   - Consider relaxing constraints or optimizing design

5. **Tests fail**
   - Run with `--verbose` to see detailed output
   - Check test logs in `rtl/sim/test_logs/`
   - Verify Python dependencies are installed

### Getting Help

Each script has detailed help:
```bash
./scripts/run_full_validation.py --help
./scripts/vivado_build.py --help
./scripts/test_runner.py --help
./scripts/fpga_programmer.py --help
./scripts/image_capture.py --help
```

## Script Execution Permissions

Make scripts executable:
```bash
chmod +x scripts/*.py
```

Or run with Python explicitly:
```bash
python3 scripts/run_full_validation.py all
```

## Integration with CI/CD

These scripts are designed to work in CI/CD environments:

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: python3 scripts/test_runner.py --suite all --save-json

- name: Build Design
  run: python3 scripts/vivado_build.py main --save-json

- name: Upload Results
  uses: actions/upload-artifact@v2
  with:
    name: test-results
    path: rtl/sim/test_logs/*.json
```

## Advanced Usage

### Custom Build Configurations

Modify build scripts to add new configurations:
```python
# In vivado_build.py, add to BUILD_CONFIGS:
'custom': {
    'tcl_script': 'build_custom.tcl',
    'project_dir': 'vivado_project_custom',
    # ...
}
```

### Parallel Execution

Run independent tasks in parallel:
```bash
# Terminal 1
./scripts/test_runner.py --suite basic

# Terminal 2
./scripts/vivado_build.py vga
```

### Scripting with Python

Import and use directly in Python scripts:
```python
from scripts.test_runner import TestRunner

runner = TestRunner()
runner.run_tests(['lfsr', 'trig'])
results = runner.results
```

## Contributing

When adding new scripts:
1. Follow the existing structure (argparse, logging, dry-run support)
2. Add comprehensive help text
3. Document in this README
4. Include error handling and validation
5. Support both standalone and integrated usage

## License

Same license as the main SlimeSimulator project.
