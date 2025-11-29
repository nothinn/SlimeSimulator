#!/usr/bin/env python3
"""
Create comprehensive trajectory CSV with Python and RTL data across steps.
Combines initialization (step 0) with movement simulation (steps 1+).
"""

import json
import csv
import math
import os
from pathlib import Path

def load_python_init_state(state_file='python_state'):
    """Load Python initialization state."""
    try:
        with open(state_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[Error] {state_file} not found")
        return None

def load_rtl_validation_data(val_file='rtl_agent_validation.json'):
    """Load RTL validation data."""
    try:
        with open(val_file, 'r') as f:
            data = json.load(f)
        return data.get('agents', [])
    except FileNotFoundError:
        print(f"[Error] {val_file} not found")
        return None

def fp_to_angle_deg(fp_angle):
    """Convert fixed-point angle to degrees."""
    rad = fp_angle / 4096.0
    return math.degrees(rad)

def create_trajectory_csv(
    python_state_file='python_state',
    rtl_val_file='rtl_agent_validation.json',
    output_file='agent_trajectory.csv',
    num_agents=100,
    num_steps=3
):
    """
    Create CSV with agent trajectories combining Python and RTL data.

    For step 0: Use initialization data
    For steps 1+: Show estimated positions based on movement
    """

    print(f"[Trajectory] Loading data...")

    # Load Python initialization
    py_state = load_python_init_state(python_state_file)
    if not py_state:
        return None

    # Load RTL validation
    rtl_agents = load_rtl_validation_data(rtl_val_file)
    if not rtl_agents:
        print("[Warning] RTL validation data not available")
        rtl_agents = []

    print(f"[Trajectory] Creating trajectory CSV with {num_agents} agents × {num_steps} steps...")

    # Build trajectory data
    rows = []

    for step in range(num_steps):
        print(f"  Step {step}/{num_steps-1}...", end=' ', flush=True)

        for agent_id in range(min(num_agents, len(py_state['agent_x']))):
            # Python data (initialization)
            py_x_fp = py_state['agent_x'][agent_id]
            py_y_fp = py_state['agent_y'][agent_id]
            py_angle_fp = py_state['agent_angles'][agent_id]

            py_x_px = py_x_fp // 4096
            py_y_px = py_y_fp // 4096
            py_angle_deg = fp_to_angle_deg(py_angle_fp)

            # RTL data (from validation)
            rtl_x_px = -1
            rtl_y_px = -1
            rtl_angle_deg = -1
            rtl_x_fp = 0
            rtl_y_fp = 0
            rtl_angle_fp = 0

            if agent_id < len(rtl_agents):
                rtl_agent = rtl_agents[agent_id]
                rtl_x_px = rtl_agent['position']['x_px']
                rtl_y_px = rtl_agent['position']['y_px']
                rtl_angle_deg = rtl_agent['angle']['angle_deg']
                rtl_x_fp = rtl_agent['position']['x_fp']
                rtl_y_fp = rtl_agent['position']['y_fp']
                rtl_angle_fp = rtl_agent['angle']['angle_fp']

            # Calculate position after movement (simple forward movement)
            if step > 0:
                # Agents move by 1 pixel per step in their facing direction
                # This is approximate - actual movement depends on sensing/turning
                dx = math.cos(math.radians(py_angle_deg))
                dy = math.sin(math.radians(py_angle_deg))

                py_x_px_step = py_x_px + (dx * step)
                py_y_px_step = py_y_px + (dy * step)

                rtl_x_px_step = rtl_x_px + (dx * step) if rtl_x_px >= 0 else -1
                rtl_y_px_step = rtl_y_px + (dy * step) if rtl_y_px >= 0 else -1
            else:
                py_x_px_step = py_x_px
                py_y_px_step = py_y_px
                rtl_x_px_step = rtl_x_px
                rtl_y_px_step = rtl_y_px

            # Calculate differences
            x_diff = abs(py_x_px_step - rtl_x_px_step) if rtl_x_px_step >= 0 else 0
            y_diff = abs(py_y_px_step - rtl_y_px_step) if rtl_y_px_step >= 0 else 0
            angle_diff = abs(py_angle_deg - rtl_angle_deg) if rtl_angle_deg >= 0 else 0

            row = {
                'step': step,
                'agent_id': agent_id,
                'python_x': f"{py_x_px_step:.1f}",
                'python_y': f"{py_y_px_step:.1f}",
                'python_angle_deg': f"{py_angle_deg:.2f}",
                'python_x_fp': py_x_fp,
                'python_y_fp': py_y_fp,
                'python_angle_fp': py_angle_fp,
                'rtl_x': f"{rtl_x_px_step:.1f}" if rtl_x_px_step >= 0 else "N/A",
                'rtl_y': f"{rtl_y_px_step:.1f}" if rtl_y_px_step >= 0 else "N/A",
                'rtl_angle_deg': f"{rtl_angle_deg:.2f}" if rtl_angle_deg >= 0 else "N/A",
                'rtl_x_fp': rtl_x_fp,
                'rtl_y_fp': rtl_y_fp,
                'rtl_angle_fp': rtl_angle_fp,
                'x_diff': f"{x_diff:.2f}",
                'y_diff': f"{y_diff:.2f}",
                'angle_diff': f"{angle_diff:.2f}"
            }

            rows.append(row)

        print("✓")

    # Write CSV
    columns = [
        'step', 'agent_id',
        'python_x', 'python_y', 'python_angle_deg',
        'python_x_fp', 'python_y_fp', 'python_angle_fp',
        'rtl_x', 'rtl_y', 'rtl_angle_deg',
        'rtl_x_fp', 'rtl_y_fp', 'rtl_angle_fp',
        'x_diff', 'y_diff', 'angle_diff'
    ]

    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n[Trajectory] ✓ Created {output_file}")
    print(f"  Rows: {len(rows)} ({num_agents} agents × {num_steps} steps)")
    print(f"  Columns: {len(columns)}")
    print(f"\nCSV Preview (first 5 rows):")

    with open(output_file, 'r') as f:
        for i, line in enumerate(f):
            if i < 6:  # Header + 5 rows
                print(f"  {line.rstrip()}")
            else:
                break

    return output_file

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Create agent trajectory CSV')
    parser.add_argument('--python-state', default='python_state', help='Python state dump file')
    parser.add_argument('--rtl-validation', default='rtl_agent_validation.json', help='RTL validation JSON')
    parser.add_argument('--output', default='agent_trajectory.csv', help='Output CSV file')
    parser.add_argument('--agents', type=int, default=100, help='Number of agents')
    parser.add_argument('--steps', type=int, default=3, help='Number of steps to simulate')

    args = parser.parse_args()

    print("\n" + "="*70)
    print("Agent Trajectory CSV Generator")
    print("="*70 + "\n")

    csv_file = create_trajectory_csv(
        python_state_file=args.python_state,
        rtl_val_file=args.rtl_validation,
        output_file=args.output,
        num_agents=args.agents,
        num_steps=args.steps
    )

    if csv_file:
        print(f"\n" + "="*70)
        print(f"✓ Trajectory CSV ready: {csv_file}")
        print("="*70)
        print(f"\nUse with visualizer:")
        print(f"  python3 agent_trajectory_visualizer.py {csv_file}")
    else:
        print("\n[Error] Failed to create trajectory CSV")
