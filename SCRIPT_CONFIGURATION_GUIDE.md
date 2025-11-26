# Script Configuration Guide

## Parametrized Run Script

The `run_extended_comparison.sh` script now supports configurable resolution and agent count.

---

## Basic Usage

### Default (800×600, 100,000 agents)
```bash
./run_extended_comparison.sh
```

### Custom Resolution
```bash
./run_extended_comparison.sh --resolution 320x240
```

### Custom Agent Count
```bash
./run_extended_comparison.sh --agents 50000
```

### Both Custom
```bash
./run_extended_comparison.sh --resolution 640x480 --agents 75000
```

---

## Parameter Format

### `--resolution WIDTHxHEIGHT`
Specifies the simulation resolution.

**Format**: `WIDTHxHEIGHT` (lowercase 'x', no spaces)

**Examples**:
```bash
--resolution 320x240     # QVGA (small, fast)
--resolution 640x480     # VGA (medium)
--resolution 800x600     # Default (large)
--resolution 1024x768    # XGA (very large)
```

**Impact**:
- Memory: `resolution² × 4 bytes` for trail map
- Computation: `agents × resolution² / 1000` ops per step
- Storage: `resolution × resolution × 3 bytes` per dump

### `--agents NUM`
Specifies number of agents to simulate.

**Format**: Positive integer

**Examples**:
```bash
--agents 1000        # Small test (1 second per step)
--agents 10000       # Medium (10 seconds per step)
--agents 100000      # Default (100 seconds per 10k steps)
--agents 500000      # Large (requires 5-10GB memory)
```

**Impact**:
- Computation: Linear in number of agents
- Memory: ~75 bytes per agent (for agent state)
- Time: `num_agents × 10000 steps / 100M ops/sec`

---

## Optimization Presets

### Quick Test (fast, low resource)
```bash
./run_extended_comparison.sh --resolution 320x240 --agents 1000
```
**Time**: ~5-10 minutes total
**Disk**: ~100 MB
**Use case**: Verification, debugging

### Medium Simulation
```bash
./run_extended_comparison.sh --resolution 640x480 --agents 50000
```
**Time**: ~20-30 minutes
**Disk**: ~1.5 GB
**Use case**: Reasonable quality, moderate resources

### Standard (Default)
```bash
./run_extended_comparison.sh --resolution 800x600 --agents 100000
```
**Time**: ~30-50 minutes
**Disk**: ~5 GB
**Use case**: Full comparison, production quality

### High Resolution
```bash
./run_extended_comparison.sh --resolution 1024x768 --agents 100000
```
**Time**: ~45-60 minutes
**Disk**: ~8-10 GB
**Use case**: High-detail analysis

---

## Combined with Skip Options

### Test Configuration Quickly (Skip RTL simulation)
```bash
./run_extended_comparison.sh \
  --resolution 320x240 \
  --agents 1000 \
  --no-build \
  --no-rtl
```

### Use Existing Binary with Different Parameters
```bash
./run_extended_comparison.sh \
  --resolution 640x480 \
  --agents 75000 \
  --no-build
```

### Rebuild for Different Config (Skip Previous Dumps)
```bash
./run_extended_comparison.sh \
  --resolution 512x512 \
  --agents 50000 \
  --no-rtl
```

---

## Memory Requirements

### Trail Map Memory
```
Memory = WIDTH × HEIGHT × 4 bytes (uint32)

Examples:
  320×240:  307 KB
  640×480:  1.2 MB
  800×600:  1.9 MB
  1024×768: 3.1 MB
```

### Agent State Memory
```
Memory = num_agents × 75 bytes

Examples:
  1,000 agents:     75 KB
  10,000 agents:    750 KB
  50,000 agents:    3.8 MB
  100,000 agents:   7.6 MB
  500,000 agents:   38 MB
```

### Verilator Binary
```
Size = 30-50 MB (varies with compilation flags)
```

### Total RAM During Simulation
```
= Trail map + Agent state + Verilator runtime + OS overhead
  + image buffers + Python runtime

Examples:
  320×240, 1k agents:     ~100 MB
  640×480, 50k agents:    ~500 MB
  800×600, 100k agents:   ~1 GB
  1024×768, 500k agents:  ~3-5 GB
```

---

## Disk Space Requirements

### Trail Dumps
```
Size per dump = WIDTH × HEIGHT × 3 bytes
Number of dumps = 1,001 (every 10 steps for 10,000 steps)

Total = WIDTH × HEIGHT × 3 × 1001

Examples:
  320×240:   230 MB
  640×480:   920 MB
  800×600:   1.4 GB
  1024×768:  2.3 GB
```

### Comparison Images (PNG)
```
Size per image = WIDTH × HEIGHT × 3 bytes
Number of images = 1,001

Total ≈ WIDTH × HEIGHT × 3 × 1001 × 0.4  (compression ratio ~40%)

Examples:
  320×240:   100 MB
  640×480:   400 MB
  800×600:   600 MB
  1024×768:  1 GB
```

### Total Per Run
```
Examples:
  320×240, 1k agents:   ~350 MB
  640×480, 50k agents:  ~1.5 GB
  800×600, 100k agents: ~2-2.5 GB
  1024×768, 500k agents: ~3-4 GB
```

---

## Time Estimates

### Verilator Compilation
- **Small**: 1 minute
- **Medium**: 1-2 minutes
- **Large**: 2-3 minutes

### RTL Simulation (per 1000 steps)
```
Time ≈ (num_agents × 1000) / (200M ops/sec)

Examples:
  1,000 agents, 10k steps:    0.05 seconds (negligible)
  10,000 agents, 10k steps:   0.5 seconds
  50,000 agents, 10k steps:   2.5 seconds
  100,000 agents, 10k steps:  5-15 seconds (with I/O)
  500,000 agents, 10k steps:  25-60 seconds
```

### Python Simulation (per agent × step)
```
Time ≈ (num_agents × num_steps) / (1M ops/sec)

Examples:
  1,000 agents, 10k steps:    10 seconds
  10,000 agents, 10k steps:   100 seconds
  50,000 agents, 10k steps:   500 seconds (8 min)
  100,000 agents, 10k steps:  1000 seconds (15-20 min)
  500,000 agents, 10k steps:  5000+ seconds (1+ hour)
```

### Image Generation (per image)
```
Time ≈ 1-2 seconds per image (I/O bound)

Total for 1001 images:
  320×240:  20-30 min
  640×480:  30-40 min
  800×600:  30-40 min
  1024×768: 40-50 min
```

### Total Runtime Examples
```
320×240, 1k agents:
  Build: 1 min
  RTL: 1 min
  Python: 10 sec
  Images: 20 min
  Total: ~25-30 minutes

640×480, 50k agents:
  Build: 2 min
  RTL: 5 min
  Python: 5 min
  Images: 35 min
  Total: ~45-50 minutes

800×600, 100k agents:
  Build: 2 min
  RTL: 10 min
  Python: 15 min
  Images: 35 min
  Total: ~60-65 minutes

1024×768, 500k agents:
  Build: 3 min
  RTL: 30 min
  Python: 60 min
  Images: 45 min
  Total: ~140-150 minutes (2.5 hours)
```

---

## Output Directory Naming

Output directories are automatically named based on configuration:

```
rtl_comparison_WIDTHxHEIGHT_NUMagents/

Examples:
  ./run_extended_comparison.sh
  → rtl_comparison_800x600_100000agents/

  ./run_extended_comparison.sh --resolution 320x240 --agents 1000
  → rtl_comparison_320x240_1000agents/

  ./run_extended_comparison.sh --resolution 640x480 --agents 50000
  → rtl_comparison_640x480_50000agents/
```

---

## Parameter Validation

The script validates parameters:

### Invalid Resolution
```bash
./run_extended_comparison.sh --resolution 800 600
Error: Invalid resolution format: 600
Use format: WIDTHxHEIGHT (e.g., 800x600)

./run_extended_comparison.sh --resolution 800x600x2
Error: Invalid resolution format: 800x600x2
```

### Invalid Agent Count
```bash
./run_extended_comparison.sh --agents 50000.5
Error: Invalid agent count: 50000.5
Must be a positive integer

./run_extended_comparison.sh --agents -1000
Error: Invalid agent count: -1000
```

---

## Best Practices

### 1. Start Small for Testing
```bash
# First run: quick test
./run_extended_comparison.sh --resolution 320x240 --agents 1000

# Verify everything works before scaling up
```

### 2. Iterate on Configuration
```bash
# Skip expensive phases with --no-build --no-rtl
./run_extended_comparison.sh --resolution 640x480 --no-build --no-rtl

# Adjust parameters and re-run quickly
./run_extended_comparison.sh --resolution 800x600 --agents 75000 --no-build --no-rtl
```

### 3. Monitor Resources
```bash
# In another terminal, watch memory/disk
watch -n 1 'free -h && df -h /home'
```

### 4. Name Your Runs
```bash
# Each configuration gets unique output directory
./run_extended_comparison.sh --resolution 320x240 --agents 1000
  → rtl_comparison_320x240_1000agents/

./run_extended_comparison.sh --resolution 640x480 --agents 50000
  → rtl_comparison_640x480_50000agents/

# No accidental overwrites!
```

---

## Troubleshooting

### "Segmentation fault" during RTL simulation
- Likely cause: Configuration uses too much BRAM
- Fix: Reduce resolution or agent count
- Try: `--resolution 640x480 --agents 50000`

### Python simulation very slow (>1 hour)
- Likely cause: Too many agents
- Fix: Reduce with `--agents`
- Or use: `--no-build --no-rtl` on next run

### Out of memory
- Check available: `free -h`
- Reduce resolution or agents
- Try: `--resolution 320x240 --agents 10000`

### Compilation takes forever
- Large agent counts = more memory for compilation
- Normal behavior (be patient)
- Already compiled: Use `--no-build`

---

## Environment Variables

You can also set defaults via environment variables (for advanced users):

```bash
export COMPARISON_WIDTH=320
export COMPARISON_HEIGHT=240
export COMPARISON_AGENTS=1000

./run_extended_comparison.sh
# Uses env vars if present, command-line args override
```

(This feature is not yet implemented in the script, but can be added)

---

## Example Workflows

### Workflow 1: Quick Verification
```bash
# Test configuration quickly
./run_extended_comparison.sh --resolution 320x240 --agents 1000

# Takes ~30 min, generates rtl_comparison_320x240_1000agents/
```

### Workflow 2: Production Comparison
```bash
# Standard full comparison
./run_extended_comparison.sh

# Takes ~50 min, generates rtl_comparison_800x600_100000agents/
```

### Workflow 3: Multi-Scale Analysis
```bash
# Small
./run_extended_comparison.sh --resolution 320x240 --agents 1000

# Medium
./run_extended_comparison.sh --resolution 640x480 --agents 50000

# Large
./run_extended_comparison.sh --resolution 800x600 --agents 100000

# Generates three comparable datasets:
# - rtl_comparison_320x240_1000agents/
# - rtl_comparison_640x480_50000agents/
# - rtl_comparison_800x600_100000agents/
```

### Workflow 4: Fast Parameter Sweep
```bash
# Build once
./run_extended_comparison.sh --resolution 640x480 --agents 50000

# Re-run with different config, skip compilation and simulation
./run_extended_comparison.sh --resolution 640x480 --agents 60000 --no-build --no-rtl
./run_extended_comparison.sh --resolution 640x480 --agents 70000 --no-build --no-rtl
./run_extended_comparison.sh --resolution 640x480 --agents 80000 --no-build --no-rtl
```

---

## Summary

| Parameter | Default | Format | Impact |
|-----------|---------|--------|--------|
| `--resolution` | 800x600 | WIDTHxHEIGHT | Memory, disk, computation time |
| `--agents` | 100000 | Integer | Agent simulation time |
| `--no-build` | (off) | Flag | Skip Verilator compilation |
| `--no-rtl` | (off) | Flag | Skip RTL simulation phase |
| `--verbose` | (off) | Flag | Show detailed output |

---

## Quick Reference Card

```
╔════════════════════════════════════════════════════════════════╗
║              SCRIPT CONFIGURATION QUICK REFERENCE              ║
╠════════════════════════════════════════════════════════════════╣
║ Default (800×600, 100k agents)                                 ║
║   ./run_extended_comparison.sh                                 ║
║                                                                 ║
║ Quick Test (320×240, 1k agents)                                ║
║   ./run_extended_comparison.sh --resolution 320x240 --agents 1000 ║
║                                                                 ║
║ Custom Resolution                                              ║
║   ./run_extended_comparison.sh --resolution 640x480           ║
║                                                                 ║
║ Custom Agents                                                  ║
║   ./run_extended_comparison.sh --agents 50000                  ║
║                                                                 ║
║ Fast Iteration (skip build & RTL)                              ║
║   ./run_extended_comparison.sh --resolution 640x480 \          ║
║     --agents 50000 --no-build --no-rtl                         ║
║                                                                 ║
║ High Resolution                                                ║
║   ./run_extended_comparison.sh --resolution 1024x768           ║
║     --agents 100000                                            ║
╠════════════════════════════════════════════════════════════════╣
║ Output: rtl_comparison_WIDTHxHEIGHT_NUMagents/                 ║
║ Time: 25-150 minutes depending on parameters                   ║
║ Disk: 100 MB - 5 GB depending on parameters                    ║
╚════════════════════════════════════════════════════════════════╝
```
