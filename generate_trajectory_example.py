#!/usr/bin/env python3
"""
Example script showing how to generate multi-step trajectory data
for use with the agent trajectory visualizer.

This demonstrates the expected CSV format for multi-step data.
"""

import numpy as np
import csv

def generate_example_trajectory(num_agents=10, num_steps=5, output_file='example_trajectory.csv'):
    """
    Generate example multi-step trajectory data.

    Args:
        num_agents: Number of agents to simulate
        num_steps: Number of simulation steps
        output_file: Output CSV filename
    """
    print(f"Generating {num_steps}-step trajectory for {num_agents} agents...")

    # Initialize agents on circle (like slime simulator)
    width, height = 320, 240
    radius = min(width, height) * 0.4
    center_x, center_y = width / 2, height / 2

    # Create CSV file
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # Write header
        writer.writerow([
            'Step', 'Agent',
            'Python_X', 'Python_Y', 'Python_Angle_Deg',
            'RTL_X', 'RTL_Y', 'RTL_Angle_Deg',
            'X_Diff', 'Y_Diff', 'Angle_Diff'
        ])

        # Generate trajectory for each step
        for step in range(num_steps):
            for agent_id in range(num_agents):
                # Initial angle around circle
                base_angle = (agent_id / num_agents) * 360.0

                # Python agent (drifts slightly clockwise)
                python_angle = base_angle + step * 2.0  # 2 degrees per step
                python_angle_rad = np.deg2rad(python_angle)
                python_x = center_x + radius * np.cos(python_angle_rad) + step * 0.5
                python_y = center_y + radius * np.sin(python_angle_rad) + step * 0.3

                # RTL agent (small error from Python)
                rtl_x = python_x + np.random.uniform(-0.5, 0.5)
                rtl_y = python_y + np.random.uniform(-0.5, 0.5)
                rtl_angle = python_angle + np.random.uniform(-0.1, 0.1)

                # Calculate differences
                x_diff = abs(rtl_x - python_x)
                y_diff = abs(rtl_y - python_y)
                angle_diff = abs(rtl_angle - python_angle)

                # Write row
                writer.writerow([
                    step, agent_id,
                    f'{python_x:.2f}', f'{python_y:.2f}', f'{python_angle:.2f}',
                    f'{rtl_x:.2f}', f'{rtl_y:.2f}', f'{rtl_angle:.2f}',
                    f'{x_diff:.2f}', f'{y_diff:.2f}', f'{angle_diff:.2f}'
                ])

    print(f"Generated {output_file}")
    print(f"Total rows: {num_agents * num_steps}")
    print(f"\nVisualize with:")
    print(f"  python3 agent_trajectory_visualizer.py {output_file}")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Generate example trajectory data')
    parser.add_argument('--agents', type=int, default=10, help='Number of agents')
    parser.add_argument('--steps', type=int, default=5, help='Number of steps')
    parser.add_argument('--output', default='example_trajectory.csv', help='Output file')

    args = parser.parse_args()

    generate_example_trajectory(
        num_agents=args.agents,
        num_steps=args.steps,
        output_file=args.output
    )
