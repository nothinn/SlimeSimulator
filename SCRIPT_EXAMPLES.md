# Script Usage Examples

Quick copy-paste examples for common scenarios.

---

## Basic Usage

### Example 1: Default Configuration (800×600, 100k agents)
```bash
./run_extended_comparison.sh
```
**Time**: ~45-50 minutes
**Output**: `rtl_comparison_800x600_100000agents/`
**Use**: Standard full comparison

---

### Example 2: Quick Test (320×240, 1k agents)
```bash
./run_extended_comparison.sh --resolution 320x240 --agents 1000
```
**Time**: ~20-25 minutes
**Output**: `rtl_comparison_320x240_1000agents/`
**Use**: Quick verification, debugging

---

### Example 3: Medium Resolution (640×480, 50k agents)
```bash
./run_extended_comparison.sh --resolution 640x480 --agents 50000
```
**Time**: ~35-40 minutes
**Output**: `rtl_comparison_640x480_50000agents/`
**Use**: Balanced detail and performance

---

## Advanced Usage

### Example 4: Fast Iteration (Skip Compilation & RTL)
```bash
./run_extended_comparison.sh \
  --resolution 640x480 \
  --agents 50000 \
  --no-build \
  --no-rtl
```
**Time**: ~10-15 minutes (only Python + images)
**Use**: Testing different parameters quickly

---

### Example 5: Rebuild Binary with Different Config
```bash
./run_extended_comparison.sh \
  --resolution 512x512 \
  --agents 75000 \
  --no-rtl
```
**Time**: ~30-35 minutes (build + RTL + images)
**Use**: Recompile for new resolution/agents

---

### Example 6: Use Existing Binary
```bash
./run_extended_comparison.sh \
  --resolution 640x480 \
  --agents 60000 \
  --no-build
```
**Time**: ~20-25 minutes (skip compilation)
**Use**: Fast re-run with existing binary

---

### Example 7: Verbose Output
```bash
./run_extended_comparison.sh --verbose --resolution 320x240 --agents 1000
```
Shows detailed progress and debug output.

---

## Batch Testing

### Example 8: Test Multiple Resolutions
```bash
# QVGA
./run_extended_comparison.sh --resolution 320x240 --agents 1000

# VGA
./run_extended_comparison.sh --resolution 640x480 --agents 10000

# SVGA
./run_extended_comparison.sh --resolution 800x600 --agents 50000

# XGA
./run_extended_comparison.sh --resolution 1024x768 --agents 100000
```

Generates:
- `rtl_comparison_320x240_1000agents/`
- `rtl_comparison_640x480_10000agents/`
- `rtl_comparison_800x600_50000agents/`
- `rtl_comparison_1024x768_100000agents/`

---

### Example 9: Test Multiple Agent Counts
```bash
# Small
./run_extended_comparison.sh --agents 10000

# Medium
./run_extended_comparison.sh --agents 50000 --no-build --no-rtl

# Large
./run_extended_comparison.sh --agents 100000 --no-build --no-rtl

# Extra Large
./run_extended_comparison.sh --agents 200000 --no-build --no-rtl
```

Generates:
- `rtl_comparison_800x600_10000agents/`
- `rtl_comparison_800x600_50000agents/`
- `rtl_comparison_800x600_100000agents/`
- `rtl_comparison_800x600_200000agents/`

---

### Example 10: Comprehensive 2D Sweep
```bash
for agents in 1000 10000 50000 100000; do
  for res in 320x240 640x480 800x600; do
    echo "Running $res with $agents agents..."
    ./run_extended_comparison.sh --resolution $res --agents $agents --no-build --no-rtl
    echo "Done: $res/$agents"
    echo ""
  done
done
```

Generates 12 comparison directories with all combinations.

---

## Special Cases

### Example 11: Low-Resource Machine
```bash
./run_extended_comparison.sh --resolution 320x240 --agents 1000
```
**RAM**: <100 MB
**Time**: ~25 minutes
**Disk**: ~350 MB

---

### Example 12: High-Resolution Analysis
```bash
./run_extended_comparison.sh --resolution 1024x768 --agents 100000
```
**RAM**: ~1-2 GB
**Time**: ~60-70 minutes
**Disk**: ~5-7 GB

---

### Example 13: Debugging RTL Issues
```bash
./run_extended_comparison.sh --resolution 320x240 --agents 100 --verbose
```
**Time**: ~20 minutes
**Output**: Detailed progress with verbose output
**Use**: Troubleshooting RTL simulation

---

### Example 14: Compare Python vs RTL Quickly
```bash
# Skip all builds, just generate images from existing dumps
./run_extended_comparison.sh --no-build --no-rtl
```
**Time**: ~30-40 minutes (images only)
**Use**: Re-generate comparison images

---

## Monitor During Execution

### Example 15: Watch Progress in Separate Terminal
```bash
# Terminal 1: Run simulation
./run_extended_comparison.sh

# Terminal 2: Monitor (in /home/reson/SlimeSimulator)
watch -n 5 "ls -lh rtl_trail_dumps/*.bin 2>/dev/null | wc -l && \
             ls -lh rtl_final_comparison_100k/*.png 2>/dev/null | wc -l && \
             df -h | grep /home"
```

Shows:
- Number of RTL trail dumps generated
- Number of comparison images generated
- Remaining disk space

---

### Example 16: Monitor Memory & CPU
```bash
# Terminal 2 (separate): Monitor resources
watch -n 2 'echo "=== Memory ===" && free -h && echo "=== Disk ===" && du -sh rtl_trail_dumps rtl_final_comparison_100k 2>/dev/null'
```

---

## Real-World Workflows

### Workflow A: Validate New RTL Changes
```bash
# 1. Quick test with small config
./run_extended_comparison.sh --resolution 320x240 --agents 1000
# → Check images look correct

# 2. If good, try medium config
./run_extended_comparison.sh --resolution 640x480 --agents 50000 --no-build

# 3. If still good, run full test
./run_extended_comparison.sh --no-build --no-rtl
```

---

### Workflow B: Performance Comparison
```bash
# Test 3 different agent counts at same resolution
./run_extended_comparison.sh --agents 10000
./run_extended_comparison.sh --agents 50000 --no-build --no-rtl
./run_extended_comparison.sh --agents 100000 --no-build --no-rtl

# Compare results:
# - rtl_comparison_800x600_10000agents/comparison_stats.json
# - rtl_comparison_800x600_50000agents/comparison_stats.json
# - rtl_comparison_800x600_100000agents/comparison_stats.json
```

---

### Workflow C: Resolution Study
```bash
# Test 4 different resolutions at same agent count
./run_extended_comparison.sh --resolution 320x240
./run_extended_comparison.sh --resolution 640x480 --no-build --no-rtl
./run_extended_comparison.sh --resolution 800x600 --no-build --no-rtl
./run_extended_comparison.sh --resolution 1024x768 --no-build --no-rtl

# Analyze how resolution affects simulation behavior
```

---

### Workflow D: Continuous Testing
```bash
#!/bin/bash

# Run multiple configurations in sequence
configs=(
  "320x240:1000"
  "640x480:10000"
  "800x600:50000"
  "800x600:100000"
)

for config in "${configs[@]}"; do
  res=$(echo $config | cut -d: -f1)
  agents=$(echo $config | cut -d: -f2)

  echo "Running $res with $agents agents..."
  ./run_extended_comparison.sh --resolution $res --agents $agents --no-build --no-rtl

  echo "Completed: $res/$agents"
  echo ""
done

echo "All configurations complete!"
```

---

## Analyzing Results

### Example 17: View Specific Frames
```bash
# After run completes, view key frames
OUTPUT_DIR="rtl_comparison_800x600_100000agents"

# First frame (initial state)
open $OUTPUT_DIR/comparison_00000.png

# Middle frame (50% done)
open $OUTPUT_DIR/comparison_05000.png

# Last frame (final state)
open $OUTPUT_DIR/comparison_09999.png
```

---

### Example 18: Extract Statistics
```bash
OUTPUT_DIR="rtl_comparison_800x600_100000agents"

# Show Python trail intensity over time
python3 << 'EOF'
import json

with open('$OUTPUT_DIR/comparison_stats.json') as f:
    stats = json.load(f)

print("Step\tPython Mean\tRTL Mean\tDiff")
for s in stats[::100]:  # Every 100 steps
    py_mean = s['python']['mean']
    rtl_mean = s['rtl']['mean']
    diff = abs(py_mean - rtl_mean)
    print(f"{s['step']}\t{py_mean:.0f}\t\t{rtl_mean:.0f}\t\t{diff:.0f}")
EOF
```

---

### Example 19: Compare Two Runs
```bash
# Run with different agent counts
./run_extended_comparison.sh --agents 50000 --no-build --no-rtl
./run_extended_comparison.sh --agents 100000 --no-build --no-rtl

# Compare the statistics
python3 << 'EOF'
import json

with open('rtl_comparison_800x600_50000agents/comparison_stats.json') as f:
    stats_50k = json.load(f)

with open('rtl_comparison_800x600_100000agents/comparison_stats.json') as f:
    stats_100k = json.load(f)

# Find max trail intensity in each
max_50k = max(s['python']['max'] for s in stats_50k)
max_100k = max(s['python']['max'] for s in stats_100k)

print(f"Max trail with 50k agents: {max_50k}")
print(f"Max trail with 100k agents: {max_100k}")
print(f"Ratio: {max_100k / max_50k:.2f}x")
EOF
```

---

## Tips & Tricks

### Tip 1: Minimize Disk Usage
```bash
# Run comparison once, then delete trail dumps to save 1.4GB
./run_extended_comparison.sh
rm -rf rtl_trail_dumps
```

---

### Tip 2: Reuse Binary Across Runs
```bash
# Build once with first config
./run_extended_comparison.sh

# Reuse binary for other configs
./run_extended_comparison.sh --resolution 640x480 --agents 50000 --no-build
./run_extended_comparison.sh --resolution 512x512 --agents 75000 --no-build
./run_extended_comparison.sh --resolution 1024x768 --agents 100000 --no-build
```

---

### Tip 3: Background Execution
```bash
# Run in background, redirect to log file
nohup ./run_extended_comparison.sh --resolution 800x600 --agents 100000 > comparison.log 2>&1 &

# Monitor progress
tail -f comparison.log
```

---

### Tip 4: Check Progress
```bash
# In another terminal, count generated files
watch -n 5 "echo 'Dumps:' && ls rtl_trail_dumps/*.bin 2>/dev/null | wc -l && \
             echo 'Images:' && ls rtl_comparison_*/comparison_*.png 2>/dev/null | wc -l"
```

---

## Common Mistakes & Fixes

### Mistake 1: Wrong Resolution Format
```bash
# ❌ Wrong
./run_extended_comparison.sh --resolution 800 600

# ✓ Correct
./run_extended_comparison.sh --resolution 800x600
```

---

### Mistake 2: Floating Point Agents
```bash
# ❌ Wrong
./run_extended_comparison.sh --agents 50000.5

# ✓ Correct
./run_extended_comparison.sh --agents 50000
```

---

### Mistake 3: Mixing Old and New Configs
```bash
# If you get errors, make sure previous run finished
# Delete old output
rm -rf rtl_comparison_*/
rm -rf rtl_trail_dumps/

# Then restart fresh
./run_extended_comparison.sh --resolution 640x480 --agents 50000
```

---

## Summary

| Use Case | Command |
|----------|---------|
| Quick test | `./run_extended_comparison.sh --resolution 320x240 --agents 1000` |
| Standard run | `./run_extended_comparison.sh` |
| Fast iteration | `./run_extended_comparison.sh --resolution 640x480 --agents 50000 --no-build --no-rtl` |
| High detail | `./run_extended_comparison.sh --resolution 1024x768 --agents 100000` |
| Re-compare only | `./run_extended_comparison.sh --no-build --no-rtl` |
| Rebuild binary | `./run_extended_comparison.sh --resolution 512x512 --agents 75000 --no-rtl` |

---

For detailed parameter information, see `SCRIPT_CONFIGURATION_GUIDE.md`.
