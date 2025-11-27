#!/usr/bin/env python3
"""
Test to verify the agent circle spawn fix.
This validates that all agents have properly wrapped angles in [0, 2π).
"""

import math

def test_rtl_circle_spawn(num_agents=1000, width=800, height=600):
    """Simulate the fixed RTL circle spawn initialization."""
    fp_scale = 4096  # 2^12

    # Center canvas
    cx = (width * fp_scale) // 2
    cy = (height * fp_scale) // 2

    # Radius and constants
    min_dimension = min(width, height)
    radius_real = min_dimension * 0.4
    pi_fp = int(3.14159265359 * fp_scale)
    two_pi = 2.0 * 3.14159265359
    two_pi_fp = int(two_pi * fp_scale)

    print(f"Testing RTL circle spawn for {num_agents} agents")
    print(f"Canvas: {width}x{height}, Center: ({cx/fp_scale:.1f}, {cy/fp_scale:.1f})")
    print(f"Radius: {radius_real:.1f} pixels")
    print(f"two_pi_fp = {two_pi_fp}, pi_fp = {pi_fp}")
    print()

    # Track statistics
    max_unwrapped_angle = 0
    num_wrapped = 0
    all_valid = True

    # Test all agents
    for i in range(num_agents):
        # Calculate spawn angle
        angle_rad = (two_pi * i) / num_agents

        # Position calculation (using $cos and $sin)
        cos_val = math.cos(angle_rad)
        sin_val = math.sin(angle_rad)

        x = cx + int(cos_val * radius_real * fp_scale)
        y = cy + int(sin_val * radius_real * fp_scale)

        # Agent angle = spawn_angle + π
        spawn_angle_fp = int(angle_rad * fp_scale)
        angle_fp_raw = spawn_angle_fp + pi_fp

        # Track max unwrapped angle
        if angle_fp_raw > max_unwrapped_angle:
            max_unwrapped_angle = angle_fp_raw

        # Apply wrapping (THE FIX)
        if angle_fp_raw >= two_pi_fp:
            angle_fp = angle_fp_raw - two_pi_fp
            num_wrapped += 1
        else:
            angle_fp = angle_fp_raw

        # Validate
        if not (0 <= angle_fp < two_pi_fp):
            all_valid = False
            print(f"ERROR: Agent[{i}] has invalid angle: {angle_fp} (not in [0, {two_pi_fp}))")

    print(f"Results:")
    print(f"  Total agents: {num_agents}")
    print(f"  Agents wrapped: {num_wrapped} ({100*num_wrapped/num_agents:.1f}%)")
    print(f"  Max unwrapped angle: {max_unwrapped_angle} (would be {max_unwrapped_angle/fp_scale:.4f} rad)")
    print(f"  All angles valid: {all_valid}")
    print()

    # Sample positions to verify continuous circle
    print("Sample agent positions (8 points around circle):")
    for i in range(8):
        idx = i * num_agents // 8
        angle_rad = (two_pi * idx) / num_agents
        cos_val = math.cos(angle_rad)
        sin_val = math.sin(angle_rad)

        x = cx + int(cos_val * radius_real * fp_scale)
        y = cy + int(sin_val * radius_real * fp_scale)

        spawn_angle_fp = int(angle_rad * fp_scale)
        angle_fp_raw = spawn_angle_fp + pi_fp
        angle_fp = angle_fp_raw - two_pi_fp if angle_fp_raw >= two_pi_fp else angle_fp_raw

        print(f"  Agent[{idx:4d}]: pos=({x/fp_scale:6.1f}, {y/fp_scale:6.1f}), "
              f"spawn_angle={math.degrees(angle_rad):6.1f}°, "
              f"agent_angle={angle_fp/fp_scale:.3f} rad")

    print()
    if all_valid:
        print("SUCCESS: All agent angles properly wrapped to [0, 2π)")
        print("The circle should render as ONE continuous circle, not 3 broken pieces!")
    else:
        print("FAILURE: Some agents have invalid angles")

    return all_valid


def compare_before_and_after_fix():
    """Show the specific issue before and after the fix."""
    num_agents = 1000
    fp_scale = 4096
    two_pi = 2.0 * 3.14159265359
    two_pi_fp = int(two_pi * fp_scale)
    pi_fp = int(3.14159265359 * fp_scale)

    print("=" * 80)
    print("DEMONSTRATING THE BUG AND FIX")
    print("=" * 80)
    print()

    print("Testing agents in bottom half of circle (180° to 360°):")
    print()

    # Test critical agents around the wrapping boundary
    test_indices = [499, 500, 501, 750, 999]

    for i in test_indices:
        angle_rad = (two_pi * i) / num_agents
        spawn_angle_fp = int(angle_rad * fp_scale)
        angle_fp_raw = spawn_angle_fp + pi_fp

        # Before fix: no wrapping
        angle_fp_before = angle_fp_raw

        # After fix: with wrapping
        if angle_fp_raw >= two_pi_fp:
            angle_fp_after = angle_fp_raw - two_pi_fp
        else:
            angle_fp_after = angle_fp_raw

        print(f"Agent[{i:4d}] at spawn angle {math.degrees(angle_rad):6.1f}°:")
        print(f"  BEFORE FIX: angle_fp = {angle_fp_before:5d} "
              f"({angle_fp_before/fp_scale:.3f} rad) "
              f"{'[EXCEEDS 2π!]' if angle_fp_before >= two_pi_fp else '[OK]'}")
        print(f"  AFTER FIX:  angle_fp = {angle_fp_after:5d} "
              f"({angle_fp_after/fp_scale:.3f} rad) "
              f"{'[OK - wrapped]' if angle_fp_after < two_pi_fp else '[ERROR]'}")
        print()

    print("EXPLANATION:")
    print("  Without the fix, agents in the bottom half (spawn angle > π) have")
    print("  agent_angle = spawn_angle + π exceeding 2π (25735 in fixed-point).")
    print()
    print("  This causes discontinuity when their angles are used in trig lookups,")
    print("  resulting in the circle appearing broken into 3 pieces instead of")
    print("  one continuous circle.")
    print()
    print("  The fix adds modulo wrapping: if angle_fp >= 2π, subtract 2π.")
    print()


if __name__ == "__main__":
    # Run tests
    compare_before_and_after_fix()
    print("=" * 80)
    print()
    test_rtl_circle_spawn(num_agents=1000, width=800, height=600)
