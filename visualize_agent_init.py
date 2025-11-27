#!/usr/bin/env python3
"""
Agent Initialization Visualization Tool

Creates visual comparison plots of agent positions from Python and RTL simulations.

Features:
- Side-by-side scatter plots of agent positions
- Color coding by quadrant
- Highlighting of mismatches
- Circle overlay showing expected spawn pattern
- Vector arrows showing agent angles

Output: agent_comparison.png
"""

import json
import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Circle, FancyArrowPatch


def plot_agents(ax, agents, title, show_angles=True, highlight_failed=None):
    """
    Plot agent positions on given axes.

    Args:
        ax: Matplotlib axes
        agents: List of agent data dicts
        title: Plot title
        show_angles: Whether to show angle vectors
        highlight_failed: List of failed agent indices (or None)
    """
    # Extract data
    x_positions = [a['position']['x_px'] for a in agents]
    y_positions = [a['position']['y_px'] for a in agents]
    angles_rad = [a['angle']['angle_rad'] for a in agents]
    quadrants = [a['geometry']['quadrant'] for a in agents]

    # Get expected parameters
    expected = agents[0]['expected']
    center_x = expected['center_x_px']
    center_y = expected['center_y_px']
    radius = expected['radius_px']
    width = expected.get('width', center_x * 2)
    height = expected.get('height', center_y * 2)

    # Color map for quadrants
    quadrant_colors = ['red', 'green', 'blue', 'orange']
    colors = [quadrant_colors[q] for q in quadrants]

    # Plot agents
    if highlight_failed:
        # Plot passed agents in color
        passed_x = [x_positions[i] for i in range(len(agents)) if i not in highlight_failed]
        passed_y = [y_positions[i] for i in range(len(agents)) if i not in highlight_failed]
        passed_colors = [colors[i] for i in range(len(agents)) if i not in highlight_failed]

        # Plot failed agents in black with larger markers
        failed_x = [x_positions[i] for i in highlight_failed]
        failed_y = [y_positions[i] for i in highlight_failed]

        ax.scatter(passed_x, passed_y, c=passed_colors, s=20, alpha=0.6, edgecolors='none')
        ax.scatter(failed_x, failed_y, c='black', s=50, alpha=0.8, marker='x', linewidths=2, label='Failed')
    else:
        ax.scatter(x_positions, y_positions, c=colors, s=20, alpha=0.6, edgecolors='none')

    # Draw expected circle
    circle = Circle((center_x, center_y), radius, fill=False, edgecolor='gray',
                   linestyle='--', linewidth=2, label='Expected circle')
    ax.add_patch(circle)

    # Draw center marker
    ax.plot(center_x, center_y, 'k+', markersize=15, markeredgewidth=2, label='Center')

    # Draw angle vectors for a subset of agents
    if show_angles:
        step = max(1, len(agents) // 20)  # Show ~20 vectors
        for i in range(0, len(agents), step):
            x = x_positions[i]
            y = y_positions[i]
            angle = angles_rad[i]
            dx = 10 * np.cos(angle)
            dy = 10 * np.sin(angle)

            arrow = FancyArrowPatch((x, y), (x + dx, y + dy),
                                   arrowstyle='->', mutation_scale=10,
                                   color='black', alpha=0.3, linewidth=0.5)
            ax.add_patch(arrow)

    # Set limits and labels
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.set_aspect('equal')
    ax.set_xlabel('X (pixels)')
    ax.set_ylabel('Y (pixels)')
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right')

    # Invert y-axis to match image coordinates
    ax.invert_yaxis()


def plot_comparison(python_data, rtl_data, comparison_data, output_file):
    """
    Create side-by-side comparison plot.

    Args:
        python_data: Python agent data
        rtl_data: RTL agent data
        comparison_data: Comparison results
        output_file: Output PNG file path
    """
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))

    # Get failed agent indices
    failed_indices = [a['index'] for a in comparison_data['agents'] if not a['passed']]

    # Plot Python agents
    plot_agents(axes[0], python_data['agents'], 'Python Reference', show_angles=True)

    # Plot RTL agents with failures highlighted
    plot_agents(axes[1], rtl_data['agents'], 'RTL Implementation', show_angles=True,
               highlight_failed=failed_indices)

    # Add overall title
    summary = comparison_data['summary']
    overall_status = "✓ PASSED" if summary['overall_passed'] else "✗ FAILED"
    fig.suptitle(f'Agent Initialization Comparison - {overall_status}\n' +
                f'{summary["num_agents_passed"]}/{summary["num_agents_compared"]} agents passed',
                fontsize=14, fontweight='bold')

    # Adjust layout
    plt.tight_layout(rect=[0, 0, 1, 0.96])

    # Save figure
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"[Visualization] ✓ Saved comparison plot to {output_file}")

    plt.close()


def plot_error_distribution(comparison_data, output_file):
    """
    Create error distribution plots.

    Args:
        comparison_data: Comparison results
        output_file: Output PNG file path
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Extract error data
    agents = comparison_data['agents']
    indices = [a['index'] for a in agents]
    position_errors = [a['position']['position_error_px'] for a in agents]
    angle_errors = [a['angle']['angle_deg_error'] for a in agents]
    distance_errors = [a['geometry']['distance_error_rtl'] for a in agents]

    # Position error scatter
    ax = axes[0, 0]
    ax.scatter(indices, position_errors, s=5, alpha=0.5)
    ax.set_xlabel('Agent Index')
    ax.set_ylabel('Position Error (pixels)')
    ax.set_title('Position Error vs Agent Index')
    ax.grid(True, alpha=0.3)

    # Angle error scatter
    ax = axes[0, 1]
    ax.scatter(indices, angle_errors, s=5, alpha=0.5)
    ax.set_xlabel('Agent Index')
    ax.set_ylabel('Angle Error (degrees)')
    ax.set_title('Angle Error vs Agent Index')
    ax.grid(True, alpha=0.3)

    # Position error histogram
    ax = axes[1, 0]
    ax.hist(position_errors, bins=50, edgecolor='black', alpha=0.7)
    ax.set_xlabel('Position Error (pixels)')
    ax.set_ylabel('Count')
    ax.set_title('Position Error Distribution')
    ax.axvline(np.mean(position_errors), color='red', linestyle='--',
              label=f'Mean: {np.mean(position_errors):.6f}')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Angle error histogram
    ax = axes[1, 1]
    ax.hist(angle_errors, bins=50, edgecolor='black', alpha=0.7)
    ax.set_xlabel('Angle Error (degrees)')
    ax.set_ylabel('Count')
    ax.set_title('Angle Error Distribution')
    ax.axvline(np.mean(angle_errors), color='red', linestyle='--',
              label=f'Mean: {np.mean(angle_errors):.6f}')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Add overall title
    summary = comparison_data['summary']
    fig.suptitle(f'Error Distribution Analysis\n' +
                f'{summary["num_agents_passed"]}/{summary["num_agents_compared"]} agents passed',
                fontsize=14, fontweight='bold')

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"[Visualization] ✓ Saved error distribution plot to {output_file}")

    plt.close()


def plot_polar_distribution(python_data, rtl_data, comparison_data, output_file):
    """
    Create polar plot showing agent distribution around circle.

    Args:
        python_data: Python agent data
        rtl_data: RTL agent data
        comparison_data: Comparison results
        output_file: Output PNG file path
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 7), subplot_kw=dict(projection='polar'))

    # Python agents
    ax = axes[0]
    py_angles = [a['geometry']['angle_from_center_rad'] for a in python_data['agents']]
    py_distances = [a['geometry']['distance_from_center'] for a in python_data['agents']]
    ax.scatter(py_angles, py_distances, s=10, alpha=0.5, c='blue')
    ax.set_title('Python Reference\n(Polar Coordinates)', pad=20)
    ax.set_theta_zero_location('E')
    ax.set_theta_direction(1)

    # RTL agents
    ax = axes[1]
    rtl_angles = [a['geometry']['angle_from_center_rad'] for a in rtl_data['agents']]
    rtl_distances = [a['geometry']['distance_from_center'] for a in rtl_data['agents']]

    # Color by pass/fail
    failed_indices = set([a['index'] for a in comparison_data['agents'] if not a['passed']])
    colors = ['red' if i in failed_indices else 'blue' for i in range(len(rtl_data['agents']))]

    ax.scatter(rtl_angles, rtl_distances, s=10, alpha=0.5, c=colors)
    ax.set_title('RTL Implementation\n(Polar Coordinates, red=failed)', pad=20)
    ax.set_theta_zero_location('E')
    ax.set_theta_direction(1)

    # Add overall title
    summary = comparison_data['summary']
    fig.suptitle(f'Agent Distribution (Polar View)\n' +
                f'{summary["num_agents_passed"]}/{summary["num_agents_compared"]} agents passed',
                fontsize=14, fontweight='bold')

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"[Visualization] ✓ Saved polar distribution plot to {output_file}")

    plt.close()


def main():
    parser = argparse.ArgumentParser(description='Visualize agent initialization comparison')
    parser.add_argument('--python', type=str, default='python_agent_validation.json',
                       help='Python validation JSON file')
    parser.add_argument('--rtl', type=str, default='rtl_agent_validation.json',
                       help='RTL validation JSON file')
    parser.add_argument('--comparison', type=str, default='agent_validation_report.json',
                       help='Comparison report JSON file')
    parser.add_argument('--output', type=str, default='agent_comparison.png',
                       help='Output comparison plot file')
    parser.add_argument('--output-errors', type=str, default='agent_error_distribution.png',
                       help='Output error distribution plot file')
    parser.add_argument('--output-polar', type=str, default='agent_polar_distribution.png',
                       help='Output polar distribution plot file')

    args = parser.parse_args()

    print(f"[Visualization] Loading validation data...")

    with open(args.python, 'r') as f:
        python_data = json.load(f)

    with open(args.rtl, 'r') as f:
        rtl_data = json.load(f)

    with open(args.comparison, 'r') as f:
        comparison_data = json.load(f)

    print(f"[Visualization] Creating comparison plot...")
    plot_comparison(python_data, rtl_data, comparison_data, args.output)

    print(f"[Visualization] Creating error distribution plot...")
    plot_error_distribution(comparison_data, args.output_errors)

    print(f"[Visualization] Creating polar distribution plot...")
    plot_polar_distribution(python_data, rtl_data, comparison_data, args.output_polar)

    print(f"\n[Visualization] ✓ All plots created successfully!")


if __name__ == '__main__':
    main()
