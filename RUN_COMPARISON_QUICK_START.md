# Quick Start: Automated Extended Comparison

## One-Command Workflow

```bash
./run_extended_comparison.sh
```

That's it! The script will:
1. ✓ Build Verilator binary (if needed)
2. ✓ Run RTL simulation for 10,000 steps
3. ✓ Generate 1,000 trail dumps
4. ✓ Run Python reference simulation
5. ✓ Generate 1,000 comparison PNG images
6. ✓ Produce statistics JSON

**Expected time**: 30-50 minutes
**Disk space**: ~5 GB

---

## Options

### Run with existing RTL dumps (skip simulation)
```bash
./run_extended_comparison.sh --no-rtl
```
This skips RTL simulation if you already have trail dumps. Useful for:
- Tweaking comparison parameters
- Re-running comparison with different seeds
- Saving time on subsequent runs

### Use existing Verilator binary
```bash
./run_extended_comparison.sh --no-build
```
Skips compilation. Uses existing binary at `rtl/sim/obj_dir_slime_top/Vslime_top`.

### Both
```bash
./run_extended_comparison.sh --no-build --no-rtl
```
Only runs Python simulation and generates comparison images. Fastest mode (5-10 min).

### Verbose output
```bash
./run_extended_comparison.sh --verbose
```
Shows detailed progress and debug output.

### Help
```bash
./run_extended_comparison.sh --help
```

---

## What Gets Generated

### Directory: `rtl_final_comparison_100k/`
```
comparison_00000.png        Step 0
comparison_00010.png        Step 10
comparison_00020.png        Step 20
...
comparison_09990.png        Step 9990
comparison_09999.png        Step 9999
comparison_stats.json       Statistics for all steps
```

### Statistics File Format
```json
[
  {
    "step": 0,
    "python": {"min": 0, "max": 5234, "mean": 234.5},
    "rtl": {"min": 0, "max": 5123, "mean": 231.2},
    "max_diff": 111,
    "filename": "comparison_00000.png"
  },
  ...
]
```

---

## Inspect Results

### View first/middle/last frames
```bash
open rtl_final_comparison_100k/comparison_00000.png
open rtl_final_comparison_100k/comparison_05000.png
open rtl_final_comparison_100k/comparison_09999.png
```

### Check statistics
```bash
python3 << 'EOF'
import json

with open('rtl_final_comparison_100k/comparison_stats.json') as f:
    stats = json.load(f)

# Show first, middle, and last
for idx in [0, len(stats)//2, -1]:
    s = stats[idx]
    print(f"Step {s['step']}:")
    print(f"  Python: mean={s['python']['mean']:.0f}, max={s['python']['max']}")
    print(f"  RTL:    mean={s['rtl']['mean']:.0f}, max={s['rtl']['max']}")
    print(f"  Diff:   {s['max_diff']}")
EOF
```

### Count generated files
```bash
ls rtl_final_comparison_100k/comparison_*.png | wc -l
du -sh rtl_final_comparison_100k/
du -sh rtl_trail_dumps/
```

---

## Troubleshooting

### "Command not found: verilator"
```bash
# Install Verilator (Ubuntu/Debian)
sudo apt install verilator

# Or download from: https://www.veripool.org/wiki/verilator
```

### "Virtual environment not found"
```bash
# Create it (one-time only)
python3 -m venv .venv

# Install dependencies
source .venv/bin/activate
pip install numpy pillow cocotb scipy pygame
```

### "RTL simulation failed" / "Trail dumps not found"
```bash
# Check if Verilator compilation succeeded
ls rtl/sim/obj_dir_slime_top/Vslime_top

# If not, rebuild
./run_extended_comparison.sh  # Remove --no-build flag
```

### "Out of disk space"
The script needs ~5 GB:
- RTL dumps: ~1.4 GB
- PNG images: ~3-5 GB

Check available space:
```bash
df -h
```

### "Too slow" / "Out of memory"
This is expected for 100k agents × 10k steps. You can:
1. Wait (total ~30-50 min)
2. Edit the script to use `--no-rtl` on second run (skip simulation phase)
3. Reduce agents/steps in source code (advanced)

---

## Advanced: Customize Parameters

Edit `rtl_final_comparison.py` before running:

### Change simulation seed
```python
seed=0xDEADBEEF  # Change to 0x12345678 or any 32-bit value
```

### Reduce for quick test
```python
num_agents=10000,        # 100k → 10k
num_steps=1000,          # 10k → 1k
```

Then re-run comparison:
```bash
./run_extended_comparison.sh --no-build --no-rtl
```

---

## Expected Behavior

### During RTL Simulation
```
[TB] Initializing 100,000 agents...
[TB] Agents initialized in circle pointing inward
Processing agents with sensory logic for 10000 steps...
  Progress:  10%
  Progress:  20%
  ...
  Progress: 100%
```

### During Python Comparison
```
Running Python reference simulation...
[    0/10000] Generating comparison frame... ✓ comparison_00000.png
[   10/10000] Generating comparison frame... ✓ comparison_00010.png
...
[10000/10000] Generating comparison frame... ✓ comparison_09999.png
```

### Final Output
```
════════════════════════════════════════════════════════════════
  COMPARISON COMPLETE
════════════════════════════════════════════════════════════════

📊 Results Summary:
  • RTL trail dumps: 1001 files
  • Comparison frames: 1001 PNG images
  • Output directory: rtl_final_comparison_100k/
  • Statistics JSON: rtl_final_comparison_100k/comparison_stats.json

✓ All phases completed successfully!
```

---

## Performance Expectations

| Phase | Time | Output |
|-------|------|--------|
| Verilator build | 1-2 min | Binary executable |
| RTL simulation | 10-15 min | 1,001 × 1.44 MB dumps |
| Python reference | 3-5 min | Trail maps (in memory) |
| Image generation | 15-30 min | 1,001 × 1.2-1.5 MB PNGs |
| **Total** | **30-50 min** | **~5 GB on disk** |

---

## Files Created/Modified

### New Files
- `run_extended_comparison.sh` - This automation script
- `rtl_final_comparison_100k/` - Output directory (created during run)
- `rtl_trail_dumps/` - RTL binary dumps (cleaned/created each run)

### Modified Files
- `rtl/sim/slime_verilator_full_tb.cpp` - Updated for 10k steps, 10-step dumps
- `rtl_final_comparison.py` - Updated for 10k steps, correct display text

### Documentation (New)
- `EXTENDED_COMPARISON_GUIDE.md` - Detailed technical guide
- `COMPARISON_ARCHITECTURE.md` - Architecture and data flow
- `RUN_COMPARISON_QUICK_START.md` - This file

---

## Cleanup

To save space after comparison:

```bash
# Keep images, remove dumps (1.4 GB saved)
rm -rf rtl_trail_dumps/

# Remove old builds (50 MB saved)
rm -rf rtl/sim/obj_dir*

# Keep only final images and stats
# (rtl_final_comparison_100k/ stays)
```

---

## Integration with Development

This script is designed for the workflow:

```
Make code change
    ↓
./run_extended_comparison.sh
    ↓
Review images in rtl_final_comparison_100k/
    ↓
Check statistics in comparison_stats.json
    ↓
Iterate
```

Use `--no-build --no-rtl` for fast iteration on comparison parameters.

---

## Support

For issues, check:
1. **EXTENDED_COMPARISON_GUIDE.md** - Troubleshooting section
2. **COMPARISON_ARCHITECTURE.md** - Technical details
3. **CLAUDE.md** - Project structure and commands
4. **slime_simulator.py** - Python implementation
5. **rtl/sim/slime_verilator_full_tb.cpp** - RTL testbench

---

Happy comparing! 🧪
