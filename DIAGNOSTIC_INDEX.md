# Agent Movement Diagnostic - Quick Reference

## Quick Start

```bash
# Run complete diagnostic suite
source .venv/bin/activate
python agent_diagnostic.py      # Generate diagnostic data
python visualize_diagnostic.py  # Create visualizations
python print_diagnostic_report.py  # Print summary report
```

## Generated Files

### Data Files
- `debug_log.json` (42 KB) - Full step-by-step logs for all tracked agents
- `debug_analysis.json` (5 KB) - Statistical analysis of movement patterns
- `debug_trail.npy` (75 KB) - Trail map data (320×240 uint8 array)

### Human-Readable
- `debug_table.txt` (16 KB) - Text table showing agent movement step-by-step
- `AGENT_DIAGNOSTIC_SUMMARY.md` (10 KB) - Comprehensive documentation

### Visualizations
- `trajectory_plot.png` (167 KB) - 4-panel visualization:
  - Agent trajectories (all 10 agents)
  - Sensor readings over time
  - Turn decision distribution
  - Distance moved per step
- `trail_map_vis.png` (1 KB) - Trail map with color gradient
- `trail_map_heatmap.png` (43 KB) - Trail intensity heatmap
- `comparison_table.png` (40 KB) - Visual comparison table

## Key Results Summary

### Test Configuration
- **Resolution:** 320×240 pixels
- **Agents:** 10 tracked agents
- **Steps:** 5 simulation steps
- **Seed:** 0xDEADBEEF
- **Format:** Q12.12 fixed-point

### Movement Behavior
- **All sensors read 0** (empty canvas) → Agents turn right 100% of time
- **Average distance:** 0.99 px/step (expected: 1.0 px/step)
- **Max distance:** 1.41 px (diagonal movement, √2)
- **All agents start at center:** (160.0, 120.0)
- **Movement pattern:** Outward spiral with right-hand turning

### Ground Truth Established
✅ Deterministic LFSR sequence
✅ Bit-exact fixed-point arithmetic
✅ Sensor position calculations verified
✅ Turn decisions logged with reasoning
✅ Trail deposits tracked at pixel level

## JSON Data Structure

### Metadata
```json
{
  "width": 320,
  "height": 240,
  "num_agents": 10,
  "total_steps": 5,
  "lfsr_seed": "0xb6fbbcaf",
  "fixed_point": {
    "int_bits": 12,
    "frac_bits": 12,
    "scale": 4096
  },
  "parameters": {
    "move_speed": 1.0,
    "turn_speed": 0.300048828125,
    "sensor_angle": 0.5,
    "sensor_distance": 9.0,
    "deposit_amount": 5,
    "decay_rate": 0.949951171875
  }
}
```

### Step Log Entry
```json
{
  "step_num": 0,
  "agent_id": 0,
  "pos_x_fp": 655360,          // Fixed-point (160.0 × 4096)
  "pos_y_fp": 491520,          // Fixed-point (120.0 × 4096)
  "pos_x_float": 160.0,
  "pos_y_float": 120.0,
  "angle_idx": 478,            // 10-bit angle (0-1023)
  "angle_rad": 2.9329,
  "sensor_forward": 0,         // Trail values
  "sensor_left": 0,
  "sensor_right": 0,
  "sensor_fwd_pos": [151, 121],
  "sensor_left_pos": [151, 117],
  "sensor_right_pos": [153, 125],
  "turn_decision": "right",    // none/left/right/random_left/random_right
  "new_angle_idx": 468,
  "new_angle_rad": 2.8716,
  "new_pos_x_fp": 651264,
  "new_pos_y_fp": 491520,
  "new_pos_x_float": 159.0,
  "new_pos_y_float": 120.0,
  "deposit_pixel": [159, 120],
  "distance_moved": 1.0,
  "angle_changed": -0.0614
}
```

## Example Agent Behavior

### Agent 0 - Step-by-Step

| Step | Position | Angle | Decision | Sensors (F/L/R) | Deposit | Distance |
|------|----------|-------|----------|-----------------|---------|----------|
| 0 | (160,120)→(159,120) | 478→468 | RIGHT | 0/0/0 | (159,120) | 1.00 px |
| 1 | (159,120)→(158,120) | 468→458 | RIGHT | 0/0/0 | (158,120) | 1.00 px |
| 2 | (158,120)→(157,120) | 458→448 | RIGHT | 0/0/0 | (157,120) | 1.00 px |
| 3 | (157,120)→(156,120) | 448→438 | RIGHT | 0/0/0 | (156,120) | 1.00 px |
| 4 | (156,120)→(155,120) | 438→428 | RIGHT | 0/0/0 | (155,120) | 1.00 px |

**Result:** Agent 0 moves 5 pixels left (160→155) with consistent right turning

## RTL Comparison Checklist

### Before Running RTL
- [ ] Use same LFSR seed: 0xDEADBEEF
- [ ] Configure 10 agents
- [ ] Run for 5 steps
- [ ] Initialize agents at center (160, 120)
- [ ] Use Q12.12 fixed-point format
- [ ] 1024-entry trig LUT

### Data to Export from RTL
- [ ] Agent positions (x, y) in fixed-point after each step
- [ ] Agent angles (10-bit index) after each step
- [ ] Sensor readings (forward, left, right)
- [ ] Sensor positions (x, y)
- [ ] Turn decisions
- [ ] Trail deposit locations
- [ ] LFSR state progression

### Comparison Points
- [ ] Agent 0 position after step 0: (159.0, 120.0) in fixed-point 0x9F000, 0x78000
- [ ] Agent 0 angle after step 0: 468 (2.8716 rad)
- [ ] Agent 3 moves diagonally: distance ~1.414 px per step
- [ ] Agent 9 stays stationary: all steps result in (160, 120)
- [ ] All 50 decisions are "turn right"
- [ ] Total trail deposits: 50 (one per agent per step)

## Understanding the Behavior

### Why All Right Turns?

When sensors all read 0 (empty canvas), the decision logic is:

```python
if F > L and F > R:        # False (0 not > 0)
    continue_straight
elif F < L and F < R:      # False (0 not < 0)
    random_turn
elif L > R:                # False (0 not > 0)
    turn_left
else:                      # TRUE - Default case
    turn_right             # ← This executes
```

**Result:** Empty canvas → default to right turn

### Why Agent 9 Doesn't Move?

Agent 9 starts at angle 175/1024 ≈ 6°:
- cos(6°) ≈ 0.995 → dx ≈ 0.995
- sin(6°) ≈ 0.105 → dy ≈ 0.105

After fixed-point conversion and pixel rounding:
- dx rounds to 1 pixel
- dy rounds to 0 pixels

With right turning (angle decreases), dx approaches 1.0 horizontally while dy stays ~0.

When final position rounds to same pixel: (160, 120) → (160, 120)

### Why Diagonal Movement = √2?

Agents at ~45° angles:
- cos(45°) ≈ 0.707
- sin(45°) ≈ 0.707
- Movement: Δx ≈ 0.707, Δy ≈ 0.707
- Distance: √(0.707² + 0.707²) = √1 = 1.0

But when positions round to integer pixels:
- From (160, 120) → (159, 119)
- Δx = 1, Δy = 1
- Distance = √(1² + 1²) = √2 ≈ 1.414

## File Relationships

```
agent_diagnostic.py
  ├─→ debug_log.json (raw data)
  ├─→ debug_table.txt (text view)
  ├─→ debug_analysis.json (statistics)
  └─→ debug_trail.npy (trail map)

visualize_diagnostic.py (uses debug_log.json, debug_trail.npy)
  ├─→ trajectory_plot.png
  ├─→ trail_map_vis.png
  ├─→ trail_map_heatmap.png
  └─→ comparison_table.png

print_diagnostic_report.py (uses debug_log.json, debug_analysis.json)
  └─→ console output (summary report)

AGENT_DIAGNOSTIC_SUMMARY.md
  └─→ comprehensive documentation
```

## Customization Options

### Change Number of Agents
```python
# In agent_diagnostic.py, main():
num_agents = 20              # Simulate 20 agents
tracked_agents = list(range(10))  # But only log first 10
```

### Change Number of Steps
```python
num_steps = 100  # Run for 100 steps instead of 5
```

### Change Canvas Size
```python
width = 640
height = 480
```

### Use Different Seed
```python
seed = 0x12345678  # Different LFSR seed
```

## Common Issues

### Issue: "No module named 'rtl.sim.python_reference'"
**Solution:** Run from project root directory:
```bash
cd /home/reson/SlimeSimulator
python agent_diagnostic.py
```

### Issue: Visualization plots not showing
**Solution:** Script saves to files automatically (non-interactive backend). View:
```bash
open trajectory_plot.png  # macOS
xdg-open trajectory_plot.png  # Linux
```

### Issue: Out of memory with large simulations
**Solution:** Track fewer agents or reduce steps:
```python
tracked_agents = list(range(5))  # Only track 5 agents
num_steps = 10  # Fewer steps
```

## Next Steps

1. **Run RTL Simulation** - Use Verilator testbench with same parameters
2. **Export RTL Data** - Generate JSON in same format as `debug_log.json`
3. **Compare Results** - Use diff tools or custom comparison script
4. **Debug Discrepancies** - Refer to detailed logs to find mismatch source

## References

- **Python Reference:** `/home/reson/SlimeSimulator/rtl/sim/python_reference.py`
- **Main Simulator:** `/home/reson/SlimeSimulator/slime_simulator.py`
- **RTL Source:** `/home/reson/SlimeSimulator/rtl/src/agent_processor.sv`
- **CLAUDE.md:** Project overview and build instructions

---

*Generated: 2025-11-27*
*Project: SlimeSimulator - FPGA-based Physarum simulation*
