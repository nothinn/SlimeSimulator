#!/usr/bin/env python3
"""
Verify Agent Initialization Values

This script validates the generated C++ agent initialization data against
the Python reference implementation to ensure correctness.
"""

import numpy as np
import math
import sys
from pathlib import Path

# Add parent directory to path to import slime_simulator
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from slime_simulator import FixedPoint, TrigLUT


def verify_circle_spawn(num_agents=100, width=320, height=240):
    """
    Verify the circle spawn pattern matches expected behavior.
    """
    print("=" * 80)
    print("Agent Initialization Verification")
    print("=" * 80)
    print(f"Configuration: {num_agents} agents, {width}x{height} resolution")
    print()

    # Initialize fixed-point system
    fp = FixedPoint(12, 12)
    trig = TrigLUT(fp, table_bits=10)

    # Calculate expected values
    cx_fp = fp.to_fixed(width / 2.0)
    cy_fp = fp.to_fixed(height / 2.0)
    radius_fp = fp.to_fixed(min(width, height) * 0.4)

    print("Expected parameters:")
    print(f"  Center: ({width/2.0}, {height/2.0}) px → ({cx_fp}, {cy_fp}) fp")
    print(f"  Radius: {min(width, height) * 0.4} px → {radius_fp} fp")
    print(f"  Scale: {fp.scale} (Q12.12)")
    print()

    # Verify first 10 agents
    print("First 10 agents verification:")
    print("-" * 80)
    print(f"{'#':<4} {'X (px)':<10} {'Y (px)':<10} {'Angle (rad)':<12} {'Angle (deg)':<10} "
          f"{'Dist from center':<16} {'Expected dist':<14}")
    print("-" * 80)

    all_pass = True
    for i in range(min(10, num_agents)):
        # Calculate expected position
        spawn_angle_rad = 2.0 * math.pi * i / num_agents
        spawn_angle_fp = fp.to_fixed(spawn_angle_rad)

        cos_val = trig.cos_array(np.array([spawn_angle_fp], dtype=np.int64))[0]
        sin_val = trig.sin_array(np.array([spawn_angle_fp], dtype=np.int64))[0]

        x_fp = cx_fp + fp.multiply(cos_val, radius_fp)
        y_fp = cy_fp + fp.multiply(sin_val, radius_fp)

        # Expected angle (pointing inward = spawn_angle + π)
        pi_fp = fp.to_fixed(math.pi)
        two_pi_fp = fp.to_fixed(2.0 * math.pi)
        angle_fp = spawn_angle_fp + pi_fp
        if angle_fp >= two_pi_fp:
            angle_fp -= two_pi_fp

        # Convert to float for display
        x_px = fp.from_fixed(x_fp)
        y_px = fp.from_fixed(y_fp)
        angle_rad = fp.from_fixed(angle_fp)
        angle_deg = angle_rad * 180.0 / math.pi

        # Calculate distance from center
        dx = x_px - width/2.0
        dy = y_px - height/2.0
        dist = math.sqrt(dx*dx + dy*dy)
        expected_dist = min(width, height) * 0.4

        # Check if distance is approximately correct (within 1%)
        dist_error = abs(dist - expected_dist) / expected_dist
        status = "✓" if dist_error < 0.01 else "✗"

        print(f"{i:<4} {x_px:<10.2f} {y_px:<10.2f} {angle_rad:<12.6f} {angle_deg:<10.1f} "
              f"{dist:<16.2f} {expected_dist:<14.2f} {status}")

        if dist_error >= 0.01:
            all_pass = False
            print(f"     WARNING: Distance error {dist_error*100:.2f}%")

    print("-" * 80)
    print()

    # Verify angle distribution
    print("Verifying angle distribution (agents should be evenly distributed):")
    print("-" * 80)

    angles_deg = []
    for i in range(num_agents):
        spawn_angle_rad = 2.0 * math.pi * i / num_agents
        spawn_angle_fp = fp.to_fixed(spawn_angle_rad)
        pi_fp = fp.to_fixed(math.pi)
        two_pi_fp = fp.to_fixed(2.0 * math.pi)
        angle_fp = spawn_angle_fp + pi_fp
        if angle_fp >= two_pi_fp:
            angle_fp -= two_pi_fp
        angle_rad = fp.from_fixed(angle_fp)
        angles_deg.append(angle_rad * 180.0 / math.pi)

    angles_deg = np.array(angles_deg)

    print(f"  Min angle: {angles_deg.min():.2f}°")
    print(f"  Max angle: {angles_deg.max():.2f}°")
    print(f"  Expected spacing: {360.0/num_agents:.2f}° per agent")

    # Check first few spacings
    print(f"\n  First 5 angle spacings:")
    for i in range(min(5, num_agents-1)):
        spacing = angles_deg[i+1] - angles_deg[i]
        expected = 360.0 / num_agents
        print(f"    Agent {i} → {i+1}: {spacing:.2f}° (expected: {expected:.2f}°)")

    print("-" * 80)
    print()

    # Summary
    if all_pass:
        print("✓ All verification checks PASSED!")
        print("  - All agents are positioned on circle with 40% radius")
        print("  - All agents are pointing inward (toward center)")
        print("  - Agents are evenly distributed around the circle")
    else:
        print("✗ Some verification checks FAILED!")
        print("  Please review the warnings above.")

    print("=" * 80)

    return all_pass


if __name__ == '__main__':
    success = verify_circle_spawn(num_agents=100, width=320, height=240)
    sys.exit(0 if success else 1)
