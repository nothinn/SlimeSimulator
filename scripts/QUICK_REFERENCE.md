# Automation Scripts - Quick Reference

## One-Line Commands

### Full Workflow
```bash
# Run everything (tests, build, program, compare)
./scripts/run_full_validation.py all

# Preview what would happen
./scripts/run_full_validation.py all --dry-run
```

### Testing
```bash
# Run basic tests
./scripts/test_runner.py --suite basic

# Run all tests
./scripts/test_runner.py --suite all

# Run specific test
./scripts/test_runner.py lfsr --verbose

# List available tests
./scripts/test_runner.py --list
```

### Building
```bash
# Build main design
./scripts/vivado_build.py main

# Build VGA test pattern
./scripts/vivado_build.py vga

# Build with clean
./scripts/vivado_build.py main --clean --verbose
```

### Programming
```bash
# Program FPGA (auto-detect bitstream)
./scripts/fpga_programmer.py

# Program specific bitstream
./scripts/fpga_programmer.py --bitstream path/to/design.bit

# Check FPGA connection
./scripts/fpga_programmer.py --check-only
```

### Image Capture & Comparison
```bash
# Generate Python reference
./scripts/image_capture.py reference --steps 10

# Full comparison workflow
./scripts/image_capture.py full --steps 10 --save-images

# Compare existing files
./scripts/image_capture.py compare --fpga fpga.bin --ref ref.bin
```

## Common Scenarios

### Scenario 1: Quick Test
```bash
./scripts/test_runner.py --suite basic
```

### Scenario 2: Build and Deploy
```bash
./scripts/vivado_build.py main
./scripts/fpga_programmer.py
```

### Scenario 3: Full Validation
```bash
./scripts/run_full_validation.py all
```

### Scenario 4: Test-Driven Development
```bash
# Test -> Build -> Deploy -> Verify
./scripts/run_full_validation.py tests build-main program compare
```

### Scenario 5: Debugging Build Issues
```bash
./scripts/vivado_build.py main --verbose --clean
```

### Scenario 6: VGA Diagnostic
```bash
./scripts/run_full_validation.py build-vga program
```

## Flags Reference

| Flag | Purpose | Works With |
|------|---------|------------|
| `--dry-run` | Preview without executing | All scripts |
| `--verbose` / `-v` | Show detailed output | All scripts |
| `--clean` | Clean before building/testing | build, test_runner |
| `--save-json` | Save results to JSON | build, test_runner |
| `--save-images` | Save comparison images | image_capture |
| `--list` | List available tests | test_runner |
| `--check-only` | Only check connection | fpga_programmer |
| `--info` | Read device info | fpga_programmer |

## Exit Codes

- `0` - Success
- `1` - Failure or error

## Environment Setup

Before running scripts that use Vivado:
```bash
source /path/to/Vivado/2024.1/settings64.sh
```

## Help

Get help for any script:
```bash
./scripts/run_full_validation.py --help
./scripts/vivado_build.py --help
./scripts/test_runner.py --help
./scripts/fpga_programmer.py --help
./scripts/image_capture.py --help
```

## Tips

1. **Always run from project root:**
   ```bash
   cd /home/reson/SlimeSimulator
   ./scripts/run_full_validation.py all
   ```

2. **Use dry-run first:**
   ```bash
   ./scripts/run_full_validation.py all --dry-run
   ```

3. **Check logs on failure:**
   - Test logs: `rtl/sim/test_logs/`
   - Build logs: `rtl/build_logs/`
   - Programming logs: `rtl/programming_logs/`
   - Validation logs: `validation_logs/`

4. **Save results for analysis:**
   ```bash
   ./scripts/test_runner.py --suite all --save-json
   ./scripts/vivado_build.py main --save-json
   ```

5. **Chain commands:**
   ```bash
   ./scripts/test_runner.py --suite basic && \
   ./scripts/vivado_build.py main && \
   ./scripts/fpga_programmer.py
   ```
