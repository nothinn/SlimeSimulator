#!/usr/bin/env python3
"""
Agent Trajectory Visualizer

Interactive visualization tool for analyzing agent trajectories in the SlimeSimulator project.
Compares Python reference implementation vs RTL simulation results.

Usage:
    python3 agent_trajectory_visualizer.py [csv_file]

    If no CSV file is provided, defaults to 'agent_comparison.csv' in current directory.

Features:
    - Step through simulation frames (if multi-step data available)
    - Toggle Python/RTL agent visibility
    - View agent positions, vectors, and angles
    - Compare position/angle differences
    - Keyboard shortcuts: Left/Right arrows for navigation

Input CSV Format:
    Agent,Python_X,Python_Y,Python_Angle_Deg,RTL_X,RTL_Y,RTL_Angle_Deg,X_Diff,Y_Diff,Angle_Diff

Author: Generated for SlimeSimulator project
"""

import sys
import matplotlib
# Set interactive backend BEFORE importing pyplot
try:
    # Try to use TkAgg (works on most systems)
    matplotlib.use('TkAgg')
except Exception:
    try:
        # Fallback to Qt5Agg
        matplotlib.use('Qt5Agg')
    except Exception:
        try:
            # Fallback to wxAgg
            matplotlib.use('wxAgg')
        except Exception:
            # Final fallback - let matplotlib choose
            pass

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, CheckButtons
from matplotlib.patches import Circle, FancyArrow
import argparse


class AgentTrajectoryVisualizer:
    def __init__(self, csv_file='agent_comparison.csv', width=320, height=240):
        """
        Initialize the agent trajectory visualizer.

        Args:
            csv_file: Path to CSV file with agent data
            width: Canvas width in pixels (default 320)
            height: Canvas height in pixels (default 240)
        """
        self.width = width
        self.height = height
        self.spawn_radius = min(width, height) * 0.4  # 40% of smaller dimension

        # Load data
        self.load_data(csv_file)

        # Visualization state
        self.current_step = 0
        self.show_python = True
        self.show_rtl = True
        self.show_vectors = True
        self.show_spawn_circle = True

        # Create figure and setup UI
        self.setup_figure()
        self.draw_frame()

    def load_data(self, csv_file):
        """Load agent trajectory data from CSV file."""
        try:
            # Load CSV with numpy
            with open(csv_file, 'r') as f:
                header_line = f.readline().strip()
                self.column_names = header_line.split(',')

            # Load data (skip header)
            raw_data = np.genfromtxt(csv_file, delimiter=',', skip_header=1)

            # Create dictionary to store data by column name
            self.data = {}
            for i, col_name in enumerate(self.column_names):
                self.data[col_name] = raw_data[:, i]

            num_rows = raw_data.shape[0]
            print(f"Loaded {num_rows} agents from {csv_file}")

            # Check if this is multi-step data (has Step column)
            if 'Step' in self.column_names:
                self.steps = sorted(np.unique(self.data['Step']).astype(int))
                self.num_steps = len(self.steps)
                print(f"Multi-step data: {self.num_steps} steps")
            else:
                # Single step initialization data
                self.data['Step'] = np.zeros(num_rows)
                self.steps = [0]
                self.num_steps = 1
                print("Single-step initialization data")

            # Get agent count (agents in first step)
            first_step_mask = self.data['Step'] == self.steps[0]
            self.num_agents = np.sum(first_step_mask)
            print(f"Number of agents: {self.num_agents}")

        except Exception as e:
            print(f"Error loading CSV file: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    def setup_figure(self):
        """Create matplotlib figure with interactive controls."""
        self.fig = plt.figure(figsize=(16, 10))
        self.fig.canvas.manager.set_window_title('Agent Trajectory Visualizer')

        # Main canvas for agent visualization
        self.ax_canvas = plt.subplot2grid((10, 12), (0, 0), colspan=9, rowspan=10)
        self.ax_canvas.set_xlim(0, self.width)
        self.ax_canvas.set_ylim(0, self.height)
        self.ax_canvas.set_aspect('equal')
        self.ax_canvas.set_xlabel('X Position (pixels)')
        self.ax_canvas.set_ylabel('Y Position (pixels)')
        self.ax_canvas.grid(True, alpha=0.3)
        self.ax_canvas.invert_yaxis()  # Screen coordinates (origin top-left)

        # Control panel area
        control_col = 9

        # Step navigation buttons
        ax_prev = plt.subplot2grid((10, 12), (0, control_col), colspan=3)
        ax_next = plt.subplot2grid((10, 12), (1, control_col), colspan=3)
        self.btn_prev = Button(ax_prev, '◄ Previous Step')
        self.btn_next = Button(ax_next, 'Next Step ►')
        self.btn_prev.on_clicked(self.prev_step)
        self.btn_next.on_clicked(self.next_step)

        # Toggle checkboxes
        ax_toggles = plt.subplot2grid((10, 12), (3, control_col), colspan=3, rowspan=2)
        ax_toggles.axis('off')
        self.check_visibility = CheckButtons(
            ax_toggles,
            ['Show Python', 'Show RTL', 'Show Vectors', 'Spawn Circle'],
            [self.show_python, self.show_rtl, self.show_vectors, self.show_spawn_circle]
        )
        self.check_visibility.on_clicked(self.toggle_visibility)

        # Info panel
        ax_info = plt.subplot2grid((10, 12), (6, control_col), colspan=3, rowspan=4)
        ax_info.axis('off')
        self.ax_info = ax_info

        # Keyboard event handling
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)

    def get_current_data(self):
        """Get agent data for current step."""
        step_value = self.steps[self.current_step]
        mask = self.data['Step'] == step_value

        # Return dictionary with filtered data for current step
        current_data = {}
        for col_name, col_data in self.data.items():
            current_data[col_name] = col_data[mask]

        return current_data

    def draw_frame(self):
        """Draw the current frame with agents and vectors."""
        self.ax_canvas.clear()
        self.ax_canvas.set_xlim(0, self.width)
        self.ax_canvas.set_ylim(0, self.height)
        self.ax_canvas.set_aspect('equal')
        self.ax_canvas.set_xlabel('X Position (pixels)')
        self.ax_canvas.set_ylabel('Y Position (pixels)')
        self.ax_canvas.grid(True, alpha=0.3)
        self.ax_canvas.invert_yaxis()

        # Draw spawn circle
        if self.show_spawn_circle:
            spawn_circle = Circle(
                (self.width/2, self.height/2),
                self.spawn_radius,
                fill=False,
                edgecolor='gray',
                linestyle='--',
                linewidth=2,
                alpha=0.5,
                label='Spawn Circle'
            )
            self.ax_canvas.add_patch(spawn_circle)

        # Get current step data
        data = self.get_current_data()

        # Vector length for visualization (pixels)
        vector_length = 10

        # Draw Python agents
        if self.show_python and 'Python_X' in data:
            python_x = data['Python_X']
            python_y = data['Python_Y']
            python_angle = data['Python_Angle_Deg']

            # Plot positions
            self.ax_canvas.scatter(
                python_x, python_y,
                c='red',
                s=30,
                alpha=0.6,
                marker='o',
                label='Python Agents',
                zorder=3
            )

            # Draw vectors if enabled
            if self.show_vectors:
                for x, y, angle in zip(python_x, python_y, python_angle):
                    # Convert angle to radians and compute vector components
                    angle_rad = np.deg2rad(angle)
                    dx = vector_length * np.cos(angle_rad)
                    dy = vector_length * np.sin(angle_rad)

                    arrow = FancyArrow(
                        x, y, dx, dy,
                        width=1.5,
                        head_width=3,
                        head_length=2,
                        fc='orange',
                        ec='orange',
                        alpha=0.5,
                        zorder=2
                    )
                    self.ax_canvas.add_patch(arrow)

        # Draw RTL agents
        if self.show_rtl and 'RTL_X' in data:
            rtl_x = data['RTL_X']
            rtl_y = data['RTL_Y']
            rtl_angle = data['RTL_Angle_Deg']

            # Plot positions
            self.ax_canvas.scatter(
                rtl_x, rtl_y,
                c='cyan',
                s=30,
                alpha=0.6,
                marker='s',
                label='RTL Agents',
                zorder=3
            )

            # Draw vectors if enabled
            if self.show_vectors:
                for x, y, angle in zip(rtl_x, rtl_y, rtl_angle):
                    # Convert angle to radians and compute vector components
                    angle_rad = np.deg2rad(angle)
                    dx = vector_length * np.cos(angle_rad)
                    dy = vector_length * np.sin(angle_rad)

                    arrow = FancyArrow(
                        x, y, dx, dy,
                        width=1.5,
                        head_width=3,
                        head_length=2,
                        fc='blue',
                        ec='blue',
                        alpha=0.5,
                        zorder=2
                    )
                    self.ax_canvas.add_patch(arrow)

        # Add legend
        self.ax_canvas.legend(loc='upper right', fontsize=8)

        # Update title with step info
        title = f'Step {self.current_step + 1}/{self.num_steps}'
        if self.num_steps == 1:
            title = 'Agent Initialization'
        self.ax_canvas.set_title(title, fontsize=14, fontweight='bold')

        # Update info panel
        self.update_info_panel(data)

        # Redraw
        self.fig.canvas.draw_idle()

    def update_info_panel(self, data):
        """Update the information panel with statistics."""
        self.ax_info.clear()
        self.ax_info.axis('off')

        # Calculate statistics
        if 'X_Diff' in data:
            x_diff = data['X_Diff']
            y_diff = data['Y_Diff']
            angle_diff = data['Angle_Diff']

            mean_x_diff = np.mean(x_diff)
            mean_y_diff = np.mean(y_diff)
            mean_angle_diff = np.mean(angle_diff)
            max_x_diff = np.max(x_diff)
            max_y_diff = np.max(y_diff)
            max_angle_diff = np.max(angle_diff)

            # Euclidean distance
            distances = np.sqrt(x_diff**2 + y_diff**2)
            mean_distance = np.mean(distances)
            max_distance = np.max(distances)
        else:
            mean_x_diff = mean_y_diff = mean_angle_diff = 0
            max_x_diff = max_y_diff = max_angle_diff = 0
            mean_distance = max_distance = 0

        # Create info text
        info_text = f"""
SIMULATION INFO
━━━━━━━━━━━━━━━━━━━
Canvas: {self.width}×{self.height}
Agents: {self.num_agents}
Step: {self.current_step + 1}/{self.num_steps}

SPAWN PATTERN
━━━━━━━━━━━━━━━━━━━
Circle Radius: {self.spawn_radius:.1f} px
Center: ({self.width/2:.1f}, {self.height/2:.1f})

POSITION DIFFERENCES
━━━━━━━━━━━━━━━━━━━
Mean X Δ: {mean_x_diff:.3f} px
Mean Y Δ: {mean_y_diff:.3f} px
Mean Dist: {mean_distance:.3f} px

Max X Δ: {max_x_diff:.3f} px
Max Y Δ: {max_y_diff:.3f} px
Max Dist: {max_distance:.3f} px

ANGLE DIFFERENCES
━━━━━━━━━━━━━━━━━━━
Mean: {mean_angle_diff:.3f}°
Max: {max_angle_diff:.3f}°

CONTROLS
━━━━━━━━━━━━━━━━━━━
← → : Navigate steps
Checkboxes: Toggle views
        """

        self.ax_info.text(
            0.05, 0.95, info_text,
            transform=self.ax_info.transAxes,
            fontsize=9,
            verticalalignment='top',
            family='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3)
        )

    def toggle_visibility(self, label):
        """Toggle visibility of different elements."""
        if label == 'Show Python':
            self.show_python = not self.show_python
        elif label == 'Show RTL':
            self.show_rtl = not self.show_rtl
        elif label == 'Show Vectors':
            self.show_vectors = not self.show_vectors
        elif label == 'Spawn Circle':
            self.show_spawn_circle = not self.show_spawn_circle

        self.draw_frame()

    def next_step(self, event=None):
        """Navigate to next step."""
        if self.current_step < self.num_steps - 1:
            self.current_step += 1
            self.draw_frame()

    def prev_step(self, event=None):
        """Navigate to previous step."""
        if self.current_step > 0:
            self.current_step -= 1
            self.draw_frame()

    def on_key_press(self, event):
        """Handle keyboard shortcuts."""
        if event.key == 'right':
            self.next_step()
        elif event.key == 'left':
            self.prev_step()
        elif event.key == 'q':
            plt.close(self.fig)

    def show(self):
        """Display the visualization."""
        plt.tight_layout()
        plt.show()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Interactive agent trajectory visualizer for SlimeSimulator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 agent_trajectory_visualizer.py
    python3 agent_trajectory_visualizer.py agent_comparison.csv
    python3 agent_trajectory_visualizer.py --width 640 --height 480 trace_data.csv

Keyboard Shortcuts:
    Left Arrow  - Previous step
    Right Arrow - Next step
    Q           - Quit
        """
    )
    parser.add_argument(
        'csv_file',
        nargs='?',
        default='agent_comparison.csv',
        help='Path to CSV file with agent data (default: agent_comparison.csv)'
    )
    parser.add_argument(
        '--width',
        type=int,
        default=320,
        help='Canvas width in pixels (default: 320)'
    )
    parser.add_argument(
        '--height',
        type=int,
        default=240,
        help='Canvas height in pixels (default: 240)'
    )

    args = parser.parse_args()

    # Check if file exists
    import os
    if not os.path.exists(args.csv_file):
        print(f"Error: File '{args.csv_file}' not found")
        sys.exit(1)

    # Create and show visualizer
    print("=" * 60)
    print("Agent Trajectory Visualizer")
    print("=" * 60)

    viz = AgentTrajectoryVisualizer(
        csv_file=args.csv_file,
        width=args.width,
        height=args.height
    )

    print("\nVisualization ready. Close window or press 'Q' to exit.")
    print("=" * 60)

    viz.show()


if __name__ == '__main__':
    main()
