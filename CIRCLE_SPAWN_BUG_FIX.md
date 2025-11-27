# Circle Spawn Bug Fix - Agent Angle Wrapping Issue

## Problem Description

RTL agent initialization created a circle where:
- **Top half (0° to 180°)**: Agents rendered correctly in a smooth arc
- **Bottom half (180° to 360°)**: Agents appeared broken into 3 disconnected pieces

## Root Cause

In `rtl/src/agent_coordinator.sv`, the agent initialization code calculated agent angles as:

```systemverilog
angle_fp = $rtoi(angle_rad * FP_SCALE) + pi_fp;  // Line 178
agent_angle[i] = angle_fp;                       // Line 179
```

For agents spawned in the bottom half of the circle (spawn angles from π to 2π), adding π to the spawn angle caused the result to **exceed 2π** (25735 in Q12.12 fixed-point):

- Agent 500 (spawn at π): angle = π + π = 2π ✓ (just at boundary)
- Agent 501 (spawn at π + ε): angle = π + π + ε = 2π + ε ✗ **(exceeds 2π!)**
- Agent 750 (spawn at 3π/2): angle = 3π/2 + π = 5π/2 ✗ **(exceeds 2π!)**
- Agent 999 (spawn at ~2π): angle = ~2π + π = ~3π ✗ **(exceeds 2π!)**

These unwrapped angles (> 2π) caused discontinuities in the simulation, leading to the visual appearance of 3 broken pieces instead of a continuous circle.

## The Fix

Added angle normalization to wrap all angles into the valid range [0, 2π):

```systemverilog
// CRITICAL FIX: Wrap angle to [0, 2π) to match Python behavior
spawn_angle_fp = $rtoi(angle_rad * FP_SCALE);
angle_fp = spawn_angle_fp + pi_fp;

// Normalize to [0, 2π) - essential for bottom half of circle
if (angle_fp >= two_pi_fp) begin
    angle_fp = angle_fp - two_pi_fp;
end

agent_angle[i] = angle_fp;
```

## Validation Results

With the fix applied:
- **Total agents tested**: 1000
- **Agents requiring wrapping**: 499 (49.9%) - all agents from index 501 to 999
- **All angles valid**: ✓ All angles now in range [0, 2π)
- **Circle continuity**: ✓ Agents form ONE continuous circle

### Before Fix (Examples)
| Agent | Spawn Angle | Agent Angle (raw) | Status |
|-------|-------------|-------------------|---------|
| 501   | 180.4°      | 25760 (6.289 rad) | ✗ Exceeds 2π |
| 750   | 270.0°      | 32168 (7.854 rad) | ✗ Exceeds 2π |
| 999   | 359.6°      | 38577 (9.418 rad) | ✗ Exceeds 2π |

### After Fix (Examples)
| Agent | Spawn Angle | Agent Angle (wrapped) | Status |
|-------|-------------|----------------------|---------|
| 501   | 180.4°      | 25 (0.006 rad)      | ✓ Valid |
| 750   | 270.0°      | 6433 (1.571 rad)    | ✓ Valid |
| 999   | 359.6°      | 12842 (3.135 rad)   | ✓ Valid |

## Impact

This fix ensures:
1. All agents have valid angles in [0, 2π)
2. The circle spawn pattern renders as a continuous circle
3. Agent behavior is consistent across all positions on the circle
4. No discontinuities in agent movement or trail deposition

## Related Files

- **Fixed file**: `/home/reson/SlimeSimulator/rtl/src/agent_coordinator.sv` (lines 145-191)
- **Test script**: `/home/reson/SlimeSimulator/test_circle_spawn_fix.py`

## Technical Details

- **Fixed-point representation**: Q12.12 format (4096 = 1.0)
- **2π in fixed-point**: 25735
- **π in fixed-point**: 12867
- **Wrapping boundary**: Agents 0-500 don't need wrapping, agents 501-999 do

The wrapping occurs precisely at agent 501, where spawn_angle + π first exceeds 2π.
