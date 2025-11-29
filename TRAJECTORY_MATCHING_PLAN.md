# Plan: Make RTL Agent Trajectories Match Python Exactly

## Current Problem

RTL agents differ from Python agents by:
- **X/Y Position:** ~3 pixels off (RTL ahead by 3 pixels)
- **Angle:** 0.01° difference (negligible)
- **Root cause:** Unknown - likely in movement/sensing/decision logic

## Goal

Make all agents have:
- `x_diff < 1 pixel`
- `y_diff < 1 pixel`
- `angle_diff < 0.1°`

Across **all 100 steps** of simulation.

## Investigation Strategy

### Phase 1: Capture Complete RTL Simulation Data

**Current Issue:** We only have RTL initialization data (step 0), not the actual RTL simulation steps 1-100.

**Action Required:**
1. Run the RTL simulation for 100 steps (same parameters as Python)
   - Resolution: 320×240
   - Agents: 100
   - Steps: 100
   - Seed: 0xDEADBEEF (same as Python)

2. Dump RTL agent state at **every step** (0-100)
   - Position (x, y) in fixed-point
   - Angle in fixed-point
   - Trail map state (optional but helpful)

3. Match exactly what Python does:
   - Same resolution
   - Same agent count
   - Same random seed
   - Same parameter values (move_speed, turn_speed, sensor_angle, sensor_distance, deposit_amount)

### Phase 2: Extract RTL Trajectory Data

Once we have 100 steps of RTL simulation:

1. Parse RTL dumps for each step (0-100)
2. Create CSV with format matching Python:
   ```
   step, agent_id, rtl_x, rtl_y, rtl_angle_deg, rtl_x_fp, rtl_y_fp, rtl_angle_fp
   ```

### Phase 3: Merge Python and RTL Trajectories

Create unified CSV with both:
```
step, agent_id,
python_x, python_y, python_angle_deg,
rtl_x, rtl_y, rtl_angle_deg,
x_diff, y_diff, angle_diff
```

### Phase 4: Analyze Differences

1. Calculate statistics for each step
2. Identify which step divergence occurs
3. Identify which agents diverge first
4. Look for patterns:
   - Linear drift (consistent offset)
   - Accelerating drift (error grows)
   - Sudden jumps (logic error)
   - Per-agent variations (specific agent bug)

### Phase 5: Debug Root Cause

Based on analysis, investigate:

**If position drifts linearly:**
- Movement calculation has systematic error
- Check: velocity magnitude, angle-to-velocity conversion
- Check: fixed-point arithmetic precision loss
- Check: coordinate wrapping logic

**If position jumps suddenly:**
- Sensory logic has discrete error
- Check: trail reading coordinates
- Check: sensory decision logic (F > L/R comparisons)
- Check: turn angle application

**If angle diverges:**
- Angle update logic differs
- Check: angle wrapping (modulo 2π)
- Check: turn speed sign (left vs right)
- Check: LFSR random bit interpretation

**If specific agents diverge:**
- Agent-specific bug (e.g., boundary condition)
- Check: agent ID masking
- Check: wrapping at canvas edges
- Check: initialization of specific agent types

## Implementation Steps

### Step 1: Modify RTL Testbench for State Dumps

**Location:** `/home/reson/SlimeSimulator/rtl/sim/slime_verilator_full_tb.cpp`

**Changes needed:**
1. Increase NUM_STEPS to 100 (currently 5)
2. Add method to dump agent state at every step:
   ```cpp
   void dump_agent_state(int step) {
       // For each agent (0-99):
       //   - Read x via debug_agent_idx=i, debug_agent_sel=0 → x_fp
       //   - Read y via debug_agent_idx=i, debug_agent_sel=1 → y_fp
       //   - Read angle via debug_agent_idx=i, debug_agent_sel=2 → angle_fp
       // Save to agent_state_step_XXXXX.json or CSV
   }
   ```
3. Call dump_agent_state() at end of each step (every NUM_AGENTS*30 cycles)
4. Use existing debug_agent_idx/debug_agent_sel signals (already in RTL)

**Rationale:**
- RTL already has debug interface for reading agent state
- Must capture actual RTL execution, not estimation
- Must match Python: 100 agents, 100 steps, same parameters

### Step 2: Run Modified RTL Simulation

**Command:**
```bash
cd rtl/sim
make -f Makefile.agent_init_validator clean
# Rebuild with NUM_STEPS=100 and state dump functionality
make -f Makefile.agent_init_validator
./obj_dir/slime_verilator_full
```

**Expected output:**
- `rtl_trail_dumps/` directory with 100 step dumps
- Agent state files: `agent_state_step_00000.json` through `agent_state_step_00099.json`
- Each file contains all 100 agents' (x, y, angle) at that step

### Step 3: Create Python Trajectory with 100 Steps

**Run existing Python simulator:**
```bash
source .venv/bin/activate
python3 slime_simulator.py \
  --width 320 --height 240 \
  --agents 100 --steps 100 \
  --dump-state /tmp/python_100step_state
```

**Output:** `/tmp/python_100step_state` containing final agent positions

**Critical:** Must use same seed (0xDEADBEEF) and parameters as RTL

### Step 4: Extract RTL State Dumps to CSV

**Create script:** `extract_rtl_trajectory.py`

**Logic:**
1. For each step (0-99):
   - Load `agent_state_step_XXXXX.json`
   - For each agent (0-99):
     - Extract x_fp, y_fp, angle_fp
     - Convert to pixels: x_px = x_fp >> 12, y_px = y_fp >> 12
     - Convert angle to degrees: angle_deg = (angle_fp / 4096.0) * 180 / π
     - Append to CSV row

**Output:** `rtl_trajectory_100steps.csv`

### Step 5: Create Python Trajectory CSV

**Create script:** `extract_python_trajectory.py`

**Logic:**
1. Load Python final state from step 100
2. For each agent, estimate positions at steps 0-99:
   - Step 0: Use initialization position from agent_coordinator.sv
   - Step N: Position = initial_position + movement * N
   - Movement direction from agent angle

**Alternative (Better):**
- Modify Python simulator to dump state at EVERY step (not just final)
- Use actual positions, not estimates

**Output:** `python_trajectory_100steps.csv`

### Step 6: Merge Python and RTL CSVs

**Create script:** `merge_trajectories.py`

**Logic:**
1. Load both CSV files
2. For each (step, agent_id):
   - Calculate x_diff, y_diff, angle_diff
   - Create combined row
3. Generate unified CSV

**Output:** `agent_trajectory_100steps_matched.csv`

**Format:**
```
step, agent_id,
python_x, python_y, python_angle_deg,
rtl_x, rtl_y, rtl_angle_deg,
x_diff, y_diff, angle_diff
```

### Step 7: Analyze Divergence

**Create analysis script:** `analyze_trajectory_divergence.py`

**Metrics to calculate:**
- Per-step statistics: mean/max/min x_diff, y_diff, angle_diff
- Per-agent statistics: total drift, final position error
- Divergence onset: which step does error first exceed threshold?
- Agent ordering: which agents diverge first?
- Error growth: linear, quadratic, exponential?

**Output:**
- Summary statistics to console
- Divergence graphs (save to PNG)
- Per-agent error heatmap

### Step 8: Visualize with Interactive Viewer

**Update:** `interactive_trajectory_viewer.py`

**New features:**
- Color agents by error magnitude (red=high error, green=low error)
- Show error magnitude in statistics panel
- Graph error over steps
- Highlight agents with >1px deviation

### Step 9: Debug Based on Findings

**Depending on divergence pattern:**

**If error is constant ~3 pixels:**
- Likely initialization or coordinate conversion issue
- Check: agent_coordinator.sv initialization
- Check: fp_to_pixel() function

**If error grows linearly:**
- Movement logic has systematic bias
- Check: move_speed application
- Check: angle-to-velocity conversion
- Check: sensor reading coordinates

**If error grows quadratically:**
- Cumulative rounding errors in fixed-point math
- Check: fixed_point_mult.sv precision
- Check: angle accumulation and wrapping

**If error jumps at specific step:**
- Logic error in that step's behavior
- Check: sensory decision logic
- Check: LFSR random bit generation
- Check: turn angle sign/magnitude

### Step 10: Implement Fixes

- Modify RTL based on root cause analysis
- Recompile and test
- Repeat steps 2-9 until differences < 1 pixel

## Success Metrics Per Step

```
Step 0:   x_diff < 0.1px, y_diff < 0.1px, angle_diff < 0.01°
Step 1:   x_diff < 0.5px, y_diff < 0.5px, angle_diff < 0.05°
Step 10:  x_diff < 1.0px, y_diff < 1.0px, angle_diff < 0.1°
Step 100: x_diff < 2.0px, y_diff < 2.0px, angle_diff < 0.2°
```

**Final target:** All steps have x_diff, y_diff < 1 pixel, angle_diff < 0.1°

## Expected Outcome

After implementing fixes:
- Step 0: x_diff=0, y_diff=0, angle_diff=0 (perfect initialization match)
- Steps 1-100: x_diff < 0.5px, y_diff < 0.5px, angle_diff < 0.05°

## Success Criteria

✅ All 100 agents × 100 steps have differences < 1 pixel in position and < 0.1° in angle
✅ Differences are randomly distributed, not systematic
✅ No agent diverges more than others (consistency across all agents)
✅ Visualization shows Python and RTL agents nearly overlapping

## Notes

- **Do NOT** subset data from wrong simulations
- **Must** run dedicated RTL 100-step simulation with 100 agents
- **Must** match parameters exactly (seed, resolution, agent count, physics params)
- **Must** extract ALL steps (0-100), not just initialization
- **Must** capture from actual RTL execution, not estimated positions
