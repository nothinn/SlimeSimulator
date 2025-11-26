# Extended Comparison Guide: RTL vs Python (10× Extended)

## Overview

This guide explains how to run an extended RTL vs Python comparison with:
- **10× longer simulation**: 10,000 steps (vs 1,000 original)
- **10× more images**: Every 10 steps (vs every 100 steps)
- **1,000 comparison frames** generated at full 800×600 resolution

## What It Takes to Compare Python vs RTL

### 1. **Python Reference Model**
The Python reference (`slime_simulator.py`) provides the "golden standard":
- **Bit-exact fixed-point arithmetic**: Q12.12 format (12 integer + 12 fractional bits)
- **RTL-compatible LFSR**: 32-bit maximal-length LFSR with identical tap sequences
- **Identical algorithm**: Same sensory logic, decision-making, and trail physics

**Key files**:
- `slime_simulator.py` - Main simulation (850 LOC)
- `rtl/sim/python_reference.py` - Verification model with bit-exact arithmetic

### 2. **RTL Simulation (Verilator)**
SystemVerilog hardware design compiled to C++ then native binary:
- Emulates 19-stage pipelined agent processor
- Processes 100,000 agents at 800×600 resolution
- Dumps trail maps as binary files (`trail_step_XXXXX.bin`)

**Key files**:
- `rtl/sim/slime_verilator_full_tb.cpp` - Testbench (modified for 10× run)
- `rtl/src/slime_top.sv` - Top-level RTL design
- `rtl_trail_dumps/` - Output directory for trail snapshots

### 3. **Comparison Pipeline**
The comparison script:
1. Runs Python simulation for full 10,000 steps
2. Loads RTL trail dumps at matching steps
3. Computes statistics (min/max/mean for each)
4. Generates side-by-side heat-mapped images
5. Calculates pixel-level differences

**Key file**:
- `rtl_final_comparison.py` - Comparison generator (modified for 10× run)

---

## Step-by-Step Instructions

### Phase 1: Build Verilator Binary (1-2 minutes)

```bash
cd rtl/sim

# Clean previous build
rm -rf obj_dir obj_dir_full

# Compile with Verilator
verilator -cc -std c++14 --trace \
  -I../src \
  --top-module slime_top \
  -o slime_verilator_full \
  ../src/slime_top.sv ../src/*.sv

# Build executable
cd obj_dir_slime_top
make -f Vslime_top.mk

cd ../..
```

**Expected output**: `obj_dir_slime_top/Vslime_top` executable (~30-50 MB)

### Phase 2: Run Extended RTL Simulation (8-15 minutes)

```bash
cd rtl/sim

# Clean old trail dumps
rm -rf ../../rtl_trail_dumps
mkdir -p ../../rtl_trail_dumps

# Run simulation (10,000 steps with dumps every 10 steps = 1,000 dumps)
./obj_dir_slime_top/Vslime_top

# Verify output
ls -lh ../../rtl_trail_dumps/*.bin | wc -l
# Should show ~1001 files (steps 0, 10, 20, ..., 9990, 9999)
```

**What it does**:
- Initializes 100,000 agents in circle spawn pattern
- Processes each step through pipelined agent processor
- Applies trail decay (0.95 rate)
- Dumps trail map every 10 steps as 3-byte 18-bit values
- Shows progress: `Progress: 100%`

**Time estimate**:
- ~100k agents × 10k steps = 1 billion operations
- Modern CPU: ~100 million ops/sec → ~10-15 seconds
- With I/O dumps: ~30-60 seconds expected

### Phase 3: Generate Comparison Images (3-5 minutes)

```bash
cd /home/reson/SlimeSimulator

# Activate Python environment
source .venv/bin/activate

# Run comparison
python rtl_final_comparison.py

# Wait for completion (~1000 frames to generate)
# Expected: Creates rtl_final_comparison_100k/ directory
```

**What it does**:
1. Loads Python simulator configuration (100k agents, 10k steps)
2. Runs Python reference model to completion (100k steps)
3. At each comparison step (every 10 steps):
   - Loads corresponding RTL trail dump
   - Compares statistics (min/max/mean)
   - Generates heat-mapped side-by-side PNG image
   - Logs differences

**Output files**:
```
rtl_final_comparison_100k/
├── comparison_00000.png      # Step 0
├── comparison_00010.png      # Step 10
├── comparison_00020.png      # Step 20
├── ...
├── comparison_09990.png      # Step 9990
├── comparison_09999.png      # Step 9999
└── comparison_stats.json     # Summary statistics
```

---

## Understanding the Comparison Output

### Heat Map Color Scheme
The trail intensity maps to colors:
- **Black**: No trail (0)
- **Blue**: Weak trail (1-64)
- **Cyan**: Medium trail (64-128)
- **Green**: Strong trail (128-192)
- **Yellow/Red**: Very strong trail (192-262143)

### Statistics Columns

**Left side (Python Reference)**:
```
Python: min=0 max=21743 mean=8234
```
- Min: Minimum trail value in frame
- Max: Peak trail concentration
- Mean: Average trail across entire map

**Right side (RTL Simulation)**:
```
RTL: min=0 max=18921 mean=7856
```
- Same metrics as Python but from RTL simulation

### Comparison Metrics
```
Diff: max=2822 mean=378.1 match=98.3%
```
- `max`: Largest pixel difference
- `mean`: Average pixel difference
- `match`: Percentage match to Python reference

---

## Key Parameters Modified for 10× Extension

| Parameter | Original | Extended | File |
|-----------|----------|----------|------|
| Simulation Steps | 1,000 | 10,000 | `slime_verilator_full_tb.cpp:17` |
| Dump Interval | Every 100 steps | Every 10 steps | `slime_verilator_full_tb.cpp:18` |
| Comparison Steps | ~100 frames | ~1,000 frames | `rtl_final_comparison.py:174` |
| Total Frames | ~11 | ~1,001 | Output directory |

---

## Troubleshooting

### Issue: "RTL trail not found" errors
**Symptom**: Many `[SKIP]` messages during comparison
**Cause**: RTL simulation didn't generate trail dumps
**Fix**:
1. Verify `rtl_trail_dumps/` directory exists
2. Check Verilator build succeeded: `ls obj_dir_slime_top/Vslime_top`
3. Re-run RTL simulation

### Issue: Comparison takes very long
**Symptom**: Python simulation phase hangs or progresses very slowly
**Cause**: 100k agents × 10k steps is computationally intensive
**Solution**:
- Let it run (may take 2-3 minutes for Python alone)
- Or reduce `num_steps` in script to 1000 for testing

### Issue: Memory errors during comparison
**Cause**: 800×600 × 10000 frames × memory overhead
**Solution**: Run comparison in smaller batches or reduce resolution

### Issue: Images look identical (Python == RTL)
**Reason**: This is actually correct! Both Python and RTL use:
- Same LFSR implementation (bit-exact)
- Same fixed-point arithmetic (Q12.12)
- Same algorithm
- Therefore, they should match

The real test is whether the behavior matches the *expected* slime mold behavior (circular spread pattern, network formation, etc.)

---

## Performance Expectations

### RTL Simulation Phase
- **100k agents** × **10k steps** = 1 billion agent-step operations
- **Verilator throughput**: ~100M-200M ops/sec (modern CPU)
- **Expected time**: 5-15 seconds (plus I/O overhead for dumps)
- **Storage**: ~1,001 dumps × 1.44 MB = ~1.4 GB

### Python Comparison Phase
- **100k agents** × **10k steps**: ~3-5 minutes on modern CPU
- **Image generation**: ~1 second per frame × 1,000 = ~1000 seconds (parallel I/O helps)
- **Total expected**: 5-10 minutes for comparison

### Disk Requirements
```
RTL trail dumps:  ~1.4 GB
PNG comparison:   ~3-5 GB (1000 × 1.2×800×600 RGB)
Python temp:      <100 MB
Total:            ~5 GB available recommended
```

---

## Advanced Options

### Run with Different Seed
Modify in `rtl_final_comparison.py`:
```python
seed=0xDEADBEEF  # Change to any 32-bit value
```

### Different Resolution
Not recommended (would require RTL rebuild), but possible:
- Modify `WIDTH` and `HEIGHT` in `slime_verilator_full_tb.cpp`
- Rebuild Verilator binary
- Adjust Python resolution in `rtl_final_comparison.py`

### Shorter Test Run
Quick 100-step test for debugging:
```python
# In rtl_final_comparison.py
num_steps=100,           # Change from 10000
num_agents=100,          # Reduce to 100 for faster testing
```

---

## Quality Metrics to Monitor

### Excellent Agreement (Expected)
```
- match > 95%
- mean_diff < 500 trail units
- Both show clear circular spread pattern
- Both develop interconnected agent networks
```

### Good Agreement
```
- match > 90%
- mean_diff < 1000 trail units
- Visual patterns similar, some pixel-level differences
```

### Problem Indicators
```
- match < 80%
- RTL shows only a dot while Python shows networks
- Max diff > 262143 (18-bit saturation)
- RTL trail stays at 0 (agent deposition not working)
```

---

## Files Modified for 10× Extension

1. **rtl/sim/slime_verilator_full_tb.cpp**
   - Line 17: `NUM_STEPS = 10000` (was 1000)
   - Line 18: `DUMP_INTERVAL = 10` (was 100)

2. **rtl_final_comparison.py**
   - Line 147: `num_steps=10000` (was 10000, already correct)
   - Line 161: Display text "10,000" (was 1,000)
   - Line 195: Progress format updated

These changes enable the extended 10,000-step comparison with dumps every 10 steps.

---

## Next Steps After Comparison

1. **Analyze images**: Browse `rtl_final_comparison_100k/comparison_*.png`
2. **Review statistics**: Check `comparison_stats.json` for convergence patterns
3. **Look for patterns**:
   - Do agents form networks?
   - Does trail intensity grow over time?
   - Any unexpected artifacts?
4. **Debug if needed**: Compare specific frames with Python reference

---

## Summary Table

| Component | Time | Output | Size |
|-----------|------|--------|------|
| Verilator build | 1-2 min | Binary executable | ~50 MB |
| RTL simulation | 10-15 min | 1,001 trail dumps | ~1.4 GB |
| Python reference | 3-5 min | Trail map (in memory) | N/A |
| Image generation | 15-30 min | 1,001 PNG images | ~3-5 GB |
| **Total time** | **30-50 min** | All output files | ~5 GB |

---

## References

- **CLAUDE.md**: Project architecture and design parameters
- **slime_simulator.py**: Python reference implementation
- **rtl/sim/slime_verilator_full_tb.cpp**: RTL testbench
- **rtl/src/slime_top.sv**: Top-level RTL design
