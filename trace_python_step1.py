#!/usr/bin/env python3
"""Trace Python step 0->1 to understand expected behavior."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rtl', 'sim'))

from python_reference import (
    LFSR, FixedPoint, TrigLUT, SlimeSimulatorReference, SlimeAgent
)
import math
import json

# Create simulator
sim = SlimeSimulatorReference(
    width=320, height=240, num_agents=100,
    lfsr_seed=0xDEADBEEF
)

# Initialize agents on circle pattern (matching RTL testbench)
print("Initializing agents on circle pattern...")
center_x_fp = sim.fp.to_fixed(160)
center_y_fp = sim.fp.to_fixed(120)
radius_fp = sim.fp.to_fixed(48)

for i in range(sim.num_agents):
    angle_rad = 2.0 * math.pi * i / sim.num_agents
    x_float = 160 + 48 * math.cos(angle_rad)
    y_float = 120 + 48 * math.sin(angle_rad)

    x_fp = sim.fp.to_fixed(x_float)
    y_fp = sim.fp.to_fixed(y_float)

    # Angle pointing inward
    pointing_angle = angle_rad + math.pi
    angle_idx = int(round(pointing_angle * 1024 / (2 * math.pi))) & 0x3FF

    sim.agents.append(SlimeAgent(x_fp, y_fp, angle_idx, sim.fp))

# Get agent 0 step 0 state
agent0 = sim.agents[0]
print(f"\nAgent 0 at Step 0:")
print(f"  x: 0x{agent0.x:07X} = {sim.fp.from_fixed(agent0.x):.6f}")
print(f"  y: 0x{agent0.y:07X} = {sim.fp.from_fixed(agent0.y):.6f}")
print(f"  angle: 0x{agent0.angle:03X}")

# Manually trace update_agent for agent 0
print(f"\n--- TRACING update_agent(agent0) ---")

# Step 1: Sense
sense_forward = sim.sense(agent0, 0)
print(f"\nSense forward (offset=0):")
print(f"  trail value: {sense_forward}")

angle_offset = 81
sense_left = sim.sense(agent0, angle_offset)
print(f"Sense left (offset={angle_offset}):")
print(f"  trail value: {sense_left}")

sense_right = sim.sense(agent0, -angle_offset & 0x3FF)
print(f"Sense right (offset=-{angle_offset}):")
print(f"  trail value: {sense_right}")

# Step 2: Decision
turn_amount = 10
if sense_forward > sense_left and sense_forward > sense_right:
    print(f"\nDecision: F > L and F > R -> no change")
    new_angle = agent0.angle
elif sense_forward < sense_left and sense_forward < sense_right:
    print(f"\nDecision: F < L and F < R -> random turn")
    sim.lfsr.step()
    if sim.lfsr.state & 1:
        new_angle = (agent0.angle + turn_amount) & 0x3FF
    else:
        new_angle = (agent0.angle - turn_amount) & 0x3FF
elif sense_left > sense_right:
    print(f"\nDecision: L > R -> turn left")
    new_angle = (agent0.angle + turn_amount) & 0x3FF
else:
    print(f"\nDecision: R > L -> turn right")
    new_angle = (agent0.angle - turn_amount) & 0x3FF

print(f"  new_angle: 0x{new_angle:03X} (was 0x{agent0.angle:03X})")

# Step 3: Move
print(f"\nMovement calculation:")
sin_val = sim.trig.sin(new_angle)
cos_val = sim.trig.cos(new_angle)

print(f"  new_angle index: 0x{new_angle:03X}")
print(f"  sin lookup: 0x{sin_val:07X}")
print(f"  cos lookup: 0x{cos_val:07X}")

# Convert to signed
def to_signed_25bit(val):
    if val >= (1 << 24):
        return val - (1 << 25)
    return val

sin_val_signed = to_signed_25bit(sin_val)
cos_val_signed = to_signed_25bit(cos_val)

print(f"  sin signed: {sin_val_signed:+7d} = {sim.fp.from_fixed(sin_val_signed):.6f}")
print(f"  cos signed: {cos_val_signed:+7d} = {sim.fp.from_fixed(cos_val_signed):.6f}")

# Multiply by move_speed
dx = sim.fp.multiply(cos_val, sim.move_speed)
dy = sim.fp.multiply(sin_val, sim.move_speed)

dx_signed = to_signed_25bit(dx)
dy_signed = to_signed_25bit(dy)

print(f"\n  move_speed: 0x{sim.move_speed:07X} = {sim.fp.from_fixed(sim.move_speed):.6f}")
print(f"  dx = cos * speed: 0x{dx:07X} (signed: {dx_signed:+7d}) = {sim.fp.from_fixed(dx_signed):.6f}")
print(f"  dy = sin * speed: 0x{dy:07X} (signed: {dy_signed:+7d}) = {sim.fp.from_fixed(dy_signed):.6f}")

# Update position
new_x = (agent0.x + dx) & sim.fp.mask
new_y = (agent0.y + dy) & sim.fp.mask

print(f"\n  new_x = agent.x + dx = 0x{new_x:07X} = {sim.fp.from_fixed(new_x):.6f}")
print(f"  new_y = agent.y + dy = 0x{new_y:07X} = {sim.fp.from_fixed(new_y):.6f}")

# Step 4: Update agent in place
agent0.angle = new_angle
agent0.x = sim.fp.to_fixed(int(sim.fp.from_fixed(new_x)))
agent0.y = sim.fp.to_fixed(int(sim.fp.from_fixed(new_y)))

print(f"\nAgent 0 after update_agent():")
print(f"  x: 0x{agent0.x:07X} = {sim.fp.from_fixed(agent0.x):.6f}")
print(f"  y: 0x{agent0.y:07X} = {sim.fp.from_fixed(agent0.y):.6f}")
print(f"  angle: 0x{agent0.angle:03X}")

# Now do the full step and compare
print(f"\n--- RUNNING FULL STEP ---")
sim2 = SlimeSimulatorReference(width=320, height=240, num_agents=100, lfsr_seed=0xDEADBEEF)

# Same init
for i in range(sim2.num_agents):
    angle_rad = 2.0 * math.pi * i / sim2.num_agents
    x_float = 160 + 48 * math.cos(angle_rad)
    y_float = 120 + 48 * math.sin(angle_rad)
    x_fp = sim2.fp.to_fixed(x_float)
    y_fp = sim2.fp.to_fixed(y_float)
    pointing_angle = angle_rad + math.pi
    angle_idx = int(round(pointing_angle * 1024 / (2 * math.pi))) & 0x3FF
    sim2.agents.append(SlimeAgent(x_fp, y_fp, angle_idx, sim2.fp))

sim2.step()

agent0_after = sim2.agents[0]
print(f"Agent 0 after full step():")
print(f"  x: 0x{agent0_after.x:07X} = {sim2.fp.from_fixed(agent0_after.x):.6f}")
print(f"  y: 0x{agent0_after.y:07X} = {sim2.fp.from_fixed(agent0_after.y):.6f}")
print(f"  angle: 0x{agent0_after.angle:03X}")

# Save the state for comparison
output = {
    "step0": {
        "agent0": {
            "x_fp": agent0.x,
            "y_fp": agent0.y,
            "angle_idx": agent0.angle,
        }
    },
    "step1_expected": {
        "agent0": {
            "x_fp": agent0_after.x,
            "y_fp": agent0_after.y,
            "angle_idx": agent0_after.angle,
        }
    },
    "parameters": {
        "move_speed_fp": sim.move_speed,
        "move_speed_float": sim.fp.from_fixed(sim.move_speed),
        "sensor_distance_fp": sim.sensor_distance,
        "turn_speed_fp": sim.turn_speed,
    }
}

with open('python_step1_trace.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nTrace saved to python_step1_trace.json")
