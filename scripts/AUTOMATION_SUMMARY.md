# SlimeSimulator Automation Scripts - Summary

## What Was Created

A complete automation suite for the SlimeSimulator FPGA project with 5 Python scripts and comprehensive documentation.

### Scripts Created

1. **`run_full_validation.py`** (12 KB)
   - Master orchestration script
   - Runs complete validation workflow
   - Supports selective step execution
   - Generates comprehensive reports

2. **`vivado_build.py`** (14 KB)
   - Automated Vivado builds in batch mode
   - Supports multiple build configurations
   - Parses timing and utilization reports
   - Provides detailed build status

3. **`test_runner.py`** (16 KB)
   - Runs cocotb simulation tests
   - Supports individual tests and test suites
   - Parses and reports test results
   - Saves results to JSON

4. **`fpga_programmer.py`** (14 KB)
   - Programs FPGA via Vivado Hardware Manager
   - Auto-detects latest bitstream
   - Verifies FPGA connectivity
   - Reads device information

5. **`image_capture.py`** (18 KB)
   - Captures trail maps from FPGA via JTAG
   - Generates Python reference implementations
   - Compares FPGA vs reference
   - Generates comparison reports and images

### Documentation

- **`README.md`** (13 KB) - Comprehensive usage guide
- **`QUICK_REFERENCE.md`** (3.6 KB) - Quick command reference
- **`AUTOMATION_SUMMARY.md`** (This file) - Overview and setup

## Key Features

### All Scripts Include:
- Command-line argument parsing with argparse
- Dry-run mode (`--dry-run`)
- Verbose mode (`--verbose`)
- Timestamped logging
- Error handling with helpful messages
- Can be run from project root
- Support for both standalone and integrated usage

### Master Script Capabilities:
- Run complete workflow or selective steps
- Progress tracking across all stages
- Consolidated logging and reporting
- Continue-on-error mode
- JSON result export
- Time tracking for each step

## Quick Start

### 1. Make Scripts Executable (Already Done)
```bash
chmod +x scripts/*.py
```

### 2. Set Up Environment
```bash
# For Vivado operations
source /path/to/Vivado/2024.1/settings64.sh

# Install Python dependencies
pip install numpy pillow cocotb
```

### 3. Run Your First Test
```bash
cd /home/reson/SlimeSimulator
./scripts/test_runner.py --suite basic
```

### 4. Run Full Validation
```bash
./scripts/run_full_validation.py all
```

## Usage Examples

### Example 1: Quick Test
```bash
./scripts/test_runner.py lfsr --verbose
```

### Example 2: Build Main Design
```bash
./scripts/vivado_build.py main --clean --verbose
```

### Example 3: Program FPGA
```bash
./scripts/fpga_programmer.py --info
```

### Example 4: Full Workflow
```bash
./scripts/run_full_validation.py all --verbose
```

### Example 5: Dry Run
```bash
./scripts/run_full_validation.py all --dry-run
```

## Directory Structure

```
SlimeSimulator/
├── scripts/                        # Automation scripts (NEW)
│   ├── run_full_validation.py     # Master script
│   ├── vivado_build.py            # Build automation
│   ├── test_runner.py             # Test runner
│   ├── fpga_programmer.py         # FPGA programming
│   ├── image_capture.py           # Image capture/compare
│   ├── README.md                  # Full documentation
│   ├── QUICK_REFERENCE.md         # Quick reference
│   └── AUTOMATION_SUMMARY.md      # This file
├── rtl/
│   ├── sim/                       # Tests work here
│   ├── src/                       # RTL sources
│   ├── constraints/               # Constraint files
│   ├── *.tcl                      # TCL scripts (used by automation)
│   ├── build_logs/                # Build logs (created by scripts)
│   └── programming_logs/          # Programming logs (created by scripts)
├── validation_logs/               # Master logs (created by scripts)
└── output_images/                 # Captured images (created by scripts)
```

## Log Locations

All scripts create timestamped logs:

- **Test logs:** `rtl/sim/test_logs/test_run_YYYYMMDD_HHMMSS.log`
- **Build logs:** `rtl/build_logs/build_TYPE_YYYYMMDD_HHMMSS.log`
- **Programming logs:** `rtl/programming_logs/program_YYYYMMDD_HHMMSS.log`
- **Capture logs:** `output_images/logs/capture_YYYYMMDD_HHMMSS.log`
- **Validation logs:** `validation_logs/validation_YYYYMMDD_HHMMSS.log`

## JSON Result Files

When using `--save-json`:

- **Test results:** `rtl/sim/test_logs/test_results_*.json`
- **Build results:** `rtl/build_logs/build_results_*.json`
- **Comparison results:** `output_images/comparison_report_*.json`
- **Validation results:** `validation_logs/validation_results_*.json`

## Script Capabilities Matrix

| Feature | Master | Build | Test | Program | Capture |
|---------|--------|-------|------|---------|---------|
| Dry Run | ✓ | ✓ | ✓ | ✓ | ✓ |
| Verbose | ✓ | ✓ | ✓ | ✓ | ✓ |
| Logging | ✓ | ✓ | ✓ | ✓ | ✓ |
| JSON Export | ✓ | ✓ | ✓ | - | ✓ |
| Progress Tracking | ✓ | ✓ | ✓ | ✓ | ✓ |
| Error Recovery | ✓ | ✓ | - | - | - |
| Auto-detect | ✓ | - | - | ✓ | ✓ |

## Workflow Recommendations

### Daily Development
```bash
# Quick test
./scripts/test_runner.py --suite basic

# Build and test
./scripts/vivado_build.py main
./scripts/fpga_programmer.py
```

### Pre-Commit Validation
```bash
# Run all tests
./scripts/test_runner.py --suite all --save-json
```

### Release Validation
```bash
# Full validation with all steps
./scripts/run_full_validation.py all --verbose --test-suite all
```

### Debugging
```bash
# Verbose builds
./scripts/vivado_build.py main --verbose --clean

# Verbose tests
./scripts/test_runner.py trail_map --verbose
```

## Dependencies Summary

### Required for All Operations
- Python 3.6+
- Standard Python libraries (argparse, subprocess, pathlib, json, datetime)

### For Simulation Tests
- Icarus Verilog
- cocotb
- NumPy (for comparison tests)
- GNU Make

### For FPGA Operations
- Xilinx Vivado (with license)
- Vivado settings64.sh sourced

### For Image Operations
- NumPy
- PIL/Pillow (optional, for image saving)
- Python reference implementation (in rtl/sim/)

## Troubleshooting Quick Guide

### "Vivado not found"
```bash
source /path/to/Vivado/2024.1/settings64.sh
```

### "cocotb not found"
```bash
pip install cocotb
```

### "No hardware targets found"
- Check USB connection
- Verify FPGA power
- Install cable drivers

### Scripts not executable
```bash
chmod +x scripts/*.py
```

### Import errors
```bash
# Run from project root
cd /home/reson/SlimeSimulator
./scripts/run_full_validation.py all
```

## Advanced Features

### Continue on Error
```bash
./scripts/run_full_validation.py all --continue-on-error
```

### Custom Test Suites
```bash
./scripts/test_runner.py lfsr trig vga --save-json
```

### Specific Build Types
```bash
./scripts/run_full_validation.py build-vga program
```

### Custom Comparison Parameters
```bash
./scripts/image_capture.py full --steps 20 --agents 200 --save-images
```

## Integration Examples

### Shell Script Integration
```bash
#!/bin/bash
set -e

echo "Running validation..."
./scripts/run_full_validation.py all --verbose

if [ $? -eq 0 ]; then
    echo "Validation PASSED"
    exit 0
else
    echo "Validation FAILED"
    exit 1
fi
```

### Makefile Integration
```makefile
.PHONY: test build program validate

test:
	./scripts/test_runner.py --suite all

build:
	./scripts/vivado_build.py main --clean

program:
	./scripts/fpga_programmer.py

validate:
	./scripts/run_full_validation.py all
```

### Python Integration
```python
#!/usr/bin/env python3
import subprocess
import sys

def run_validation():
    result = subprocess.run(
        ['./scripts/run_full_validation.py', 'all'],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print("Validation passed!")
    else:
        print("Validation failed!")
        print(result.stdout)

    return result.returncode

if __name__ == '__main__':
    sys.exit(run_validation())
```

## Next Steps

1. **Read the full README:**
   ```bash
   cat scripts/README.md
   ```

2. **Try the quick reference:**
   ```bash
   cat scripts/QUICK_REFERENCE.md
   ```

3. **Get help for each script:**
   ```bash
   ./scripts/run_full_validation.py --help
   ./scripts/vivado_build.py --help
   ./scripts/test_runner.py --help
   ./scripts/fpga_programmer.py --help
   ./scripts/image_capture.py --help
   ```

4. **Start with a dry run:**
   ```bash
   ./scripts/run_full_validation.py all --dry-run
   ```

5. **Run your first test:**
   ```bash
   ./scripts/test_runner.py --list
   ./scripts/test_runner.py lfsr
   ```

## Support

For issues or questions:
1. Check the README.md for detailed documentation
2. Run scripts with `--help` for usage information
3. Use `--verbose` for detailed debugging output
4. Check log files in respective log directories
5. Use `--dry-run` to preview operations

## License

These automation scripts are part of the SlimeSimulator project and follow the same license.

---

**Created:** 2025-11-25
**Location:** `/home/reson/SlimeSimulator/scripts/`
**Total Scripts:** 5 (100 KB total)
**Documentation:** 3 files (30 KB)
**Status:** Ready to use
