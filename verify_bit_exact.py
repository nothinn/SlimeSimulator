#!/usr/bin/env python3
"""
Verify bit-exact compatibility between Python and RTL implementations.

This script checks:
1. Fixed-point arithmetic (multiplication)
2. Trig lookup tables (sin/cos values)
3. Agent initialization (step 0)
4. Agent step-1 calculation with detailed tracing
"""

import json
import struct
import sys
from pathlib import Path

from slime_simulator import LFSR, FixedPoint, TrigLUT, SlimeSimulatorReference, SlimeAgent
import math
import numpy as np


def load_rtl_hex_lut(filename):
    """Load a hex file from RTL."""
    values = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                # Parse as 25-bit value (sign-extend if negative)
                val = int(line, 16)
                if val >= (1 << 24):  # If bit 24 is set, it's negative in 25-bit
                    val = val - (1 << 25)
                values.append(val)
    return np.array(values, dtype=np.int32)


def verify_trig_luts():
    """Verify that Python and RTL trig LUTs are identical."""
    print("=" * 80)
    print("VERIFYING TRIG LOOKUP TABLES")
    print("=" * 80)

    # Load Python LUT
    fp = FixedPoint(12, 12)
    python_trig = TrigLUT(fp, table_bits=10)

    # Load RTL hex files
    sin_hex_file = 'rtl/src/sin_lut.hex'
    cos_hex_file = 'rtl/src/cos_lut.hex'

    rtl_sin = load_rtl_hex_lut(sin_hex_file)
    rtl_cos = load_rtl_hex_lut(cos_hex_file)

    # Compare
    sin_matches = True
    cos_matches = True

    for i in range(1024):
        python_sin = python_trig.sin(i)
        python_cos = python_trig.cos(i)

        # Sign-extend Python values for comparison
        if python_sin >= (1 << 24):
            python_sin = python_sin - (1 << 25)
        if python_cos >= (1 << 24):
            python_cos = python_cos - (1 << 25)

        if python_sin != rtl_sin[i]:
            if sin_matches:
                print(f"SIN MISMATCH at index {i}:")
                print(f"  Python: {python_sin:7d} (0x{python_sin & 0x1FFFFFF:07X})")
                print(f"  RTL:    {rtl_sin[i]:7d} (0x{rtl_sin[i] & 0x1FFFFFF:07X})")
                sin_matches = False

        if python_cos != rtl_cos[i]:
            if cos_matches:
                print(f"COS MISMATCH at index {i}:")
                print(f"  Python: {python_cos:7d} (0x{python_cos & 0x1FFFFFF:07X})")
                print(f"  RTL:    {rtl_cos[i]:7d} (0x{rtl_cos[i] & 0x1FFFFFF:07X})")
                cos_matches = False

    if sin_matches:
        print("✓ SIN LUT matches perfectly")
    if cos_matches:
        print("✓ COS LUT matches perfectly")

    return sin_matches and cos_matches


def verify_fixed_point():
    """Verify fixed-point multiplication."""
    print("\n" + "=" * 80)
    print("VERIFYING FIXED-POINT MULTIPLICATION")
    print("=" * 80)

    fp = FixedPoint(12, 12)

    # Test cases
    test_cases = [
        (1.0, 1.0),
        (0.5, 2.0),
        (0.707, 0.707),  # ~sqrt(2)/2
        (-1.0, 1.0),
        (1.5, 2.5),
        (0.001, 0.001),
    ]

    all_match = True
    for a_float, b_float in test_cases:
        a_fp = fp.to_fixed(a_float)
        b_fp = fp.to_fixed(b_float)
        result_fp = fp.multiply(a_fp, b_fp)
        result_float = fp.from_fixed(result_fp)
        expected_float = a_float * b_float

        error = abs(result_float - expected_float)
        match = error < 0.001  # Allow small rounding error

        symbol = "✓" if match else "✗"
        print(f"{symbol} {a_float:6.3f} * {b_float:6.3f} = {result_float:8.5f} "
              f"(expected {expected_float:8.5f}, error {error:.6f})")

        if not match:
            all_match = False
            print(f"  FP: 0x{a_fp:07X} * 0x{b_fp:07X} = 0x{result_fp:07X}")

    return all_match


def trace_agent_step_1():
    """Trace detailed calculation of first agent at step 1."""
    print("\n" + "=" * 80)
    print("TRACING AGENT STEP 1 CALCULATION (DETAILED)")
    print("=" * 80)

    # Create simulator with 100 agents, 320x240
    sim = SlimeSimulatorReference(
        width=320, height=240, num_agents=100,
        lfsr_seed=0xDEADBEEF
    )

    # Initialize agents on circle (matching RTL)
    print("\nInitializing 100 agents on circle pattern...")
    center_x_fp = sim.fp.to_fixed(160)  # 320/2
    center_y_fp = sim.fp.to_fixed(120)  # 240/2
    radius_fp = sim.fp.to_fixed(48)     # ~40% of 120

    for i in range(sim.num_agents):
        angle_rad = 2.0 * math.pi * i / sim.num_agents
        x_float = 160 + 48 * math.cos(angle_rad)
        y_float = 120 + 48 * math.sin(angle_rad)

        x_fp = sim.fp.to_fixed(x_float)
        y_fp = sim.fp.to_fixed(y_float)

        # Angle pointing inward (toward center)
        pointing_angle = angle_rad + math.pi
        angle_idx = int(round(pointing_angle * 1024 / (2 * math.pi))) & 0x3FF

        sim.agents.append(SlimeAgent(x_fp, y_fp, angle_idx, sim.fp))

    # Print first agent's initial state
    agent0 = sim.agents[0]
    print(f"\nAgent 0 (step 0):")
    print(f"  x:     0x{agent0.x:07X} = {sim.fp.from_fixed(agent0.x):.5f}")
    print(f"  y:     0x{agent0.y:07X} = {sim.fp.from_fixed(agent0.y):.5f}")
    print(f"  angle: 0x{agent0.angle:03X} ({agent0.angle})")

    # Trace step 1 calculation for agent 0
    print(f"\n--- STEP 1 CALCULATION FOR AGENT 0 ---")

    # 1. Sense forward
    print(f"\nSensing forward (angle offset = 0):")
    sensor_angle = (agent0.angle + 0) & 0x3FF
    sin_val = sim.trig.sin(sensor_angle)
    cos_val = sim.trig.cos(sensor_angle)
    print(f"  sensor_angle index: {sensor_angle}")
    print(f"  sin(angle):    0x{sin_val:07X}")
    print(f"  cos(angle):    0x{cos_val:07X}")

    # Convert to signed if needed
    if sin_val >= (1 << 24):
        sin_val_signed = sin_val - (1 << 25)
    else:
        sin_val_signed = sin_val
    if cos_val >= (1 << 24):
        cos_val_signed = cos_val - (1 << 25)
    else:
        cos_val_signed = cos_val

    print(f"  sin(angle) signed: {sin_val_signed:+7d} = {sim.fp.from_fixed(sin_val_signed):.5f}")
    print(f"  cos(angle) signed: {cos_val_signed:+7d} = {sim.fp.from_fixed(cos_val_signed):.5f}")

    # 2. Calculate sensor position
    print(f"\nCalculating sensor position:")
    print(f"  sensor_distance: 0x{sim.sensor_distance:07X} = {sim.fp.from_fixed(sim.sensor_distance):.5f}")

    dx = sim.fp.multiply(cos_val, sim.sensor_distance)
    dy = sim.fp.multiply(sin_val, sim.sensor_distance)

    if dx >= (1 << 24):
        dx_signed = dx - (1 << 25)
    else:
        dx_signed = dx
    if dy >= (1 << 24):
        dy_signed = dy - (1 << 25)
    else:
        dy_signed = dy

    print(f"  dx = cos * distance:")
    print(f"    0x{dx:07X} (signed: {dx_signed:+7d}) = {sim.fp.from_fixed(dx_signed):.5f}")
    print(f"  dy = sin * distance:")
    print(f"    0x{dy:07X} (signed: {dy_signed:+7d}) = {sim.fp.from_fixed(dy_signed):.5f}")

    sensor_x = (agent0.x + dx) & sim.fp.mask
    sensor_y = (agent0.y + dy) & sim.fp.mask

    print(f"  sensor_x = agent.x + dx = 0x{sensor_x:07X} = {sim.fp.from_fixed(sensor_x):.5f}")
    print(f"  sensor_y = agent.y + dy = 0x{sensor_y:07X} = {sim.fp.from_fixed(sensor_y):.5f}")

    px = int(sim.fp.from_fixed(sensor_x)) % 320
    py = int(sim.fp.from_fixed(sensor_y)) % 240

    print(f"  pixel_x: {px}, pixel_y: {py}")
    print(f"  trail value: {sim.trail_map[py, px]}")

    # 3. Move agent
    print(f"\nMoving agent forward:")
    print(f"  move_speed: 0x{sim.move_speed:07X} = {sim.fp.from_fixed(sim.move_speed):.5f}")

    dx_move = sim.fp.multiply(cos_val, sim.move_speed)
    dy_move = sim.fp.multiply(sin_val, sim.move_speed)

    if dx_move >= (1 << 24):
        dx_move_signed = dx_move - (1 << 25)
    else:
        dx_move_signed = dx_move
    if dy_move >= (1 << 24):
        dy_move_signed = dy_move - (1 << 25)
    else:
        dy_move_signed = dy_move

    print(f"  dx = cos * speed = 0x{dx_move:07X} (signed: {dx_move_signed:+7d}) = {sim.fp.from_fixed(dx_move_signed):.5f}")
    print(f"  dy = sin * speed = 0x{dy_move:07X} (signed: {dy_move_signed:+7d}) = {sim.fp.from_fixed(dy_move_signed):.5f}")

    new_x = (agent0.x + dx_move) & sim.fp.mask
    new_y = (agent0.y + dy_move) & sim.fp.mask

    print(f"  new_x = 0x{new_x:07X} = {sim.fp.from_fixed(new_x):.5f}")
    print(f"  new_y = 0x{new_y:07X} = {sim.fp.from_fixed(new_y):.5f}")

    new_px = int(sim.fp.from_fixed(new_x)) % 320
    new_py = int(sim.fp.from_fixed(new_y)) % 240

    print(f"  new pixel_x: {new_px}, new pixel_y: {new_py}")

    print(f"\nAgent 0 after step 1 (expected):")
    print(f"  x:     0x{new_x:07X} = {sim.fp.from_fixed(new_x):.5f}")
    print(f"  y:     0x{new_y:07X} = {sim.fp.from_fixed(new_y):.5f}")
    print(f"  angle: 0x{agent0.angle:03X} (unchanged, sensing forward)")

    return {
        'agent0_init_x': agent0.x,
        'agent0_init_y': agent0.y,
        'agent0_init_angle': agent0.angle,
        'step1_expected_x': new_x,
        'step1_expected_y': new_y,
        'sin_val': sin_val,
        'cos_val': cos_val,
        'move_speed': sim.move_speed,
    }


def main():
    """Run all verification tests."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  VERIFYING BIT-EXACT COMPATIBILITY".center(78) + "║")
    print("║" + "  Python Reference vs RTL Implementation".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")

    results = {}

    # Verify trig LUTs
    results['trig_luts'] = verify_trig_luts()

    # Verify fixed-point
    results['fixed_point'] = verify_fixed_point()

    # Trace step 1
    results['step_1'] = trace_agent_step_1()

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    if results['trig_luts']:
        print("✓ Trig LUTs match")
    else:
        print("✗ Trig LUT mismatch found")

    if results['fixed_point']:
        print("✓ Fixed-point arithmetic verified")
    else:
        print("✗ Fixed-point arithmetic issues found")

    print("\nStep 1 trace data saved. Compare agent positions against RTL dump.")

    # Save results for comparison with RTL
    with open('python_bit_exact_results.json', 'w') as f:
        json.dump({
            'trig_luts_match': results['trig_luts'],
            'fixed_point_ok': results['fixed_point'],
            'step1_trace': {
                'agent0_init_x': hex(results['step_1']['agent0_init_x']),
                'agent0_init_y': hex(results['step_1']['agent0_init_y']),
                'agent0_init_angle': hex(results['step_1']['agent0_init_angle']),
                'step1_expected_x': hex(results['step_1']['step1_expected_x']),
                'step1_expected_y': hex(results['step_1']['step1_expected_y']),
                'sin_val': hex(results['step_1']['sin_val']),
                'cos_val': hex(results['step_1']['cos_val']),
                'move_speed': hex(results['step_1']['move_speed']),
            }
        }, f, indent=2)

    print("\nResults saved to python_bit_exact_results.json")


if __name__ == '__main__':
    main()
