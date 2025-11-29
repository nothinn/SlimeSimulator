#!/usr/bin/env python3
"""
Extract RTL and Python agent trajectories from JSON dumps and create comparison CSV.
"""

import json
import csv
import os
from pathlib import Path
from typing import Dict, List, Tuple
import math

def load_agent_dumps(dump_dir: str, num_steps: int, num_agents: int = 100) -> Dict:
    """Load all agent state dumps from a directory."""
    print(f"Loading {num_steps} agent state files from {dump_dir}...")

    data_by_step = {}

    for step in range(num_steps):
        filename = os.path.join(dump_dir, f'agent_state_step_{step:05d}.json')

        if not os.path.exists(filename):
            print(f"  WARNING: Step {step} file not found: {filename}")
            continue

        try:
            with open(filename, 'r') as f:
                data = json.load(f)

            # Index agents by agent_id for fast lookup
            data_by_step[step] = {agent['agent_id']: agent for agent in data['agents']}

            if step % 20 == 0:
                print(f"  Loaded step {step}")

        except Exception as e:
            print(f"  ERROR loading {filename}: {e}")
            continue

    print(f"✓ Loaded {len(data_by_step)} steps\n")
    return data_by_step

def create_comparison_csv(rtl_data: Dict, python_data: Dict, output_file: str, num_agents: int = 100):
    """Create comparison CSV with Python and RTL trajectories."""
    print(f"Creating comparison CSV: {output_file}")

    # Find common steps
    common_steps = sorted(set(rtl_data.keys()) & set(python_data.keys()))
    print(f"Common steps: {len(common_steps)} (0-{max(common_steps) if common_steps else 0})")
    print()

    rows = []
    error_stats = {
        'x_diffs': [],
        'y_diffs': [],
        'angle_diffs': [],
        'distances': []
    }

    for step in common_steps:
        rtl_agents = rtl_data[step]
        py_agents = python_data[step]

        for agent_id in range(num_agents):
            if agent_id not in rtl_agents or agent_id not in py_agents:
                continue

            rtl = rtl_agents[agent_id]
            py = py_agents[agent_id]

            # Calculate differences in pixels and degrees
            x_diff = abs(py['x_px'] - rtl['x_px'])
            y_diff = abs(py['y_px'] - rtl['y_px'])
            distance = math.sqrt(x_diff**2 + y_diff**2)

            # Angle difference (shortest path)
            angle_diff = abs(py['angle_deg'] - rtl['angle_deg'])
            if angle_diff > 180:
                angle_diff = 360 - angle_diff

            error_stats['x_diffs'].append(x_diff)
            error_stats['y_diffs'].append(y_diff)
            error_stats['distances'].append(distance)
            error_stats['angle_diffs'].append(angle_diff)

            rows.append({
                'step': step,
                'agent_id': agent_id,
                'python_x': round(py['x_px'], 4),
                'python_y': round(py['y_px'], 4),
                'python_angle': round(py['angle_deg'], 6),
                'rtl_x': round(rtl['x_px'], 4),
                'rtl_y': round(rtl['y_px'], 4),
                'rtl_angle': round(rtl['angle_deg'], 6),
                'x_diff': round(x_diff, 4),
                'y_diff': round(y_diff, 4),
                'distance': round(distance, 4),
                'angle_diff': round(angle_diff, 6)
            })

    # Write CSV
    if rows:
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

        print(f"✓ Wrote {len(rows)} rows to {output_file}\n")
    else:
        print(f"ERROR: No data to write!\n")
        return None

    # Print statistics
    print("=" * 70)
    print("TRAJECTORY COMPARISON STATISTICS")
    print("=" * 70)
    print(f"\nTotal comparisons: {len(rows)}")
    print(f"Steps: {len(common_steps)}")
    print(f"Agents: {num_agents}\n")

    if error_stats['x_diffs']:
        print("X Position Difference (pixels):")
        print(f"  Mean:  {sum(error_stats['x_diffs']) / len(error_stats['x_diffs']):.4f}")
        print(f"  Median: {sorted(error_stats['x_diffs'])[len(error_stats['x_diffs'])//2]:.4f}")
        print(f"  Max:   {max(error_stats['x_diffs']):.4f}")
        print(f"  Min:   {min(error_stats['x_diffs']):.4f}")

        print("\nY Position Difference (pixels):")
        print(f"  Mean:  {sum(error_stats['y_diffs']) / len(error_stats['y_diffs']):.4f}")
        print(f"  Median: {sorted(error_stats['y_diffs'])[len(error_stats['y_diffs'])//2]:.4f}")
        print(f"  Max:   {max(error_stats['y_diffs']):.4f}")
        print(f"  Min:   {min(error_stats['y_diffs']):.4f}")

        print("\nEuclidean Distance (pixels):")
        print(f"  Mean:  {sum(error_stats['distances']) / len(error_stats['distances']):.4f}")
        print(f"  Median: {sorted(error_stats['distances'])[len(error_stats['distances'])//2]:.4f}")
        print(f"  Max:   {max(error_stats['distances']):.4f}")
        print(f"  Min:   {min(error_stats['distances']):.4f}")

        print("\nAngle Difference (degrees):")
        print(f"  Mean:  {sum(error_stats['angle_diffs']) / len(error_stats['angle_diffs']):.6f}")
        print(f"  Median: {sorted(error_stats['angle_diffs'])[len(error_stats['angle_diffs'])//2]:.6f}")
        print(f"  Max:   {max(error_stats['angle_diffs']):.6f}")
        print(f"  Min:   {min(error_stats['angle_diffs']):.6f}")

        # Count agents within tolerance
        within_1px = sum(1 for d in error_stats['distances'] if d < 1.0)
        within_05px = sum(1 for d in error_stats['distances'] if d < 0.5)

        print(f"\nPositions within tolerance:")
        print(f"  < 0.5 px: {within_05px}/{len(error_stats['distances'])} ({100*within_05px/len(error_stats['distances']):.1f}%)")
        print(f"  < 1.0 px: {within_1px}/{len(error_stats['distances'])} ({100*within_1px/len(error_stats['distances']):.1f}%)")

    print("\n" + "=" * 70 + "\n")

    return output_file

def analyze_divergence_by_step(comparison_file: str, num_agents: int = 100):
    """Analyze divergence pattern across steps."""
    print(f"Analyzing divergence pattern by step...")

    step_stats = {}

    with open(comparison_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            step = int(row['step'])

            if step not in step_stats:
                step_stats[step] = {
                    'x_diffs': [],
                    'y_diffs': [],
                    'distances': [],
                    'angle_diffs': []
                }

            step_stats[step]['x_diffs'].append(float(row['x_diff']))
            step_stats[step]['y_diffs'].append(float(row['y_diff']))
            step_stats[step]['distances'].append(float(row['distance']))
            step_stats[step]['angle_diffs'].append(float(row['angle_diff']))

    print("\nDivergence by Step:")
    print("Step | Agents | Dist(mean) | Dist(max) | X(mean) | Y(mean) | Angle(mean)")
    print("-" * 75)

    for step in sorted(step_stats.keys()):
        stats = step_stats[step]
        mean_dist = sum(stats['distances']) / len(stats['distances']) if stats['distances'] else 0
        max_dist = max(stats['distances']) if stats['distances'] else 0
        mean_x = sum(stats['x_diffs']) / len(stats['x_diffs']) if stats['x_diffs'] else 0
        mean_y = sum(stats['y_diffs']) / len(stats['y_diffs']) if stats['y_diffs'] else 0
        mean_angle = sum(stats['angle_diffs']) / len(stats['angle_diffs']) if stats['angle_diffs'] else 0

        print(f"{step:4d} | {len(stats['distances']):6d} | {mean_dist:10.4f} | {max_dist:9.4f} | {mean_x:7.4f} | {mean_y:7.4f} | {mean_angle:10.6f}")

    print()

def main():
    print("\n" + "=" * 70)
    print("RTL vs Python Trajectory Comparison")
    print("=" * 70 + "\n")

    # Load both datasets
    print("Phase 1: Loading data from JSON dumps\n")

    # RTL has steps 0-99 (100 files)
    rtl_data = load_agent_dumps('rtl_agent_dumps', 100)

    # Python has steps 0-100 (101 files, but we'll use 0-99 for comparison)
    python_data = load_agent_dumps('python_agent_dumps', 100)

    # Create comparison CSV
    print("Phase 2: Creating comparison CSV\n")
    csv_file = create_comparison_csv(rtl_data, python_data, 'trajectory_comparison_100steps.csv')

    if csv_file:
        # Analyze divergence pattern
        print("Phase 3: Analyzing divergence pattern\n")
        analyze_divergence_by_step(csv_file)

        print("=" * 70)
        print("✓ Analysis complete!")
        print(f"  Comparison CSV: {csv_file}")
        print("=" * 70 + "\n")

if __name__ == '__main__':
    main()
