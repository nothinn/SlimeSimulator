# Comparison Automation - Complete Setup

## What You Now Have

A fully automated shell script that runs the entire 10× extended RTL vs Python comparison workflow in one command.

---

## Quick Start (TL;DR)

```bash
cd /home/reson/SlimeSimulator
./run_extended_comparison.sh
```

**Time**: ~30-50 minutes
**Output**: ~1,000 comparison PNG images + statistics JSON

Done! 🎉

---

## Files Created

### 1. **run_extended_comparison.sh** (9.3 KB)
The main automation script. It:
- Builds Verilator binary (if needed)
- Runs RTL simulation for 10,000 steps with dumps every 10 steps
- Runs Python reference simulation
- Generates 1,000 comparison images
- Produces statistics and summary

**Executable**: ✓ Ready to use

**Usage Examples**:
```bash
# Full run (from scratch)
./run_extended_comparison.sh

# Skip compilation (use existing binary)
./run_extended_comparison.sh --no-build

# Skip RTL simulation (use existing trail dumps)
./run_extended_comparison.sh --no-rtl

# Both (only generate comparison images)
./run_extended_comparison.sh --no-build --no-rtl

# Show help
./run_extended_comparison.sh --help
```

### 2. **RUN_COMPARISON_QUICK_START.md**
Quick reference guide for the automation script:
- Usage options
- What gets generated
- How to inspect results
- Troubleshooting
- Performance expectations

### 3. **EXTENDED_COMPARISON_GUIDE.md**
Comprehensive 300-line guide covering:
- What it takes to compare Python vs RTL
- Step-by-step instructions
- Understanding output metrics
- Performance expectations
- Advanced options
- Quality metrics

### 4. **COMPARISON_ARCHITECTURE.md**
Deep technical documentation with:
- Data flow diagrams
- Component relationships
- Synchronization points
- Agreement metrics
- Debugging mismatches
- Data format specifications

---

## Modified Source Files

### **rtl/sim/slime_verilator_full_tb.cpp**
```diff
- const int NUM_STEPS = 1000;
+ const int NUM_STEPS = 10000;      // 10× longer
- const int DUMP_INTERVAL = 100;
+ const int DUMP_INTERVAL = 10;     // 10× more frequent
```

**Effect**:
- Simulation runs 10,000 steps (was 1,000)
- Trail dumps every 10 steps (was every 100)
- Generates ~1,001 dumps instead of ~11

### **rtl_final_comparison.py**
```diff
- print(f"  Steps: 1,000")
+ print(f"  Steps: 10,000")
- print(f"[{step:4d}/1000]")
+ print(f"[{step:5d}/10000]")
- draw.text(..., "...1000 steps...")
+ draw.text(..., "...10000 steps...")
- f"Step {step}/1000 | ..."
+ f"Step {step}/10000 | ..."
```

**Effect**:
- Correct display of 10,000 steps throughout
- Proper progress indicator formatting

---

## Workflow Overview

```
START
  │
  ├─→ [Phase 1] Verilator Compilation (1-2 min)
  │   ├─ Clean previous builds
  │   ├─ Run verilator on SystemVerilog
  │   └─ Build C++ executable
  │
  ├─→ [Phase 2] RTL Simulation (10-15 min)
  │   ├─ Initialize 100k agents in circle pattern
  │   ├─ Run 10,000 simulation steps
  │   ├─ Dump trail map every 10 steps
  │   └─ Output: ~1,001 binary trail files (1.4 GB)
  │
  ├─→ [Phase 3] Comparison (10-20 min)
  │   ├─ Run Python reference for 10,000 steps
  │   ├─ Generate side-by-side images for each step
  │   ├─ Compute pixel-level statistics
  │   └─ Output: ~1,001 PNG images + stats JSON (3-5 GB)
  │
  └─→ COMPLETE
      ├─ Show results summary
      ├─ Display output directory location
      └─ Ready for analysis
```

---

## Output Structure

```
rtl_final_comparison_100k/
├── comparison_00000.png          ← Step 0 (both Python & RTL at start)
├── comparison_00010.png          ← Step 10
├── comparison_00020.png          ← Step 20
├── comparison_00050.png          ← Step 50
├── comparison_00100.png          ← Step 100 (initial trails forming)
├── comparison_00500.png          ← Step 500 (networks developing)
├── comparison_01000.png          ← Step 1000 (complex patterns)
├── comparison_05000.png          ← Step 5000 (maturity)
├── comparison_09990.png          ← Step 9990 (full convergence)
├── comparison_09999.png          ← Step 9999 (final state)
└── comparison_stats.json         ← Statistics for all 1001 frames

Also generates:
rtl_trail_dumps/
├── trail_step_00000.bin          ← 1.44 MB binary dump
├── trail_step_00010.bin
├── trail_step_00020.bin
├── ...
└── trail_step_09999.bin          ← 1,001 total files = 1.4 GB
```

---

## Key Features

### ✓ Smart Options
- `--no-build`: Skip compilation (5-10 min faster on reruns)
- `--no-rtl`: Skip simulation (fast iteration on comparison parameters)
- `--verbose`: Show detailed progress

### ✓ Comprehensive Progress Tracking
- Phase headers with timing expectations
- Section markers for each step
- Color-coded output (errors, success, info)
- Real-time progress from RTL simulator
- Final summary with disk usage

### ✓ Error Handling
- Exits on first error (`set -e`)
- Verifies commands exist (verilator, python3)
- Checks for virtual environment
- Validates output at each phase
- Detailed error messages with suggestions

### ✓ Automatic Cleanup
- Removes old trial dumps before new run
- Cleans previous Verilator builds
- Creates necessary directories
- No leftover temporary files

### ✓ Environment Management
- Auto-detects script directory
- Uses absolute paths (works from anywhere)
- Activates/deactivates venv cleanly
- Works with shell integration

---

## Execution Timeline

### Quick Test Run (with `--no-build --no-rtl`)
```
Verilator compilation:    ✓ SKIPPED
RTL simulation:           ✓ SKIPPED
Python comparison:        ⏱ 5 minutes
Image generation:         ⏱ 15-30 minutes
─────────────────────────────────
Total:                    ~20-35 minutes
```

### Standard Run (full)
```
Verilator compilation:    ⏱ 1-2 minutes
RTL simulation:           ⏱ 10-15 minutes
Python comparison:        ⏱ 3-5 minutes
Image generation:         ⏱ 15-30 minutes
─────────────────────────────────
Total:                    ~30-50 minutes
```

---

## How to Use the Script

### 1. First Run (Everything from Scratch)
```bash
./run_extended_comparison.sh
```
Let it run. Takes ~45 minutes, generates all files.

### 2. Rerun Comparison Only (Fastest)
```bash
./run_extended_comparison.sh --no-build --no-rtl
```
Takes ~20 minutes. Use this for tweaking parameters or re-running with different Python settings.

### 3. Rebuild RTL Binary Only
```bash
./run_extended_comparison.sh --no-rtl
```
Takes ~15 minutes. Use if you modified RTL source code.

### 4. Check if Existing Binary Works
```bash
./run_extended_comparison.sh --no-build
```
Takes ~25 minutes. Uses existing Verilator binary.

---

## After Comparison Completes

### 1. Review Images
```bash
# View key frames
open rtl_final_comparison_100k/comparison_00000.png    # Start
open rtl_final_comparison_100k/comparison_05000.png    # Middle
open rtl_final_comparison_100k/comparison_09999.png    # End

# Or use your image viewer to browse all
open rtl_final_comparison_100k/
```

### 2. Check Statistics
```bash
python3 << 'EOF'
import json
with open('rtl_final_comparison_100k/comparison_stats.json') as f:
    stats = json.load(f)
    for s in stats[::100]:  # Every 100 steps
        print(f"Step {s['step']:5d}: Python mean={s['python']['mean']:7.0f}, RTL mean={s['rtl']['mean']:7.0f}")
EOF
```

### 3. Analyze Trends
Look for:
- Trail intensity growing over time
- Agents forming interconnected networks
- Python and RTL showing similar patterns
- Mean pixel values converging

---

## Troubleshooting

### Issue: "Command not found: verilator"
```bash
sudo apt install verilator  # Ubuntu/Debian
brew install verilator      # macOS
```

### Issue: "Virtual environment not found"
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install numpy pillow scipy pygame cocotb
```

### Issue: Script hangs or takes too long
- **Normal**: Python simulation for 100k agents × 10k steps takes 3-5 minutes
- **Long image generation**: 1000 PNG files take 15-30 minutes to generate
- **Total expected**: 30-50 minutes for full run

### Issue: Out of disk space
You need ~5 GB:
- Check: `df -h`
- Delete old runs: `rm -rf rtl_final_comparison_100k rtl_trail_dumps`

### Issue: RTL simulation fails
```bash
# Check Verilator compilation
ls rtl/sim/obj_dir_slime_top/Vslime_top

# If missing, rebuild
./run_extended_comparison.sh  # Remove --no-build
```

---

## Customization

### Change Number of Steps
Edit `rtl/sim/slime_verilator_full_tb.cpp`:
```cpp
const int NUM_STEPS = 10000;    // Change to 5000, 20000, etc.
const int DUMP_INTERVAL = 10;   // Change to 5, 20, etc.
```
Then run: `./run_extended_comparison.sh`

### Change Python Seed
Edit `rtl_final_comparison.py`:
```python
seed=0xDEADBEEF    # Change to 0x12345678, etc.
```
Then run: `./run_extended_comparison.sh --no-build --no-rtl`

---

## Documentation Map

| File | Purpose | Read When |
|------|---------|-----------|
| **RUN_COMPARISON_QUICK_START.md** | Quick reference for script usage | First time using script |
| **EXTENDED_COMPARISON_GUIDE.md** | Detailed step-by-step guide | Want to understand each phase |
| **COMPARISON_ARCHITECTURE.md** | Technical deep-dive | Debugging mismatches or learning internals |
| **CLAUDE.md** | Project overview and architecture | Understanding overall system |
| **run_extended_comparison.sh** | Automation script | Running the comparison |

---

## Success Indicators

After `./run_extended_comparison.sh` completes successfully:

✓ **Directory created**: `rtl_final_comparison_100k/` exists
✓ **PNG files generated**: Shows ~1001 `.png` files
✓ **Statistics saved**: `comparison_stats.json` is valid
✓ **Color output**: Script prints colorized summary (green = success)
✓ **No errors**: Script exits with code 0
✓ **Disk space used**: ~5 GB total

You're ready to analyze the results!

---

## Summary

You now have a **complete, fully automated workflow** to:
1. Build RTL simulator (Verilator)
2. Run RTL simulation (10,000 steps)
3. Run Python reference (10,000 steps)
4. Generate 1,000 comparison images
5. Produce detailed statistics

All with one command: `./run_extended_comparison.sh`

The script handles all setup, error checking, and cleanup automatically.

Happy simulating! 🚀
