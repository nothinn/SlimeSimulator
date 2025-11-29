#!/usr/bin/env python3
"""
Test multi-step trajectory visualization
"""

import matplotlib
matplotlib.use('Agg')

import sys
sys.path.insert(0, '/home/reson/SlimeSimulator')

import matplotlib.pyplot as plt
plt.show = lambda: print("Plot ready (GUI suppressed)")

from agent_trajectory_visualizer import AgentTrajectoryVisualizer

def test_multistep():
    print("Testing multi-step trajectory visualization...")
    print("=" * 60)

    viz = AgentTrajectoryVisualizer(
        csv_file='/home/reson/SlimeSimulator/example_trajectory.csv',
        width=320,
        height=240
    )

    print(f"\nMulti-step visualization:")
    print(f"  Total steps: {viz.num_steps}")
    print(f"  Agents per step: {viz.num_agents}")

    # Test stepping through frames
    for step in range(min(3, viz.num_steps)):
        viz.current_step = step
        data = viz.get_current_data()
        print(f"\nStep {step}:")
        print(f"  Agents: {len(data['Agent'])}")
        print(f"  Python X range: [{min(data['Python_X']):.1f}, {max(data['Python_X']):.1f}]")
        print(f"  Python Y range: [{min(data['Python_Y']):.1f}, {max(data['Python_Y']):.1f}]")

    print("\n" + "=" * 60)
    print("SUCCESS: Multi-step visualization works!")

if __name__ == '__main__':
    test_multistep()
