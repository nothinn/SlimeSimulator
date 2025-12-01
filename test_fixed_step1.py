#!/usr/bin/env python3
"""Test fixed Python slime_simulator vs RTL step 1 movement."""

import sys
import math
from slime_simulator import SlimeSimulator, SimulationConfig

# Configuration matching regression tests
width = 320
height = 240
num_agents = 100
num_steps = 1

print("Creating fixed Python simulator...")
cfg = SimulationConfig(
    width=width,
    height=height,
    num_agents=num_agents,
    num_steps=num_steps,
    move_speed=1.0,
    turn_speed=0.3,
    sensor_angle=0.5,
    sensor_distance=9.0,
    seed=0xDEADBEEF,
)

sim = SlimeSimulator(cfg)

# Get step 0 state
print("\nAgent 0 at step 0:")
print(f"  x_fp: {int(sim.x[0]):10d} = 0x{int(sim.x[0]):07X} = {int(sim.x[0])/4096:.6f} pixels")
print(f"  y_fp: {int(sim.y[0]):10d} = 0x{int(sim.y[0]):07X} = {int(sim.y[0])/4096:.6f} pixels")
print(f"  angle: {int(sim.angles[0]):4d} = 0x{int(sim.angles[0]):03X}")

x0_step0 = int(sim.x[0])
y0_step0 = int(sim.y[0])

# Run one step
sim.step()

print("\nAgent 0 at step 1 (after fix):")
print(f"  x_fp: {int(sim.x[0]):10d} = 0x{int(sim.x[0]):07X} = {int(sim.x[0])/4096:.6f} pixels")
print(f"  y_fp: {int(sim.y[0]):10d} = 0x{int(sim.y[0]):07X} = {int(sim.y[0])/4096:.6f} pixels")
print(f"  angle: {int(sim.angles[0]):4d} = 0x{int(sim.angles[0]):03X}")

x0_step1 = int(sim.x[0])
y0_step1 = int(sim.y[0])

# Calculate deltas
dx_fp = x0_step1 - x0_step0
dy_fp = y0_step1 - y0_step0

print(f"\nMovement:")
print(f"  dx_fp: {dx_fp:10d} = {dx_fp/4096:+.6f} pixels")
print(f"  dy_fp: {dy_fp:10d} = {dy_fp/4096:+.6f} pixels")

# Expected from regression test
print(f"\nExpected movement (from Python dump in regression test):")
print(f"  dx_fp: -4096 = -1.0 pixels")
print(f"  dy_fp: ~25 = ~0.006 pixels")

if abs(dx_fp - (-4096)) < 100:  # Allow some rounding
    print(f"\n✓ X movement CORRECT (got {dx_fp/4096:.6f}, expected -1.0)")
else:
    print(f"\n✗ X movement WRONG (got {dx_fp/4096:.6f}, expected -1.0)")

print(f"\nExpected from RTL (before fix):")
print(f"  dx_fp: -8192 = -2.0 pixels")

if abs(dx_fp - (-8192)) < 100:
    print(f"⚠ X movement still shows 2x error - fix not working!")
else:
    print(f"✓ X movement no longer shows 2x error - fix is working!")
