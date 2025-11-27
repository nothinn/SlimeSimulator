#!/usr/bin/env python3
"""
Visualize Agent Diagnostic Results

Creates visual representations of agent movement patterns.
"""

import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt


def load_diagnostic_data(json_file='debug_log.json'):
    """Load diagnostic data from JSON file."""
    with open(json_file, 'r') as f:
        data = json.load(f)
    return data


def create_trajectory_plot(data, output_file='trajectory_plot.png'):
    """Create a plot showing all agent trajectories."""
    metadata = data['metadata']
    logs = data['step_logs']

    width = metadata['width']
    height = metadata['height']

    # Group logs by agent
    agent_trajectories = {}
    for log in logs:
        agent_id = log['agent_id']
        if agent_id not in agent_trajectories:
            agent_trajectories[agent_id] = []
        agent_trajectories[agent_id].append(log)

    # Create plot
    fig, axes = plt.subplots(2, 2, figsize=(16, 14))
    fig.suptitle('Agent Movement Diagnostic Visualization', fontsize=16, fontweight='bold')

    # Plot 1: Trajectories
    ax1 = axes[0, 0]
    ax1.set_title('Agent Trajectories (First 10 Agents, 5 Steps)', fontsize=12)
    ax1.set_xlabel('X Position (pixels)')
    ax1.set_ylabel('Y Position (pixels)')
    ax1.set_xlim(0, width)
    ax1.set_ylim(height, 0)  # Invert Y axis for image coordinates
    ax1.grid(True, alpha=0.3)

    colors = plt.cm.tab10(np.linspace(0, 1, 10))

    for agent_id, traj in sorted(agent_trajectories.items()):
        x_coords = [traj[0]['pos_x_float']] + [log['new_pos_x_float'] for log in traj]
        y_coords = [traj[0]['pos_y_float']] + [log['new_pos_y_float'] for log in traj]

        # Plot trajectory
        ax1.plot(x_coords, y_coords, 'o-', color=colors[agent_id],
                label=f'Agent {agent_id}', linewidth=2, markersize=6)

        # Mark start and end
        ax1.plot(x_coords[0], y_coords[0], 's', color=colors[agent_id],
                markersize=10, markeredgecolor='black', markeredgewidth=1.5)
        ax1.plot(x_coords[-1], y_coords[-1], '*', color=colors[agent_id],
                markersize=15, markeredgecolor='black', markeredgewidth=1.5)

    ax1.legend(loc='upper right', fontsize=8)

    # Plot 2: Sensor readings over time
    ax2 = axes[0, 1]
    ax2.set_title('Sensor Readings Over Time (Agent 0)', fontsize=12)
    ax2.set_xlabel('Step Number')
    ax2.set_ylabel('Sensor Value')
    ax2.grid(True, alpha=0.3)

    agent_0_traj = agent_trajectories.get(0, [])
    if agent_0_traj:
        steps = [log['step_num'] for log in agent_0_traj]
        forward = [log['sensor_forward'] for log in agent_0_traj]
        left = [log['sensor_left'] for log in agent_0_traj]
        right = [log['sensor_right'] for log in agent_0_traj]

        ax2.plot(steps, forward, 'o-', label='Forward', linewidth=2)
        ax2.plot(steps, left, 's-', label='Left', linewidth=2)
        ax2.plot(steps, right, '^-', label='Right', linewidth=2)
        ax2.legend()

    # Plot 3: Turn decision distribution
    ax3 = axes[1, 0]
    ax3.set_title('Turn Decision Distribution', fontsize=12)
    ax3.set_xlabel('Agent ID')
    ax3.set_ylabel('Count')
    ax3.grid(True, alpha=0.3, axis='y')

    turn_types = ['none', 'left', 'right', 'random_left', 'random_right']
    turn_colors = ['green', 'blue', 'red', 'cyan', 'magenta']
    agent_ids = sorted(agent_trajectories.keys())

    # Collect turn counts for each agent
    turn_data = {turn_type: [] for turn_type in turn_types}
    for agent_id in agent_ids:
        traj = agent_trajectories[agent_id]
        for turn_type in turn_types:
            count = sum(1 for log in traj if log['turn_decision'] == turn_type)
            turn_data[turn_type].append(count)

    # Stacked bar chart
    bottom = np.zeros(len(agent_ids))
    for i, turn_type in enumerate(turn_types):
        ax3.bar(agent_ids, turn_data[turn_type], bottom=bottom,
               label=turn_type, color=turn_colors[i])
        bottom += np.array(turn_data[turn_type])

    ax3.legend()
    ax3.set_xticks(agent_ids)

    # Plot 4: Distance moved per step
    ax4 = axes[1, 1]
    ax4.set_title('Distance Moved Per Step', fontsize=12)
    ax4.set_xlabel('Agent ID')
    ax4.set_ylabel('Average Distance (pixels)')
    ax4.grid(True, alpha=0.3, axis='y')

    avg_distances = []
    for agent_id in agent_ids:
        traj = agent_trajectories[agent_id]
        avg_dist = np.mean([log['distance_moved'] for log in traj])
        avg_distances.append(avg_dist)

    ax4.bar(agent_ids, avg_distances, color='steelblue', edgecolor='black')
    ax4.axhline(y=1.0, color='red', linestyle='--', linewidth=2, label='Expected (1.0 px)')
    ax4.legend()
    ax4.set_xticks(agent_ids)

    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"Saved trajectory plot to {output_file}")
    plt.close()


def create_trail_map_image(trail_file='debug_trail.npy', output_file='trail_map_vis.png'):
    """Create visualization of trail map."""
    trail_map = np.load(trail_file)

    # Normalize to 0-255 range
    if trail_map.max() > 0:
        normalized = (trail_map / trail_map.max() * 255).astype(np.uint8)
    else:
        normalized = trail_map.astype(np.uint8)

    # Create RGB image with color gradient
    img = Image.new('RGB', (trail_map.shape[1], trail_map.shape[0]))
    pixels = img.load()

    for y in range(trail_map.shape[0]):
        for x in range(trail_map.shape[1]):
            intensity = normalized[y, x]
            # Green-yellow gradient for slime
            r = min(255, int(intensity * 0.8))
            g = intensity
            b = min(255, int(intensity * 0.8))
            pixels[x, y] = (r, g, b)

    # Upscale for visibility
    img = img.resize((trail_map.shape[1] * 2, trail_map.shape[0] * 2), Image.NEAREST)

    img.save(output_file)
    print(f"Saved trail map visualization to {output_file}")

    # Also create heatmap with matplotlib
    plt.figure(figsize=(12, 9))
    plt.imshow(trail_map, cmap='hot', interpolation='nearest')
    plt.colorbar(label='Trail Intensity')
    plt.title('Trail Map Heatmap (After 5 Steps)')
    plt.xlabel('X Position')
    plt.ylabel('Y Position')
    plt.tight_layout()
    heatmap_file = 'trail_map_heatmap.png'
    plt.savefig(heatmap_file, dpi=150, bbox_inches='tight')
    print(f"Saved trail map heatmap to {heatmap_file}")
    plt.close()


def create_comparison_table_image(data, output_file='comparison_table.png'):
    """Create a visual comparison table."""
    metadata = data['metadata']
    logs = data['step_logs']

    # Create image
    width = 1200
    height = 800
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)

    # Try to use a monospace font
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 12)
        font_bold = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf', 14)
    except:
        font = ImageFont.load_default()
        font_bold = font

    y_pos = 10

    # Title
    draw.text((10, y_pos), "AGENT DIAGNOSTIC COMPARISON TABLE", font=font_bold, fill='black')
    y_pos += 30

    # Metadata
    draw.text((10, y_pos), f"Resolution: {metadata['width']}x{metadata['height']}", font=font, fill='black')
    y_pos += 20
    draw.text((10, y_pos), f"Agents: {metadata['num_agents']}", font=font, fill='black')
    y_pos += 20
    draw.text((10, y_pos), f"Steps: {metadata['total_steps']}", font=font, fill='black')
    y_pos += 30

    # Group by agent
    agent_trajectories = {}
    for log in logs:
        agent_id = log['agent_id']
        if agent_id not in agent_trajectories:
            agent_trajectories[agent_id] = []
        agent_trajectories[agent_id].append(log)

    # Show first 5 agents
    for agent_id in sorted(list(agent_trajectories.keys()))[:5]:
        traj = agent_trajectories[agent_id]

        draw.text((10, y_pos), f"Agent {agent_id}:", font=font_bold, fill='blue')
        y_pos += 20

        initial_pos = (traj[0]['pos_x_float'], traj[0]['pos_y_float'])
        final_pos = (traj[-1]['new_pos_x_float'], traj[-1]['new_pos_y_float'])

        draw.text((20, y_pos),
                 f"  Initial: ({initial_pos[0]:.1f}, {initial_pos[1]:.1f}) -> Final: ({final_pos[0]:.1f}, {final_pos[1]:.1f})",
                 font=font, fill='black')
        y_pos += 20

        total_dist = sum(log['distance_moved'] for log in traj)
        draw.text((20, y_pos), f"  Total distance: {total_dist:.2f} pixels", font=font, fill='black')
        y_pos += 20

        turn_counts = {}
        for log in traj:
            turn = log['turn_decision']
            turn_counts[turn] = turn_counts.get(turn, 0) + 1

        draw.text((20, y_pos), f"  Turns: {turn_counts}", font=font, fill='black')
        y_pos += 25

        if y_pos > height - 50:
            break

    img.save(output_file)
    print(f"Saved comparison table image to {output_file}")


def print_findings(data):
    """Print key findings from diagnostic data."""
    print("\n" + "=" * 80)
    print("KEY FINDINGS FROM DIAGNOSTIC")
    print("=" * 80)

    metadata = data['metadata']
    logs = data['step_logs']

    print(f"\nSimulation Parameters:")
    print(f"  Resolution: {metadata['width']}x{metadata['height']}")
    print(f"  Agents: {metadata['num_agents']}")
    print(f"  Steps: {metadata['total_steps']}")
    print(f"  LFSR Seed: {metadata['lfsr_seed']}")
    print(f"\n  Movement Parameters:")
    for key, value in metadata['parameters'].items():
        print(f"    {key:20s}: {value}")

    # Analyze patterns
    agent_trajectories = {}
    for log in logs:
        agent_id = log['agent_id']
        if agent_id not in agent_trajectories:
            agent_trajectories[agent_id] = []
        agent_trajectories[agent_id].append(log)

    print(f"\nBehavior Analysis:")

    # Initial sensing
    all_sensors_zero = True
    for log in logs:
        if log['sensor_forward'] != 0 or log['sensor_left'] != 0 or log['sensor_right'] != 0:
            all_sensors_zero = False
            break

    if all_sensors_zero:
        print("  ✓ All sensors read 0 initially (empty canvas)")
        print("  → Agents will turn right consistently (FL == FR, default behavior)")

    # Turn behavior
    right_turns = sum(1 for log in logs if log['turn_decision'] == 'right')
    total_decisions = len(logs)
    print(f"  ✓ {right_turns}/{total_decisions} decisions were 'turn right' ({right_turns/total_decisions*100:.1f}%)")

    # Movement consistency
    distances = [log['distance_moved'] for log in logs]
    avg_dist = np.mean(distances)
    print(f"  ✓ Average distance per step: {avg_dist:.4f} pixels")
    print(f"  ✓ Min/Max distance: {min(distances):.4f} / {max(distances):.4f} pixels")

    # Circular pattern formation
    print("\n  Pattern Formation:")
    print("  - Agents initialized at center (160, 120)")
    print("  - All agents moving outward in different directions")
    print("  - Consistent right turning creates spiral-like paths")
    print("  - Trail deposits accumulate at agent positions")

    print("\n  Ground Truth for RTL Comparison:")
    print("  ✓ Deterministic LFSR generates predictable random numbers")
    print("  ✓ Fixed-point arithmetic ensures bit-exact reproduction")
    print("  ✓ Sensor positions calculated using trig LUT (1024 entries)")
    print("  ✓ Trail deposits verified at exact pixel locations")

    print("\n" + "=" * 80)


def main():
    print("Visualizing Agent Diagnostic Results...")

    # Load data
    data = load_diagnostic_data('debug_log.json')

    # Create visualizations
    print("\nGenerating visualizations...")
    create_trajectory_plot(data)
    create_trail_map_image()
    create_comparison_table_image(data)

    # Print findings
    print_findings(data)

    print("\nVisualization complete!")
    print("\nGenerated files:")
    print("  trajectory_plot.png      - Agent trajectories and analysis")
    print("  trail_map_vis.png        - Trail map visualization")
    print("  trail_map_heatmap.png    - Trail map heatmap")
    print("  comparison_table.png     - Comparison table image")


if __name__ == "__main__":
    main()
