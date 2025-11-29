#!/usr/bin/env python3
"""
Extract agent trajectories from Python and RTL simulations.
Creates CSV files for side-by-side comparison of agent movements.
"""

import json
import csv
import math
import os
import sys
from pathlib import Path

def fp_to_pixel(fp_val, fp_scale=4096):
    """Convert fixed-point value to pixel coordinate."""
    return (fp_val // fp_scale) % 320  # Assuming 320-wide canvas

def fp_to_angle_degrees(fp_angle):
    """Convert fixed-point angle to degrees."""
    rad = fp_angle / 4096.0
    return math.degrees(rad)

def extract_agent_data(state_file):
    """Extract agent positions and angles from state JSON."""
    try:
        with open(state_file, 'r') as f:
            state = json.load(f)
        return {
            'x': state['agent_x'],
            'y': state['agent_y'],
            'angles': state['agent_angles']
        }
    except Exception as e:
        print(f"Error reading {state_file}: {e}")
        return None

def create_python_trace(python_dir, num_agents=100):
    """Create agent trajectory CSV from Python state dumps."""
    csv_file = "python_agent_trajectories.csv"

    print(f"[Python Trace] Creating {csv_file}...")

    # Try to load state file
    state_data = extract_agent_data(python_dir)
    if not state_data:
        print(f"[Python Trace] Could not load state from {python_dir}")
        return None

    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)

        # Header
        header = ['Agent']
        for field in ['X_pixels', 'Y_pixels', 'Angle_degrees', 'Angle_FP']:
            header.append(field)
        writer.writerow(header)

        # Agent data
        for agent_id in range(min(num_agents, len(state_data['x']))):
            x_fp = state_data['x'][agent_id]
            y_fp = state_data['y'][agent_id]
            angle_fp = state_data['angles'][agent_id]

            x_px = x_fp // 4096
            y_px = y_fp // 4096
            angle_deg = fp_to_angle_degrees(angle_fp)

            writer.writerow([
                agent_id,
                x_px,
                y_px,
                f"{angle_deg:.2f}",
                angle_fp
            ])

    print(f"[Python Trace] ✓ Created {csv_file}")
    return csv_file

def create_rtl_trace(validation_json="rtl_agent_validation.json"):
    """Create agent trajectory CSV from RTL validation data."""
    csv_file = "rtl_agent_trajectories.csv"

    print(f"[RTL Trace] Creating {csv_file}...")

    if not os.path.exists(validation_json):
        print(f"[RTL Trace] Validation file not found: {validation_json}")
        return None

    with open(validation_json, 'r') as f:
        rtl_data = json.load(f)

    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)

        # Header
        header = ['Agent', 'X_pixels', 'Y_pixels', 'Angle_degrees', 'X_error', 'Y_error', 'Angle_error']
        writer.writerow(header)

        # Load Python data for comparison
        py_data = extract_agent_data("python_state")

        # Process RTL data
        for agent_entry in rtl_data:
            agent_id = agent_entry.get('agent_id', -1)
            expected_x = agent_entry.get('expected_x_pixel', -1)
            expected_y = agent_entry.get('expected_y_pixel', -1)
            actual_x = agent_entry.get('actual_x_pixel', -1)
            actual_y = agent_entry.get('actual_y_pixel', -1)
            actual_angle = agent_entry.get('actual_angle_degrees', -1)

            x_error = abs(expected_x - actual_x) if expected_x >= 0 and actual_x >= 0 else 0
            y_error = abs(expected_y - actual_y) if expected_y >= 0 and actual_y >= 0 else 0

            expected_angle = -1
            angle_error = 0
            if py_data and agent_id >= 0 and agent_id < len(py_data['angles']):
                expected_angle = fp_to_angle_degrees(py_data['angles'][agent_id])
                if actual_angle >= 0:
                    angle_error = abs(expected_angle - actual_angle)

            writer.writerow([
                agent_id,
                actual_x,
                actual_y,
                f"{actual_angle:.2f}" if actual_angle >= 0 else "N/A",
                x_error,
                y_error,
                f"{angle_error:.2f}" if angle_error >= 0 else "N/A"
            ])

    print(f"[RTL Trace] ✓ Created {csv_file}")
    return csv_file

def create_comparison_trace(num_agents=100):
    """Create side-by-side comparison CSV."""
    csv_file = "agent_trace_comparison.csv"

    print(f"[Comparison] Creating {csv_file}...")

    # Load both datasets
    py_data = extract_agent_data("python_state")

    try:
        with open("rtl_agent_validation.json", 'r') as f:
            rtl_raw = json.load(f)
    except:
        rtl_raw = None

    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)

        # Header
        header = ['Agent', 'Python_X', 'Python_Y', 'Python_Angle', 'RTL_X', 'RTL_Y', 'RTL_Angle', 'X_Error', 'Y_Error']
        writer.writerow(header)

        # Process agents
        for agent_id in range(min(num_agents, len(py_data['x']) if py_data else 0)):
            py_x = py_y = py_angle = -1
            rtl_x = rtl_y = rtl_angle = -1
            x_err = y_err = 0

            if py_data and agent_id < len(py_data['x']):
                py_x = py_data['x'][agent_id] // 4096
                py_y = py_data['y'][agent_id] // 4096
                py_angle = fp_to_angle_degrees(py_data['angles'][agent_id])

            if rtl_raw:
                for rtl_entry in rtl_raw:
                    if rtl_entry.get('agent_id') == agent_id:
                        rtl_x = rtl_entry.get('actual_x_pixel', -1)
                        rtl_y = rtl_entry.get('actual_y_pixel', -1)
                        rtl_angle = rtl_entry.get('actual_angle_degrees', -1)

                        if py_x >= 0 and rtl_x >= 0:
                            x_err = abs(py_x - rtl_x)
                        if py_y >= 0 and rtl_y >= 0:
                            y_err = abs(py_y - rtl_y)
                        break

            writer.writerow([
                agent_id,
                py_x,
                py_y,
                f"{py_angle:.2f}" if py_angle >= 0 else "N/A",
                rtl_x,
                rtl_y,
                f"{rtl_angle:.2f}" if rtl_angle >= 0 else "N/A",
                x_err,
                y_err
            ])

    print(f"[Comparison] ✓ Created {csv_file}")
    return csv_file

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("Agent Trajectory Extraction")
    print("=" * 80)

    # Create traces
    py_trace = create_python_trace("python_state", num_agents=100)
    rtl_trace = create_rtl_trace()
    comparison = create_comparison_trace(num_agents=100)

    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"Python trace:    {py_trace}")
    print(f"RTL trace:       {rtl_trace}")
    print(f"Comparison:      {comparison}")
    print("\nTo view comparison:")
    print("  head -20 agent_trace_comparison.csv")
    print("  tail -30 agent_trace_comparison.csv")
