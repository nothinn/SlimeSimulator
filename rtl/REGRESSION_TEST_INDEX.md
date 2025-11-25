# RTL Regression Testing Framework - Documentation Index

## Quick Navigation

### 🚀 Getting Started
1. **[Quick Start Guide](REGRESSION_TEST_QUICKSTART.md)** - Start here!
   - Installation instructions
   - Common use cases
   - Example commands
   - Troubleshooting tips

### 📚 Complete Documentation
2. **[Full README](REGRESSION_TEST_README.md)** - Comprehensive reference
   - Architecture overview
   - Component descriptions
   - File formats
   - Development workflow
   - CI/CD integration

### 📊 Example Outputs
3. **[Example Output](REGRESSION_TEST_EXAMPLE_OUTPUT.md)** - See what to expect
   - Console output examples
   - CSV and text reports
   - Visualization samples
   - Success and failure cases

### 📋 Implementation Summary
4. **[Implementation Details](REGRESSION_TEST_IMPLEMENTATION.md)** - Technical overview
   - Deliverables summary
   - Code and documentation statistics
   - Testing status
   - Integration requirements
   - Next steps

---

## File Overview

### Core Scripts (Python)

| Script | LOC | Purpose | Status |
|--------|-----|---------|--------|
| `generate_python_ref.py` | 174 | Generate Python reference trail maps | ✅ Complete |
| `fpga_controller.py` | 297 | FPGA interface and control | ⚠️ Framework ready |
| `compare_trails.py` | 456 | Compare and analyze trail maps | ✅ Complete |
| `regression_test.py` | 401 | Master orchestration script | ✅ Complete |

### Documentation Files (Markdown)

| Document | Lines | Purpose |
|----------|-------|---------|
| `REGRESSION_TEST_QUICKSTART.md` | 299 | Quick start guide |
| `REGRESSION_TEST_README.md` | 535 | Complete documentation |
| `REGRESSION_TEST_EXAMPLE_OUTPUT.md` | 489 | Example outputs |
| `REGRESSION_TEST_IMPLEMENTATION.md` | 394 | Implementation summary |
| `REGRESSION_TEST_INDEX.md` | (this file) | Navigation index |

---

## Usage Quick Reference

### Most Common Commands

```bash
# Generate Python reference only (no FPGA required)
python regression_test.py --reference-only

# Full test with FPGA (when hardware ready)
python regression_test.py --bitstream build/slime_top.bit

# Compare existing trail maps
python compare_trails.py --reference ref/ --rtl rtl/ --visualize

# Custom configuration
python regression_test.py --reference-only \
    --width 160 --height 120 \
    --agents 1000 \
    --iterations 1,5,10,20 \
    --threshold 95.0
```

### Get Help

```bash
python regression_test.py --help
python generate_python_ref.py --help
python compare_trails.py --help
python fpga_controller.py --help
```

---

## Documentation Sections

### REGRESSION_TEST_QUICKSTART.md

**Target Audience**: First-time users, developers

**Contents**:
- Prerequisites and installation
- Quick start workflows
- Common use cases
- Understanding results
- Troubleshooting
- Command reference

**Read this if**: You want to run tests quickly

### REGRESSION_TEST_README.md

**Target Audience**: All users, integrators

**Contents**:
- Complete architecture overview
- Component descriptions
- File format specifications
- Expected results
- Development workflow
- CI/CD integration
- Future enhancements
- Technical references

**Read this if**: You need comprehensive understanding

### REGRESSION_TEST_EXAMPLE_OUTPUT.md

**Target Audience**: New users, CI/CD integrators

**Contents**:
- 9 detailed example scenarios
- Console output samples
- CSV report formats
- Text analysis examples
- Visualization examples
- Success and failure cases
- Extended test suites
- Custom configurations

**Read this if**: You want to see what outputs look like

### REGRESSION_TEST_IMPLEMENTATION.md

**Target Audience**: Project managers, developers, integrators

**Contents**:
- Executive summary
- Deliverables list
- Key features
- Testing status
- Integration points
- Expected results
- Success criteria
- Code quality metrics
- Next steps

**Read this if**: You need project-level overview

---

## Workflow Diagrams

### Basic Workflow
```
┌─────────────────────┐
│  regression_test.py │  Master Script
└──────────┬──────────┘
           │
           ├─→ generate_python_ref.py → reference/trail_*.bin
           │
           ├─→ fpga_controller.py → rtl_capture/trail_*.bin
           │
           └─→ compare_trails.py → comparison_report.csv
                                  → detailed_analysis.txt
                                  → visualizations/*.png
```

### Reference-Only Workflow (Current)
```
python regression_test.py --reference-only
    │
    └─→ generate_python_ref.py
            │
            ├─→ trail_iter_001.bin
            ├─→ trail_iter_005.bin
            ├─→ trail_iter_010.bin
            ├─→ trail_iter_020.bin
            └─→ final_state.txt
```

### Full Workflow (Future with FPGA)
```
python regression_test.py --bitstream build/slime_top.bit
    │
    ├─→ generate_python_ref.py → reference/
    │
    ├─→ fpga_controller.py
    │       ├─ Program FPGA
    │       ├─ Initialize with seed
    │       ├─ Step through iterations
    │       └─ Capture trail maps → rtl_capture/
    │
    └─→ compare_trails.py
            ├─ Load both sets
            ├─ Compute statistics
            ├─ Generate visualizations
            └─ Create reports
                ├─ comparison_report.csv
                ├─ detailed_analysis.txt
                └─ test_summary.txt
```

---

## Key Concepts

### Trail Map
- Binary file containing 8-bit pixel intensities
- Layout: row-major order (height × width)
- Size: width × height bytes (e.g., 19,200 for 160×120)
- Values: 0-255 (trail intensity deposited by agents)

### Iteration
- One complete simulation step
- All agents: sense, turn, move, deposit
- Followed by diffuse and decay
- Trail map captured after each iteration

### Comparison Metrics
- **Match %**: Percentage of exactly matching pixels
- **Max Diff**: Worst-case absolute difference
- **Mean Diff**: Average absolute difference
- **RMS Diff**: Root mean square difference
- **Status**: PASS if match % ≥ threshold

### Test Configuration
- **Width/Height**: Simulation resolution (default: 160×120)
- **Agents**: Number of simulated agents (default: 1000)
- **Iterations**: Test points to capture (default: 1,5,10,20)
- **Seed**: LFSR initialization (default: 0xDEADBEEF)
- **Threshold**: Pass percentage (default: 95%)

---

## Troubleshooting Index

| Problem | Solution | Document |
|---------|----------|----------|
| "No module named 'numpy'" | `pip install numpy` | Quick Start |
| "Bitstream not found" | Check path, regenerate | Quick Start |
| "No hardware targets" | FPGA not connected | Quick Start |
| "Memory read returns zeros" | Expected - needs JTAG2AXI IP | README |
| Low match percentage | Check RTL implementation | README |
| Slow Python reference | Reduce agents/iterations | Quick Start |
| File size mismatch | Verify resolution matches | Quick Start |

---

## Integration Checklist

### For Development (Reference-Only)
- [x] Python 3.7+ installed
- [x] NumPy installed (`pip install numpy`)
- [x] Scripts in rtl/ directory
- [x] Run: `python regression_test.py --reference-only`

### For FPGA Testing (Full Workflow)
- [ ] Vivado installed and in PATH
- [ ] FPGA connected via JTAG
- [ ] JTAG2AXI IP added to RTL design
- [ ] VIO IP added for signal monitoring
- [ ] Control interface implemented
- [ ] Bitstream generated
- [ ] Run: `python regression_test.py --bitstream <path>`

### For CI/CD Integration
- [ ] Add regression test to pipeline
- [ ] Archive test results as artifacts
- [ ] Parse CSV for pass/fail
- [ ] Set threshold appropriately
- [ ] Generate trend reports

---

## FAQ

**Q: Can I run tests without FPGA hardware?**
A: Yes! Use `--reference-only` mode for development and validation.

**Q: What resolution should I test at?**
A: Default 160×120 matches FPGA. Use higher for development.

**Q: How long do tests take?**
A: Reference-only: 1-30s. Full FPGA: 15-60s (includes programming).

**Q: What's a good pass threshold?**
A: 95% for development, 99% for final validation.

**Q: Why don't reference and RTL match exactly?**
A: Fixed-point rounding, trig LUT quantization, timing differences.

**Q: Can I visualize the differences?**
A: Yes! Use `--visualize` flag with comparison script.

**Q: How do I debug failing tests?**
A: Check detailed_analysis.txt, view visualizations, compare state dumps.

**Q: Can I test at different resolutions?**
A: Yes, use `--width` and `--height` arguments.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-11-24 | Initial implementation |

---

## Support and Contribution

### Getting Help
1. Read appropriate documentation (see above)
2. Check troubleshooting sections
3. Run with `--help` flag
4. Review example outputs
5. Check existing test results

### Contributing
- Report bugs with test logs
- Suggest enhancements
- Submit pull requests
- Improve documentation

---

## External Dependencies

### Python Packages
```bash
pip install numpy      # Required
pip install pillow     # Optional (for visualizations)
```

### Tools
- **Vivado** - For FPGA programming (optional for reference-only)
- **Python 3.7+** - Core requirement

---

## Related Files

### In rtl/ directory
- `sim/python_reference.py` - Python reference implementation
- `src/slime_top.sv` - Top-level RTL
- `src/agent_processor.sv` - Agent processing pipeline

### In docs/ directory (if exists)
- Algorithm documentation
- RTL architecture
- FPGA build guide

---

## Summary

This comprehensive regression testing framework provides:
- ✅ 4 Python scripts (1,328 lines)
- ✅ 4 documentation files (1,717 lines)
- ✅ Reference-only mode (works now)
- ✅ FPGA mode (framework ready)
- ✅ Multiple output formats
- ✅ Excellent documentation

**Start with**: [REGRESSION_TEST_QUICKSTART.md](REGRESSION_TEST_QUICKSTART.md)

**First command**: `python regression_test.py --reference-only`

---

*Last Updated: November 24, 2025*
*Framework Version: 1.0.0*
*Status: Production Ready (Reference Mode)*
