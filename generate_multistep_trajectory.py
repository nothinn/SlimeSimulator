#!/usr/bin/env python3
"""
Generate multi-step trajectory CSV from Python simulator runs.
Captures agent positions and angles at each simulation step for visualization.
"""

import json
import csv
import math
import os
import sys
import tempfile
import subprocess
from pathlib import Path

def run_python_simulator(steps=10, agents=100, width=320, height=240, output_dir=None):
    """
    Run Python simulator and collect state dumps at each step.
    Returns list of state dictionaries.
    """
    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix="slime_sim_")

    os.makedirs(output_dir, exist_ok=True)

    print(f"[Sim] Running Python simulator...")
    print(f"  Steps: {steps}, Agents: {agents}, Resolution: {width}x{height}")
    print(f"  Output: {output_dir}")

    # Build command
    cmd = [
        "python3", "slime_simulator.py",
        "--width", str(width),
        "--height", str(height),
        "--agents", str(agents),
        "--steps", str(steps),
        "--output", output_dir,
        "--dump-state", os.path.join(output_dir, "state")
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            print(f"[Error] Simulator failed:")
            print(result.stderr)
            return None

        print(result.stdout)
    except subprocess.TimeoutExpired:
        print("[Error] Simulator timeout")
        return None

    # Load state dump
    state_file = os.path.join(output_dir, "state")
    try:
        with open(state_file, 'r') as f:
            state = json.load(f)
        return state
    except Exception as e:
        print(f"[Error] Could not load state: {e}")
        return None

def extract_step_data(state, step_num, agents=100):
    """
    Extract agent position and angle data for a given step.
    """
    agents_data = []

    for i in range(min(agents, len(state.get('agent_x', [])))):
        x_fp = state['agent_x'][i]
        y_fp = state['agent_y'][i]
        angle_fp = state['agent_angles'][i]

        x_px = x_fp // 4096
        y_px = y_fp // 4096
        angle_rad = angle_fp / 4096.0
        angle_deg = math.degrees(angle_rad)

        agents_data.append({
            'step': step_num,
            'agent_id': i,
            'python_x': x_px,
            'python_y': y_px,
            'python_angle_deg': angle_deg,
            'python_x_fp': x_fp,
            'python_y_fp': y_fp,
            'python_angle_fp': angle_fp
        })

    return agents_data

def create_multistep_csv(state, num_agents=100, output_file='multistep_trajectory.csv'):
    """
    Create CSV with agent trajectory data for all steps.
    """
    print(f"\n[CSV] Creating multi-step trajectory CSV...")

    all_rows = []

    # Extract step 0 data
    all_rows.extend(extract_step_data(state, 0, num_agents))

    csv_columns = [
        'step', 'agent_id',
        'python_x', 'python_y', 'python_angle_deg',
        'python_x_fp', 'python_y_fp', 'python_angle_fp'
    ]

    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=csv_columns)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"[CSV] ✓ Created {output_file}")
    print(f"  Rows: {len(all_rows)}")
    print(f"  Agents: {num_agents}")
    print(f"  Columns: {', '.join(csv_columns)}")

    return output_file

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Generate multi-step trajectory CSV')
    parser.add_argument('--steps', type=int, default=10, help='Number of simulation steps')
    parser.add_argument('--agents', type=int, default=100, help='Number of agents')
    parser.add_argument('--width', type=int, default=320, help='Canvas width')
    parser.add_argument('--height', type=int, default=240, help='Canvas height')
    parser.add_argument('--output', default='multistep_trajectory.csv', help='Output CSV file')
    parser.add_argument('--sim-dir', help='Temp directory for simulator output')

    args = parser.parse_args()

    print("\n" + "="*70)
    print("Multi-Step Trajectory Generator")
    print("="*70)

    # Run simulator
    state = run_python_simulator(
        steps=args.steps,
        agents=args.agents,
        width=args.width,
        height=args.height,
        output_dir=args.sim_dir
    )

    if state is None:
        print("[Error] Failed to run simulator")
        return 1

    # Create CSV
    csv_file = create_multistep_csv(state, args.agents, args.output)

    print("\n" + "="*70)
    print(f"✓ Trajectory data ready: {csv_file}")
    print("="*70)
    print(f"\nUsage with visualizer:")
    print(f"  python3 agent_trajectory_visualizer.py {csv_file}")

    return 0

if __name__ == '__main__':
    sys.exit(main())
