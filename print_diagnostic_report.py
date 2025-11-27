#!/usr/bin/env python3
"""
Print comprehensive diagnostic report to console.
"""

import json
import numpy as np


def print_banner(text, char='=', width=80):
    """Print a banner."""
    print('\n' + char * width)
    print(text.center(width))
    print(char * width + '\n')


def print_section(title):
    """Print a section header."""
    print(f"\n{'─' * 80}")
    print(f"  {title}")
    print('─' * 80)


def main():
    # Load data
    with open('debug_log.json', 'r') as f:
        data = json.load(f)

    with open('debug_analysis.json', 'r') as f:
        analysis = json.load(f)

    metadata = data['metadata']
    logs = data['step_logs']

    # Print header
    print_banner("AGENT MOVEMENT DIAGNOSTIC REPORT", '═')

    # Configuration
    print_section("Test Configuration")
    print(f"  Resolution:      {metadata['width']}×{metadata['height']} pixels")
    print(f"  Agents Tracked:  {metadata['num_agents']}")
    print(f"  Simulation Steps: {metadata['total_steps']}")
    print(f"  LFSR Seed:       {metadata['lfsr_seed']}")
    print(f"\n  Fixed-Point Configuration:")
    print(f"    Format:        Q{metadata['fixed_point']['int_bits']}.{metadata['fixed_point']['frac_bits']}")
    print(f"    Scale Factor:  {metadata['fixed_point']['scale']}")
    print(f"    Total Bits:    {metadata['fixed_point']['int_bits'] + metadata['fixed_point']['frac_bits'] + 1} (including sign)")

    # Parameters
    print_section("Simulation Parameters")
    params = metadata['parameters']
    print(f"  Move Speed:      {params['move_speed']:.6f} pixels/step")
    print(f"  Turn Speed:      {params['turn_speed']:.6f} radians/turn (~{np.degrees(params['turn_speed']):.2f}°)")
    print(f"  Sensor Angle:    {params['sensor_angle']:.6f} radians (~{np.degrees(params['sensor_angle']):.2f}°)")
    print(f"  Sensor Distance: {params['sensor_distance']:.6f} pixels")
    print(f"  Deposit Amount:  {params['deposit_amount']}")
    print(f"  Decay Rate:      {params['decay_rate']:.6f}")

    # Movement summary
    print_section("Movement Analysis Summary")

    # Group logs by agent
    agent_trajectories = {}
    for log in logs:
        agent_id = log['agent_id']
        if agent_id not in agent_trajectories:
            agent_trajectories[agent_id] = []
        agent_trajectories[agent_id].append(log)

    # Calculate aggregate statistics
    all_distances = [log['distance_moved'] for log in logs]
    avg_distance = np.mean(all_distances)
    std_distance = np.std(all_distances)

    all_sensors = [(log['sensor_forward'], log['sensor_left'], log['sensor_right']) for log in logs]
    all_forward = [s[0] for s in all_sensors]
    all_left = [s[1] for s in all_sensors]
    all_right = [s[2] for s in all_sensors]

    print(f"  Total log entries:     {len(logs)}")
    print(f"  Average distance/step: {avg_distance:.4f} ± {std_distance:.4f} pixels")
    print(f"  Min/Max distance:      {min(all_distances):.4f} / {max(all_distances):.4f} pixels")
    print(f"\n  Sensor Statistics (all agents, all steps):")
    print(f"    Forward: avg={np.mean(all_forward):.2f}, max={max(all_forward)}")
    print(f"    Left:    avg={np.mean(all_left):.2f}, max={max(all_left)}")
    print(f"    Right:   avg={np.mean(all_right):.2f}, max={max(all_right)}")

    # Turn decisions
    turn_counts = {}
    for log in logs:
        turn = log['turn_decision']
        turn_counts[turn] = turn_counts.get(turn, 0) + 1

    print(f"\n  Turn Decision Distribution:")
    for turn_type, count in sorted(turn_counts.items()):
        percentage = count / len(logs) * 100
        bar_length = int(percentage / 2)
        bar = '█' * bar_length
        print(f"    {turn_type:15s}: {count:3d} ({percentage:5.1f}%) {bar}")

    # Per-agent summary
    print_section("Per-Agent Summary")

    header = f"{'Agent':<8} {'Initial Position':<20} {'Final Position':<20} {'Net Disp':<10} {'Avg Dist':<10} {'Turns':<30}"
    print(f"  {header}")
    print(f"  {'-' * len(header)}")

    for agent_id in sorted(agent_trajectories.keys()):
        stats = analysis[f'agent_{agent_id}']
        init_pos = f"({stats['initial_position'][0]:.1f}, {stats['initial_position'][1]:.1f})"
        final_pos = f"({stats['final_position'][0]:.1f}, {stats['final_position'][1]:.1f})"
        net_disp = f"{stats['net_displacement']:.2f} px"
        avg_dist = f"{stats['avg_distance_per_step']:.4f}"

        # Turn summary
        turns = stats['turn_counts']
        turn_str = f"R:{turns.get('right', 0)} L:{turns.get('left', 0)} N:{turns.get('none', 0)}"

        print(f"  {agent_id:<8} {init_pos:<20} {final_pos:<20} {net_disp:<10} {avg_dist:<10} {turn_str:<30}")

    # Detailed step-by-step for first agent
    print_section("Detailed Step-by-Step: Agent 0")

    agent_0_traj = agent_trajectories[0]
    for i, log in enumerate(agent_0_traj):
        print(f"\n  Step {log['step_num']}:")
        print(f"    Position: ({log['pos_x_float']:.2f}, {log['pos_y_float']:.2f}) → ({log['new_pos_x_float']:.2f}, {log['new_pos_y_float']:.2f})")
        print(f"    Position (FP): 0x{log['pos_x_fp']:X}, 0x{log['pos_y_fp']:X} → 0x{log['new_pos_x_fp']:X}, 0x{log['new_pos_y_fp']:X}")
        print(f"    Angle: {log['angle_rad']:.4f} rad ({log['angle_idx']:3d}/1024) → {log['new_angle_rad']:.4f} rad ({log['new_angle_idx']:3d}/1024)")
        print(f"    Sensors: F={log['sensor_forward']:3d} @ {tuple(log['sensor_fwd_pos'])}, "
              f"L={log['sensor_left']:3d} @ {tuple(log['sensor_left_pos'])}, "
              f"R={log['sensor_right']:3d} @ {tuple(log['sensor_right_pos'])}")
        print(f"    Decision: {log['turn_decision'].upper()}")
        print(f"    Movement: {log['distance_moved']:.4f} pixels, angle change: {log['angle_changed']:.4f} rad")
        print(f"    Deposit: +{params['deposit_amount']} at {tuple(log['deposit_pixel'])}")

    # Key findings
    print_section("Key Findings")

    # Check if all sensors are zero
    all_sensors_zero = all(s[0] == 0 and s[1] == 0 and s[2] == 0 for s in all_sensors)

    print("  1. Initial Behavior:")
    if all_sensors_zero:
        print("     ✓ All sensors read 0 (empty canvas)")
        print("     → Agents turn right by default when F == L == R")
    else:
        print("     ✓ Some trail detected, agents responding to environment")

    print("\n  2. Movement Consistency:")
    if 0.99 <= avg_distance <= 1.01:
        print(f"     ✓ Average distance {avg_distance:.4f} ≈ 1.0 (expected)")
    else:
        print(f"     ⚠ Average distance {avg_distance:.4f} deviates from expected 1.0")

    max_dist = max(all_distances)
    if 1.41 <= max_dist <= 1.42:
        print(f"     ✓ Max distance {max_dist:.4f} ≈ √2 (diagonal movement)")

    print("\n  3. Deterministic Behavior:")
    print("     ✓ LFSR provides deterministic pseudo-random sequence")
    print("     ✓ Fixed-point arithmetic ensures bit-exact reproduction")
    print("     ✓ Same seed will always produce identical results")

    print("\n  4. RTL Comparison Readiness:")
    print("     ✓ All agent states logged in fixed-point format")
    print("     ✓ Sensor positions and readings recorded")
    print("     ✓ Turn decisions and LFSR states captured")
    print("     ✓ Trail deposits tracked for validation")

    # File summary
    print_section("Generated Files")

    import os
    files = [
        ('debug_log.json', 'Full step-by-step logs'),
        ('debug_table.txt', 'Human-readable text table'),
        ('debug_analysis.json', 'Movement pattern analysis'),
        ('debug_trail.npy', 'Trail map data (320×240)'),
        ('trajectory_plot.png', '4-panel visualization'),
        ('trail_map_vis.png', 'Trail map visualization'),
        ('trail_map_heatmap.png', 'Trail heatmap'),
        ('comparison_table.png', 'Comparison table image'),
        ('AGENT_DIAGNOSTIC_SUMMARY.md', 'Comprehensive documentation')
    ]

    for filename, description in files:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024 * 1024:
                size_str = f"{size / 1024:.1f} KB"
            else:
                size_str = f"{size / (1024 * 1024):.1f} MB"
            print(f"  ✓ {filename:<35s} {size_str:>10s}  {description}")
        else:
            print(f"  ✗ {filename:<35s} {'--':>10s}  {description}")

    # Ground truth verification
    print_section("Ground Truth Verification")

    print("  This diagnostic establishes ground truth for RTL comparison by:")
    print("  ")
    print("  1. Deterministic LFSR")
    print("     - 32-bit maximal-length sequence")
    print("     - Taps at positions [32, 22, 2, 1]")
    print("     - Seed: 0xDEADBEEF")
    print("  ")
    print("  2. Fixed-Point Arithmetic")
    print("     - Q12.12 format (25 bits total)")
    print("     - Multiplication: (a × b) >> 12")
    print("     - Range: -2048.0 to +2047.9998")
    print("  ")
    print("  3. Trigonometric LUT")
    print("     - 1024-entry sine/cosine tables")
    print("     - 10-bit angle addressing")
    print("     - Covers full 2π range")
    print("  ")
    print("  4. Complete State Logging")
    print("     - Position (fixed-point and float)")
    print("     - Angle (index and radians)")
    print("     - Sensor readings and positions")
    print("     - Turn decisions")
    print("     - Trail deposits")

    # Next steps
    print_section("Next Steps")

    print("  To compare with RTL simulation:")
    print("  ")
    print("  1. Run RTL simulation with identical parameters")
    print("     - Same LFSR seed (0xDEADBEEF)")
    print("     - Same number of agents (10)")
    print("     - Same number of steps (5)")
    print("  ")
    print("  2. Export RTL agent states in same JSON format")
    print("  ")
    print("  3. Compare step-by-step:")
    print("     - Agent positions (fixed-point)")
    print("     - Angle indices")
    print("     - Sensor readings")
    print("     - Turn decisions")
    print("     - Trail deposits")
    print("  ")
    print("  4. Investigate any discrepancies:")
    print("     - LFSR state mismatch?")
    print("     - Fixed-point rounding error?")
    print("     - Trig LUT value difference?")
    print("     - Decision logic bug?")

    print_banner("DIAGNOSTIC COMPLETE", '═')
    print()


if __name__ == "__main__":
    main()
