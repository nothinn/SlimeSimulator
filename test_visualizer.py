#!/usr/bin/env python3
"""
Test script to verify the agent trajectory visualizer loads data correctly.
"""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for testing

import sys
import numpy as np

# Import the visualizer
sys.path.insert(0, '/home/reson/SlimeSimulator')

# Mock the show() method to prevent GUI from launching
import matplotlib.pyplot as plt
original_show = plt.show
plt.show = lambda: print("Plot would be displayed here (GUI suppressed for testing)")

from agent_trajectory_visualizer import AgentTrajectoryVisualizer

def test_visualizer():
    """Test that visualizer loads and initializes correctly."""
    print("Testing Agent Trajectory Visualizer...")
    print("=" * 60)

    try:
        # Create visualizer instance
        viz = AgentTrajectoryVisualizer(
            csv_file='/home/reson/SlimeSimulator/agent_comparison.csv',
            width=320,
            height=240
        )

        print(f"\nVisualization state:")
        print(f"  Current step: {viz.current_step}")
        print(f"  Total steps: {viz.num_steps}")
        print(f"  Number of agents: {viz.num_agents}")
        print(f"  Canvas size: {viz.width}x{viz.height}")
        print(f"  Spawn radius: {viz.spawn_radius:.2f}")

        # Get current data
        data = viz.get_current_data()
        print(f"\nData columns: {list(data.keys())}")

        if 'Python_X' in data:
            print(f"\nPython agent data:")
            print(f"  X range: [{np.min(data['Python_X']):.2f}, {np.max(data['Python_X']):.2f}]")
            print(f"  Y range: [{np.min(data['Python_Y']):.2f}, {np.max(data['Python_Y']):.2f}]")
            print(f"  Angle range: [{np.min(data['Python_Angle_Deg']):.2f}, {np.max(data['Python_Angle_Deg']):.2f}]")

        if 'RTL_X' in data:
            print(f"\nRTL agent data:")
            print(f"  X range: [{np.min(data['RTL_X']):.2f}, {np.max(data['RTL_X']):.2f}]")
            print(f"  Y range: [{np.min(data['RTL_Y']):.2f}, {np.max(data['RTL_Y']):.2f}]")
            print(f"  Angle range: [{np.min(data['RTL_Angle_Deg']):.2f}, {np.max(data['RTL_Angle_Deg']):.2f}]")

        if 'X_Diff' in data:
            print(f"\nDifferences:")
            print(f"  Mean X diff: {np.mean(data['X_Diff']):.3f} px")
            print(f"  Mean Y diff: {np.mean(data['Y_Diff']):.3f} px")
            print(f"  Mean angle diff: {np.mean(data['Angle_Diff']):.3f}°")
            distances = np.sqrt(data['X_Diff']**2 + data['Y_Diff']**2)
            print(f"  Mean Euclidean distance: {np.mean(distances):.3f} px")
            print(f"  Max Euclidean distance: {np.max(distances):.3f} px")

        print("\n" + "=" * 60)
        print("SUCCESS: Visualizer loaded and initialized correctly!")
        return True

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_visualizer()
    sys.exit(0 if success else 1)
