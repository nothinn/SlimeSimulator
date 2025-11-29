#!/usr/bin/env python3
"""
Compare agent positions and angles between Python reference and RTL simulation.
Generates CSV trace files for detailed analysis of agent divergence.
"""

import json
import sys
import os
import csv
from pathlib import Path

def extract_agent_state(state_dump_file):
    """Extract agent positions and angles from a state dump JSON file."""
    try:
        with open(state_dump_file, 'r') as f:
            state = json.load(f)
        return {
            'x': state['agent_x'],
            'y': state['agent_y'],
            'angles': state['agent_angles'],
            'trail_map': state['trail_map']
        }
    except Exception as e:
        print(f"Error reading {state_dump_file}: {e}")
        return None

def calculate_agent_pixel_pos(fp_x, fp_y, fp_scale=4096):
    """Convert fixed-point coordinates to pixel coordinates."""
    px = (fp_x // fp_scale) % 320  # Assuming 320x240
    py = (fp_y // fp_scale) % 240
    return px, py

def generate_trace_csv(python_output_dir, num_agents=100, num_steps=5):
    """Generate CSV trace comparing Python and RTL agent states."""

    # For now, use Python simulation data
    # We'll need to extend this to capture RTL data

    csv_file = "agent_trace_comparison.csv"

    print(f"\n[Trace] Generating agent trace CSV: {csv_file}")

    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)

        # Header: Step, Agent0_X, Agent0_Y, Agent0_Angle, Agent1_X, Agent1_Y, Agent1_Angle, ...
        header = ['Step']
        for agent_id in range(num_agents):
            header.extend([f'Agent{agent_id}_X', f'Agent{agent_id}_Y', f'Agent{agent_id}_Angle'])
        writer.writerow(header)

        # Read Python state dumps
        for step in range(num_steps):
            state_file = os.path.join(python_output_dir, f'state_dump_step_{step:05d}.json')

            if not os.path.exists(state_file):
                print(f"  Warning: State file not found: {state_file}")
                continue

            state = extract_agent_state(state_file)
            if not state:
                continue

            row = [step]
            for agent_id in range(min(num_agents, len(state['x']))):
                px, py = calculate_agent_pixel_pos(state['x'][agent_id], state['y'][agent_id])
                angle = state['angles'][agent_id]
                row.extend([px, py, angle])

            writer.writerow(row)

    print(f"✓ Trace CSV generated: {csv_file}")
    return csv_file

def dump_python_state(python_simulator, output_dir):
    """Dump Python simulator state at current step."""
    step = python_simulator.step_count if hasattr(python_simulator, 'step_count') else 0
    state_file = os.path.join(output_dir, f'state_dump_step_{step:05d}.json')
    python_simulator.dump_state(state_file)
    return state_file

def compare_positions(python_data, rtl_data, agent_id, max_error_pixels=2):
    """Compare Python vs RTL position for a single agent."""
    if not python_data or not rtl_data:
        return None, "Missing data"

    py_x, py_y = python_data
    rtl_x, rtl_y = rtl_data

    dx = abs(py_x - rtl_x)
    dy = abs(py_y - rtl_y)
    dist = (dx**2 + dy**2) ** 0.5

    status = "OK" if dist <= max_error_pixels else "ERROR"
    return dist, status

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Compare agent traces between Python and RTL")
    parser.add_argument("--python-dir", default="python_output", help="Python output directory")
    parser.add_argument("--agents", type=int, default=100, help="Number of agents")
    parser.add_argument("--steps", type=int, default=5, help="Number of steps")
    parser.add_argument("--output", default="agent_trace_comparison.csv", help="Output CSV file")

    args = parser.parse_args()

    # Generate trace
    csv_file = generate_trace_csv(args.python_dir, args.agents, args.steps)

    print(f"\n[Trace] Agent trace comparison complete")
    print(f"[Trace] Output: {csv_file}")
    print(f"[Trace] To view: head -20 {csv_file}")
