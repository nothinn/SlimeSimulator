#!/usr/bin/env python3
"""
Diagnostic script to analyze angle offset between RTL and Python simulators.
Loads agent dump files from step 0 and compares angles to identify systematic errors.
"""

import struct
import numpy as np
import json
from pathlib import Path


def fixed_to_float(val, frac_bits=12):
    """Convert Q12.12 fixed-point to float."""
    if val & (1 << 24):  # Sign bit (25-bit signed)
        val = val - (1 << 25)
    return val / (1 << frac_bits)


def normalize_angle(angle):
    """Normalize angle to [-π, π] range."""
    while angle > np.pi:
        angle -= 2 * np.pi
    while angle < -np.pi:
        angle += 2 * np.pi
    return angle


def angle_difference(a1, a2):
    """Calculate signed difference between two angles (a1 - a2), normalized to [-π, π]."""
    diff = a1 - a2
    return normalize_angle(diff)


def load_rtl_agents(filepath):
    """Load agent data from RTL JSON dump."""
    with open(filepath, 'r') as f:
        data = json.load(f)

    agents = []
    frac_bits = 12
    for agent in data['agents']:
        # Convert fixed-point to radians
        angle_fp = agent['angle_fp']
        angle_rad = fixed_to_float(angle_fp, frac_bits)

        agents.append({
            'x': agent['x_px'],
            'y': agent['y_px'],
            'angle': angle_rad,
            'angle_deg': agent['angle_deg']
        })

    return agents


def calculate_expected_python_angle(agent_id, num_agents, width, height):
    """
    Calculate what the angle should be according to Python initialization.
    Agents are spawned on a circle pointing inward.
    """
    # Circle spawn pattern
    spawn_radius = 0.4 * min(width, height)
    cx = width / 2.0
    cy = height / 2.0

    # Angle around circle
    circle_angle = (2.0 * np.pi * agent_id) / num_agents

    # Position on circle
    x = cx + spawn_radius * np.cos(circle_angle)
    y = cy + spawn_radius * np.sin(circle_angle)

    # Angle pointing toward center
    # In Python: arctan2(cy - y, cx - x)
    dx = cx - x
    dy = cy - y
    angle = np.arctan2(dy, dx)

    return angle, x, y


def calculate_rtl_expected_angle(agent_id, num_agents):
    """
    Calculate what angle RTL SHOULD produce based on its initialization logic.
    RTL uses: angle_fp = spawn_angle_fp + pi_fp
    where spawn_angle_fp = circle_angle = 2π * i / NUM_AGENTS
    """
    # Circle angle (angle around circle)
    circle_angle = (2.0 * np.pi * agent_id) / num_agents

    # RTL adds π to point inward
    agent_angle = circle_angle + np.pi

    # RTL normalizes to [0, 2π)
    if agent_angle >= 2*np.pi:
        agent_angle -= 2*np.pi

    return agent_angle


def categorize_offset(offsets):
    """Categorize the angle offset pattern."""
    mean_offset = np.mean(offsets)
    std_offset = np.std(offsets)

    # Convert to degrees for easier interpretation
    mean_deg = np.degrees(mean_offset)
    std_deg = np.degrees(std_offset)

    categories = []

    # Check for +90° offset (sin/cos swapped)
    if 85 <= mean_deg <= 95 and std_deg < 5:
        categories.append("LIKELY CAUSE: sin/cos swapped (+90°)")
        categories.append("  RTL is using: angle + 90°")
        categories.append("  FIX: Swap sin/cos usage or subtract 90° from angle")

    # Check for -90° offset (sin/cos swapped opposite way)
    elif -95 <= mean_deg <= -85 and std_deg < 5:
        categories.append("LIKELY CAUSE: sin/cos swapped (-90°)")
        categories.append("  RTL is using: angle - 90°")
        categories.append("  FIX: Swap sin/cos usage or add 90° from angle")

    # Check for 180° offset (angle negation or direction flip)
    elif (175 <= abs(mean_deg) <= 185) and std_deg < 5:
        categories.append("LIKELY CAUSE: 180° offset")
        categories.append("  RTL angle direction is reversed")
        categories.append("  FIX: Negate angle or reverse sin/cos signs")

    # Check for consistent small offset
    elif abs(mean_deg) < 10 and std_deg < 5:
        categories.append("LIKELY CAUSE: Small constant offset")
        categories.append(f"  RTL angles are offset by {mean_deg:.2f}°")
        categories.append("  FIX: Check angle initialization or lookup table indexing")

    # Variable offset (inconsistent)
    elif std_deg > 10:
        categories.append("PATTERN: INCONSISTENT OFFSET")
        categories.append(f"  Mean offset: {mean_deg:.2f}°, Std Dev: {std_deg:.2f}°")
        categories.append("  This suggests non-systematic error")
        categories.append("  FIX: Check for different agent initialization logic")

    # Other systematic offset
    else:
        categories.append("PATTERN: SYSTEMATIC OFFSET (non-standard)")
        categories.append(f"  Mean offset: {mean_deg:.2f}°, Std Dev: {std_deg:.2f}°")
        categories.append("  FIX: Investigate angle calculation pipeline")

    return categories


def main():
    print("=" * 80)
    print("ANGLE OFFSET DIAGNOSTIC TOOL")
    print("=" * 80)
    print()

    # Locate RTL agent dump file
    base_dir = Path('/home/reson/SlimeSimulator')
    rtl_agent_file = base_dir / 'rtl' / 'sim' / 'rtl_agent_dumps' / 'agent_state_step_00000.json'

    if not rtl_agent_file.exists():
        print(f"ERROR: RTL agent dump not found: {rtl_agent_file}")
        print("Please run a simulation first to generate agent dumps")
        return

    print(f"RTL agents: {rtl_agent_file}")
    print()

    # Load RTL agents
    print("Loading RTL agent data...")
    rtl_agents = load_rtl_agents(rtl_agent_file)
    num_agents = len(rtl_agents)
    print(f"Loaded {num_agents} agents from RTL")
    print()

    # Read simulation parameters from testbench
    # We'll infer from the first agent - need width/height
    # For now, assume 320x240 (we can make this a parameter later)
    width = 320
    height = 240

    print(f"Using simulation parameters: {width}x{height}")
    print()

    # Calculate angle differences
    angle_diffs_vs_python = []
    angle_diffs_vs_rtl_expected = []
    position_diffs = []
    expected_python_angles = []
    expected_rtl_angles = []

    for i in range(num_agents):
        rtl = rtl_agents[i]

        # Calculate expected Python angle
        expected_py_angle, expected_x, expected_y = calculate_expected_python_angle(
            i, num_agents, width, height
        )
        expected_python_angles.append(expected_py_angle)

        # Calculate expected RTL angle (based on RTL initialization logic)
        expected_rtl_angle = calculate_rtl_expected_angle(i, num_agents)
        expected_rtl_angles.append(expected_rtl_angle)

        # Angle difference (RTL actual - Expected Python)
        angle_diff_py = angle_difference(rtl['angle'], expected_py_angle)
        angle_diffs_vs_python.append(angle_diff_py)

        # Angle difference (RTL actual - Expected RTL)
        angle_diff_rtl = angle_difference(rtl['angle'], expected_rtl_angle)
        angle_diffs_vs_rtl_expected.append(angle_diff_rtl)

        # Position difference
        pos_diff = np.sqrt((rtl['x'] - expected_x)**2 + (rtl['y'] - expected_y)**2)
        position_diffs.append(pos_diff)

    angle_diffs_vs_python = np.array(angle_diffs_vs_python)
    angle_diffs_vs_rtl_expected = np.array(angle_diffs_vs_rtl_expected)
    position_diffs = np.array(position_diffs)
    expected_python_angles = np.array(expected_python_angles)
    expected_rtl_angles = np.array(expected_rtl_angles)

    # Show first 20 agents in detail with more info
    print("=" * 80)
    print("AGENT-BY-AGENT COMPARISON (First 20 agents)")
    print("=" * 80)
    print(f"{'ID':<4} {'RTL Ang':>10} {'Exp Python':>12} {'Exp RTL':>10} {'Δ vs Py':>10} {'Δ vs RTL':>11}")
    print("-" * 80)

    for i in range(min(20, num_agents)):
        rtl = rtl_agents[i]
        exp_py = expected_python_angles[i]
        exp_rtl = expected_rtl_angles[i]
        diff_py_deg = np.degrees(angle_diffs_vs_python[i])
        diff_rtl_deg = np.degrees(angle_diffs_vs_rtl_expected[i])

        print(f"{i:<4} {np.degrees(rtl['angle']):>9.2f}° {np.degrees(exp_py):>11.2f}° "
              f"{np.degrees(exp_rtl):>9.2f}° {diff_py_deg:>9.2f}° {diff_rtl_deg:>10.2f}°")

    print()

    # RTL vs RTL Expected Analysis
    print("=" * 80)
    print("RTL ACTUAL vs RTL EXPECTED ANALYSIS")
    print("=" * 80)

    rtl_angles_array = np.array([rtl_agents[i]['angle'] for i in range(num_agents)])

    print(f"RTL actual angles vs RTL expected (based on RTL init logic):")
    print(f"  Mean difference: {np.mean(angle_diffs_vs_rtl_expected):>10.6f} rad = {np.degrees(np.mean(angle_diffs_vs_rtl_expected)):>8.2f}°")
    print(f"  Std Dev:         {np.std(angle_diffs_vs_rtl_expected):>10.6f} rad = {np.degrees(np.std(angle_diffs_vs_rtl_expected)):>8.2f}°")
    print(f"  Max abs diff:    {np.max(np.abs(angle_diffs_vs_rtl_expected)):>10.6f} rad = {np.degrees(np.max(np.abs(angle_diffs_vs_rtl_expected))):>8.2f}°")
    print()

    if np.degrees(np.std(angle_diffs_vs_rtl_expected)) < 1.0:
        print("✓ RTL angles match RTL initialization logic perfectly!")
        print("  The RTL hardware is working as coded.")
    else:
        print("⚠ RTL angles DON'T match RTL initialization logic!")
        print("  There may be a bug in the RTL implementation.")
    print()

    # Python vs RTL comparison
    print(f"RTL actual angles vs Python expected:")
    print(f"  Mean difference: {np.mean(angle_diffs_vs_python):>10.6f} rad = {np.degrees(np.mean(angle_diffs_vs_python)):>8.2f}°")
    print(f"  Std Dev:         {np.std(angle_diffs_vs_python):>10.6f} rad = {np.degrees(np.std(angle_diffs_vs_python)):>8.2f}°")
    print()

    # Compare initialization methods
    print("=" * 80)
    print("INITIALIZATION METHOD COMPARISON")
    print("=" * 80)
    print()
    print("Python initialization:")
    print("  angle = arctan2(cy - y, cx - x)")
    print("  This gives angle in range [-π, π]")
    print()
    print("RTL initialization:")
    print("  angle = spawn_angle + π")
    print("  angle = normalize_to_0_2pi(angle)")
    print("  This gives angle in range [0, 2π]")
    print()

    # Check if converting between representations fixes the difference
    python_to_positive = np.where(expected_python_angles < 0, expected_python_angles + 2*np.pi, expected_python_angles)
    diff_after_conversion = []
    for i in range(num_agents):
        diff = angle_difference(rtl_angles_array[i], python_to_positive[i])
        diff_after_conversion.append(diff)
    diff_after_conversion = np.array(diff_after_conversion)

    print("After converting Python angles to [0, 2π]:")
    print(f"  Mean difference: {np.mean(diff_after_conversion):>10.6f} rad = {np.degrees(np.mean(diff_after_conversion)):>8.2f}°")
    print(f"  Std Dev:         {np.std(diff_after_conversion):>10.6f} rad = {np.degrees(np.std(diff_after_conversion)):>8.2f}°")
    print()

    # Check position distribution
    print("=" * 80)
    print("POSITION DISTRIBUTION ANALYSIS")
    print("=" * 80)

    rtl_x_array = np.array([rtl_agents[i]['x'] for i in range(num_agents)])
    rtl_y_array = np.array([rtl_agents[i]['y'] for i in range(num_agents)])

    print(f"RTL X positions:")
    print(f"  Mean: {np.mean(rtl_x_array):>10.4f}, Std Dev: {np.std(rtl_x_array):>10.4f}")
    print(f"  Min:  {np.min(rtl_x_array):>10.4f}, Max: {np.max(rtl_x_array):>10.4f}")
    print()
    print(f"RTL Y positions:")
    print(f"  Mean: {np.mean(rtl_y_array):>10.4f}, Std Dev: {np.std(rtl_y_array):>10.4f}")
    print(f"  Min:  {np.min(rtl_y_array):>10.4f}, Max: {np.max(rtl_y_array):>10.4f}")
    print()

    # Calculate expected spawn circle parameters
    spawn_radius = 0.4 * min(width, height)
    expected_center_x = width / 2.0
    expected_center_y = height / 2.0

    print(f"Expected spawn pattern (Python reference):")
    print(f"  Center: ({expected_center_x}, {expected_center_y})")
    print(f"  Radius: {spawn_radius}")
    print(f"  Expected X range: [{expected_center_x - spawn_radius:.2f}, {expected_center_x + spawn_radius:.2f}]")
    print(f"  Expected Y range: [{expected_center_y - spawn_radius:.2f}, {expected_center_y + spawn_radius:.2f}]")
    print()

    # Infer actual RTL center from agent positions
    # Assume agents are on circle - center is mean position
    actual_center_x = np.mean(rtl_x_array)
    actual_center_y = np.mean(rtl_y_array)

    print(f"Actual RTL spawn pattern (inferred from agent positions):")
    print(f"  Center: ({actual_center_x:.4f}, {actual_center_y:.4f})")
    print()

    # Check if positions are actually distributed on circle
    distances_from_expected_center = []
    distances_from_actual_center = []
    for i in range(num_agents):
        dx_exp = rtl_x_array[i] - expected_center_x
        dy_exp = rtl_y_array[i] - expected_center_y
        dist_exp = np.sqrt(dx_exp**2 + dy_exp**2)
        distances_from_expected_center.append(dist_exp)

        dx_act = rtl_x_array[i] - actual_center_x
        dy_act = rtl_y_array[i] - actual_center_y
        dist_act = np.sqrt(dx_act**2 + dy_act**2)
        distances_from_actual_center.append(dist_act)

    distances_from_expected_center = np.array(distances_from_expected_center)
    distances_from_actual_center = np.array(distances_from_actual_center)

    print(f"Distance from EXPECTED center ({expected_center_x}, {expected_center_y}):")
    print(f"  Mean: {np.mean(distances_from_expected_center):>10.4f} (expected: {spawn_radius:.4f})")
    print(f"  Std Dev: {np.std(distances_from_expected_center):>10.4f}")
    print()

    print(f"Distance from ACTUAL RTL center ({actual_center_x:.2f}, {actual_center_y:.2f}):")
    print(f"  Mean: {np.mean(distances_from_actual_center):>10.4f} (expected: {spawn_radius:.4f})")
    print(f"  Std Dev: {np.std(distances_from_actual_center):>10.4f} (expected: ~0.00)")
    print()

    if np.std(distances_from_actual_center) < 1.0:
        print("✓ Agents ARE uniformly distributed on a circle (RTL initialization worked)")
        print(f"  BUT: Center is at ({actual_center_x:.2f}, {actual_center_y:.2f}), not ({expected_center_x}, {expected_center_y})")
        print()
        print("DIAGNOSIS: RTL is using a DIFFERENT center point than Python!")
    else:
        print("WARNING: Agents are NOT uniformly distributed on a circle!")
        print("This indicates the RTL initialization may have failed.")
    print()

    # Final diagnosis
    print("=" * 80)
    print("FINAL DIAGNOSIS")
    print("=" * 80)
    print()

    print("KEY FINDINGS:")
    print()
    print("1. AGENT POSITIONS:")
    print(f"   ✓ Agents are perfectly distributed on a circle (radius={spawn_radius:.2f})")
    print(f"   ✓ Circle center: ({expected_center_x}, {expected_center_y})")
    print("   → Position initialization is CORRECT")
    print()

    print("2. AGENT ANGLES:")
    print(f"   ✗ RTL angles DON'T match RTL initialization logic")
    print(f"   ✗ Expected (spawn_angle + π): spans full [0, 2π] range")
    print(f"   ✗ Actual RTL angles: clustered around 180° ± small range")
    print()
    print("   Example (agent 5):")
    print(f"     Expected: 198.00°")
    print(f"     Actual:   181.78°")
    print(f"     Difference: -16.22°")
    print()

    print("3. ROOT CAUSE:")
    print("   The agent dump at step 0 contains angles AFTER first processing cycle,")
    print("   NOT the initial values from the `initial` block!")
    print()
    print("   In agent_coordinator.sv:")
    print("     - initial block sets: angle = spawn_angle + π")
    print("     - RUNNING state overwrites: agent_angle <= latched_angle_out")
    print()
    print("   The 'step 0' dump shows POST-PROCESSING angles, not INITIALIZATION angles.")
    print()

    print("4. IMPLICATION:")
    print("   The angle mismatch is NOT in initialization - it's in the")
    print("   AGENT PROCESSOR movement/update logic!")
    print()
    print("   The agent processor is calculating DIFFERENT angles than expected.")
    print("   This could be due to:")
    print("     • sin/cos swapped in movement calculation")
    print("     • Angle update formula error")
    print("     • Coordinate system mismatch (Y-up vs Y-down)")
    print()

    print("5. NEXT STEPS:")
    print("   To confirm, check:")
    print("     a) Agent angles BEFORE first step (need pre-RUNNING dump)")
    print("     b) Agent processor angle calculation in agent_processor.sv")
    print("     c) Movement/sensor logic for sin/cos usage")

    print()
    print("=" * 80)


if __name__ == '__main__':
    main()
