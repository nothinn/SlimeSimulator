#!/usr/bin/env python3
"""
Agent Initialization Validation - Python Reference

Generates a detailed dump of agent initialization state from the Python
reference simulator for comparison with RTL implementation.

This captures:
- Position (x, y) in both pixel and fixed-point formats
- Angle in radians, fixed-point, and lookup table index
- Spawn angle (before adding π offset)
- Direction vectors (dx, dy from angle)
- Distance from center
- Angle from center
- Quadrant information

Output: python_agent_validation.json
"""

import numpy as np
import json
import argparse
from slime_simulator import SlimeSimulator, SimulationConfig, FixedPoint, TrigLUT, LFSR


def extract_agent_state(sim, num_agents=None):
    """
    Extract complete agent state for validation.

    Args:
        sim: SlimeSimulator instance (after initialization)
        num_agents: Number of agents to extract (None = all agents)

    Returns:
        dict with agent validation data
    """
    if num_agents is None:
        num_agents = sim.config.num_agents
    else:
        num_agents = min(num_agents, sim.config.num_agents)

    # Center coordinates in fixed-point
    cx_fp = sim.fp.to_fixed(sim.width / 2)
    cy_fp = sim.fp.to_fixed(sim.height / 2)

    # Expected radius for circle spawn
    radius_fp = sim.fp.to_fixed(min(sim.width, sim.height) * 0.4)

    agents = []

    for i in range(num_agents):
        x_fp = int(sim.x[i])
        y_fp = int(sim.y[i])
        angle_fp = int(sim.angles[i])

        # Convert to pixel coordinates
        x_px = float(x_fp) / sim.fp.scale
        y_px = float(y_fp) / sim.fp.scale
        angle_rad = float(angle_fp) / sim.fp.scale

        # Calculate distance from center
        dx_fp = x_fp - cx_fp
        dy_fp = y_fp - cy_fp
        dx_px = float(dx_fp) / sim.fp.scale
        dy_px = float(dy_fp) / sim.fp.scale
        dist_from_center = np.sqrt(dx_px**2 + dy_px**2)

        # Calculate angle from center
        angle_from_center = np.arctan2(dy_px, dx_px)
        if angle_from_center < 0:
            angle_from_center += 2 * np.pi

        # Calculate spawn angle (angle_from_center is the spawn angle)
        spawn_angle_rad = angle_from_center
        spawn_angle_fp = sim.fp.to_fixed(spawn_angle_rad)

        # Direction vectors from agent's angle
        cos_angle = np.cos(angle_rad)
        sin_angle = np.sin(angle_rad)

        # Trig lookup table index
        trig_idx = int((angle_fp * sim.trig.angle_scale)) & sim.trig.angle_mask

        # Calculate cos/sin from trig LUT
        cos_fp = sim.trig.cos(angle_fp)
        sin_fp = sim.trig.sin(angle_fp)
        cos_lut = float(cos_fp) / sim.fp.scale
        sin_lut = float(sin_fp) / sim.fp.scale

        # Determine quadrant (0-3)
        quadrant = 0
        if spawn_angle_rad >= 0 and spawn_angle_rad < np.pi/2:
            quadrant = 0  # Q1: 0 to π/2
        elif spawn_angle_rad >= np.pi/2 and spawn_angle_rad < np.pi:
            quadrant = 1  # Q2: π/2 to π
        elif spawn_angle_rad >= np.pi and spawn_angle_rad < 3*np.pi/2:
            quadrant = 2  # Q3: π to 3π/2
        else:
            quadrant = 3  # Q4: 3π/2 to 2π

        # Expected spawn angle (for circle pattern)
        expected_spawn_rad = (2.0 * np.pi * i) / sim.config.num_agents
        expected_spawn_fp = sim.fp.to_fixed(expected_spawn_rad)

        # Expected agent angle (spawn + π, wrapped)
        pi_fp = sim.fp.to_fixed(np.pi)
        two_pi_fp = sim.fp.to_fixed(2 * np.pi)
        expected_angle_fp = expected_spawn_fp + pi_fp
        if expected_angle_fp >= two_pi_fp:
            expected_angle_fp -= two_pi_fp
        expected_angle_rad = float(expected_angle_fp) / sim.fp.scale

        agent_data = {
            'index': i,
            'position': {
                'x_fp': int(x_fp),
                'y_fp': int(y_fp),
                'x_px': x_px,
                'y_px': y_px,
            },
            'angle': {
                'angle_fp': int(angle_fp),
                'angle_rad': angle_rad,
                'angle_deg': np.degrees(angle_rad),
                'trig_lut_index': int(trig_idx),
            },
            'spawn': {
                'spawn_angle_rad': spawn_angle_rad,
                'spawn_angle_deg': np.degrees(spawn_angle_rad),
                'spawn_angle_fp': int(spawn_angle_fp),
                'expected_spawn_rad': expected_spawn_rad,
                'expected_spawn_fp': int(expected_spawn_fp),
            },
            'agent_angle': {
                'expected_angle_fp': int(expected_angle_fp),
                'expected_angle_rad': expected_angle_rad,
                'expected_angle_deg': np.degrees(expected_angle_rad),
            },
            'direction': {
                'cos_exact': cos_angle,
                'sin_exact': sin_angle,
                'cos_lut': cos_lut,
                'sin_lut': sin_lut,
                'cos_fp': int(cos_fp),
                'sin_fp': int(sin_fp),
            },
            'geometry': {
                'distance_from_center': dist_from_center,
                'angle_from_center_rad': angle_from_center,
                'angle_from_center_deg': np.degrees(angle_from_center),
                'quadrant': quadrant,
            },
            'expected': {
                'radius_fp': int(radius_fp),
                'radius_px': float(radius_fp) / sim.fp.scale,
                'center_x_fp': int(cx_fp),
                'center_y_fp': int(cy_fp),
                'center_x_px': float(cx_fp) / sim.fp.scale,
                'center_y_px': float(cy_fp) / sim.fp.scale,
            }
        }

        agents.append(agent_data)

    # Calculate summary statistics
    distances = [a['geometry']['distance_from_center'] for a in agents]
    angles = [a['angle']['angle_rad'] for a in agents]

    summary = {
        'num_agents': num_agents,
        'total_agents': sim.config.num_agents,
        'resolution': {'width': sim.width, 'height': sim.height},
        'spawn_pattern': sim.config.spawn_pattern,
        'fixed_point': {
            'integer_bits': sim.fp.integer_bits,
            'fractional_bits': sim.fp.fractional_bits,
            'scale': sim.fp.scale,
        },
        'statistics': {
            'distance': {
                'min': float(np.min(distances)),
                'max': float(np.max(distances)),
                'mean': float(np.mean(distances)),
                'std': float(np.std(distances)),
            },
            'angle': {
                'min_rad': float(np.min(angles)),
                'max_rad': float(np.max(angles)),
                'mean_rad': float(np.mean(angles)),
                'min_deg': float(np.degrees(np.min(angles))),
                'max_deg': float(np.degrees(np.max(angles))),
                'mean_deg': float(np.degrees(np.mean(angles))),
            }
        }
    }

    return {
        'summary': summary,
        'agents': agents
    }


def main():
    parser = argparse.ArgumentParser(description='Validate Python agent initialization')
    parser.add_argument('--resolution', type=str, default='320x240',
                       help='Simulation resolution (WIDTHxHEIGHT)')
    parser.add_argument('--agents', type=int, default=1000,
                       help='Number of agents to simulate')
    parser.add_argument('--num-validate', type=int, default=None,
                       help='Number of agents to validate (default: all)')
    parser.add_argument('--output', type=str, default='python_agent_validation.json',
                       help='Output JSON file')
    parser.add_argument('--seed', type=int, default=0xDEADBEEF,
                       help='LFSR seed (hex or decimal)')
    parser.add_argument('--verbose', action='store_true',
                       help='Print verbose output')

    args = parser.parse_args()

    # Parse resolution
    width, height = map(int, args.resolution.split('x'))

    print(f"[Python Validation] Initializing simulator...")
    print(f"  Resolution: {width}x{height}")
    print(f"  Agents: {args.agents}")
    print(f"  Seed: 0x{args.seed:08X}")

    # Create configuration
    config = SimulationConfig(
        width=width,
        height=height,
        num_agents=args.agents,
        seed=args.seed,
        spawn_pattern='circle'
    )

    # Initialize simulator
    sim = SlimeSimulator(config)

    print(f"[Python Validation] Extracting agent state...")

    # Extract agent state
    validation_data = extract_agent_state(sim, args.num_validate)

    # Save to JSON
    print(f"[Python Validation] Writing to {args.output}...")
    with open(args.output, 'w') as f:
        json.dump(validation_data, f, indent=2)

    # Print summary
    summary = validation_data['summary']
    stats = summary['statistics']

    print(f"\n[Python Validation] Summary:")
    print(f"  Validated Agents: {summary['num_agents']}")
    print(f"  Total Agents: {summary['total_agents']}")
    print(f"  Spawn Pattern: {summary['spawn_pattern']}")
    print(f"  Resolution: {summary['resolution']['width']}x{summary['resolution']['height']}")
    print(f"\n  Distance from Center:")
    print(f"    Min:  {stats['distance']['min']:.3f} px")
    print(f"    Max:  {stats['distance']['max']:.3f} px")
    print(f"    Mean: {stats['distance']['mean']:.3f} px")
    print(f"    Std:  {stats['distance']['std']:.3f} px")
    print(f"\n  Angle Distribution:")
    print(f"    Min:  {stats['angle']['min_deg']:.1f}°")
    print(f"    Max:  {stats['angle']['max_deg']:.1f}°")
    print(f"    Mean: {stats['angle']['mean_deg']:.1f}°")

    if args.verbose:
        print(f"\n[Python Validation] First 10 agents:")
        for i, agent in enumerate(validation_data['agents'][:10]):
            print(f"\n  Agent {i}:")
            print(f"    Position: ({agent['position']['x_px']:.2f}, {agent['position']['y_px']:.2f}) px")
            print(f"    Angle: {agent['angle']['angle_deg']:.1f}° ({agent['angle']['angle_rad']:.4f} rad)")
            print(f"    Distance: {agent['geometry']['distance_from_center']:.2f} px")
            print(f"    Quadrant: Q{agent['geometry']['quadrant']+1}")

    print(f"\n[Python Validation] ✓ Validation data saved to {args.output}")


if __name__ == '__main__':
    main()
