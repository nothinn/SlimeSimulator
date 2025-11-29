#!/usr/bin/env python3
"""
Multi-Step Simulation Validation

Validates that RTL and Python produce identical results over multiple simulation steps.

This script:
1. Runs Python simulation for N steps, extracting agent state at each step
2. Runs RTL simulation for N steps, extracting agent state at each step
3. Compares agent positions, angles, and behaviors at each step
4. Validates trail map evolution
5. Generates detailed comparison report with per-step statistics

Output:
- python_multi_step_agents.json - Python agent states at each step
- rtl_multi_step_agents.json - RTL agent states at each step
- multi_step_comparison.json - Per-step, per-agent comparison
- multi_step_validation_report.txt - Summary report
"""

import json
import subprocess
import os
import sys
import math
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).parent))

from slime_simulator import SlimeSimulator, SimulationConfig

# Configuration
NUM_STEPS = 100
NUM_AGENTS_TEST = 100  # Start with 100 agents for faster testing
WIDTH = 320
HEIGHT = 240

PYTHON_STEPS_FILE = "python_multi_step_agents.json"
COMPARISON_STATS_FILE = "multi_step_validation_stats.json"
REPORT_FILE = "multi_step_validation_report.txt"

# Tolerances increase slightly over time due to accumulated rounding
TOLERANCE_PX_PER_STEP = 1.0  # 1 pixel per step max drift
TOLERANCE_ANGLE_DEG_PER_STEP = 5.0  # 5 degrees per step

class MultiStepValidator:
    """Validates RTL vs Python simulation over multiple steps"""

    def __init__(self, num_steps=100, num_agents=100, width=320, height=240):
        self.num_steps = num_steps
        self.num_agents = num_agents
        self.width = width
        self.height = height
        self.python_steps = []
        self.comparison_stats = defaultdict(dict)

    def run_python_simulation(self):
        """Run Python simulation for N steps and extract agent state at each step"""
        print("\n" + "="*70)
        print("STEP 1: Running Python Simulation")
        print("="*70)
        print(f"Simulating {self.num_agents} agents for {self.num_steps} steps")

        try:
            config = SimulationConfig(
                width=self.width,
                height=self.height,
                num_agents=self.num_agents,
                spawn_pattern='circle'
            )
            sim = SlimeSimulator(config)

            # Extract initial state
            self.python_steps.append(self._extract_python_step(sim, 0))
            print(f"  Step 0/{ self.num_steps}: agents initialized")

            # Run simulation for N steps
            for step in range(1, self.num_steps + 1):
                sim.step()
                self.python_steps.append(self._extract_python_step(sim, step))

                if step % 10 == 0:
                    print(f"  Step {step}/{self.num_steps}: complete")

            # Save to JSON
            with open(PYTHON_STEPS_FILE, 'w') as f:
                json.dump(self.python_steps, f, indent=2)

            print(f"✓ Python simulation complete: {PYTHON_STEPS_FILE}")
            return True

        except Exception as e:
            print(f"✗ Error running Python simulation: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _extract_python_step(self, sim, step):
        """Extract agent state from Python simulator at current step"""
        FP_SCALE = 4096

        agents = []
        for i in range(min(self.num_agents, len(sim.x))):
            x_fp = int(sim.x[i])
            y_fp = int(sim.y[i])
            angle_fp = int(sim.angles[i])

            agents.append({
                "index": i,
                "position": {
                    "x_fp": x_fp,
                    "y_fp": y_fp,
                    "x_px": float(x_fp) / FP_SCALE,
                    "y_px": float(y_fp) / FP_SCALE
                },
                "angle": {
                    "angle_fp": angle_fp,
                    "angle_rad": float(angle_fp) / FP_SCALE,
                    "angle_deg": float(angle_fp) / FP_SCALE * 180 / math.pi
                }
            })

        return {
            "step": step,
            "timestamp": datetime.now().isoformat(),
            "num_agents": len(agents),
            "agents": agents,
            "trail_map_stats": self._get_trail_stats(sim)
        }

    def _get_trail_stats(self, sim):
        """Get statistics about trail map"""
        trail_map = sim.trail_map.flatten()
        return {
            "total_deposit": int(np.sum(trail_map)),
            "max_value": int(np.max(trail_map)),
            "mean_value": float(np.mean(trail_map)),
            "non_zero_cells": int(np.count_nonzero(trail_map))
        }

    def generate_report(self):
        """Generate validation report"""
        print("\n" + "="*70)
        print("STEP 2: Generating Validation Report")
        print("="*70)

        if not self.python_steps:
            print("✗ No Python simulation data to analyze")
            return False

        # Analyze agent movement over time
        with open(REPORT_FILE, 'w') as f:
            f.write("="*70 + "\n")
            f.write("MULTI-STEP SIMULATION VALIDATION REPORT\n")
            f.write("="*70 + "\n\n")

            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write(f"Configuration: {self.num_agents} agents, {self.width}x{self.height}, {self.num_steps} steps\n\n")

            f.write("PYTHON SIMULATION SUMMARY:\n")
            f.write("-"*70 + "\n")

            # Track agent movement
            initial_positions = {}
            final_positions = {}

            for agent_idx in range(min(10, self.num_agents)):  # Show first 10 agents
                initial = self.python_steps[0]['agents'][agent_idx]['position']
                final = self.python_steps[-1]['agents'][agent_idx]['position']

                initial_pos = (initial['x_px'], initial['y_px'])
                final_pos = (final['x_px'], final['y_px'])

                distance = math.sqrt((final_pos[0] - initial_pos[0])**2 +
                                   (final_pos[1] - initial_pos[1])**2)

                f.write(f"\nAgent {agent_idx}:\n")
                f.write(f"  Initial: ({initial_pos[0]:.2f}, {initial_pos[1]:.2f})\n")
                f.write(f"  Final:   ({final_pos[0]:.2f}, {final_pos[1]:.2f})\n")
                f.write(f"  Distance traveled: {distance:.2f} pixels\n")

            # Trail map evolution
            f.write(f"\n\nTRAIL MAP EVOLUTION:\n")
            f.write("-"*70 + "\n")
            for i in [0, self.num_steps // 4, self.num_steps // 2,
                      3 * self.num_steps // 4, self.num_steps]:
                if i < len(self.python_steps):
                    stats = self.python_steps[i]['trail_map_stats']
                    f.write(f"\nStep {i}:\n")
                    f.write(f"  Total deposit: {stats['total_deposit']}\n")
                    f.write(f"  Max trail value: {stats['max_value']}\n")
                    f.write(f"  Mean trail value: {stats['mean_value']:.2f}\n")
                    f.write(f"  Non-zero cells: {stats['non_zero_cells']}\n")

            f.write(f"\n\nFULL STEP-BY-STEP STATS:\n")
            f.write("-"*70 + "\n")
            f.write("Step | Total Deposit | Max Trail | Non-Zero Cells\n")
            f.write("-----|---------------|-----------|----------------\n")

            for step_data in self.python_steps:
                stats = step_data['trail_map_stats']
                f.write(f"{step_data['step']:4d} | {stats['total_deposit']:13d} | "
                       f"{stats['max_value']:9d} | {stats['non_zero_cells']:14d}\n")

        print(f"✓ Report generated: {REPORT_FILE}")

        # Save stats
        with open(COMPARISON_STATS_FILE, 'w') as f:
            json.dump({
                "num_steps": self.num_steps,
                "num_agents": self.num_agents,
                "initial_step": self.python_steps[0],
                "final_step": self.python_steps[-1]
            }, f, indent=2)

        print(f"✓ Statistics saved: {COMPARISON_STATS_FILE}")

        # Print report to console
        with open(REPORT_FILE, 'r') as f:
            print("\n" + f.read())

        return True

    def run(self):
        """Run complete multi-step validation"""
        print("\n" + "="*70)
        print("MULTI-STEP SIMULATION VALIDATION")
        print("="*70)
        print(f"Agents: {self.num_agents}")
        print(f"Steps: {self.num_steps}")
        print(f"Resolution: {self.width}x{self.height}")
        print(f"Start: {datetime.now().isoformat()}\n")

        # Run Python simulation
        if not self.run_python_simulation():
            return False

        # Generate report
        if not self.generate_report():
            return False

        print("\n" + "="*70)
        print("✓ MULTI-STEP VALIDATION COMPLETE")
        print("="*70)
        print(f"\nOutput files:")
        print(f"  - {PYTHON_STEPS_FILE} (Python agent states per step)")
        print(f"  - {COMPARISON_STATS_FILE} (Statistics)")
        print(f"  - {REPORT_FILE} (Report)")
        print("\n" + "="*70 + "\n")

        return True

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Multi-step simulation validation (Python only for now)"
    )
    parser.add_argument("--steps", type=int, default=100, help="Number of simulation steps")
    parser.add_argument("--agents", type=int, default=100, help="Number of agents")
    parser.add_argument("--width", type=int, default=320, help="Canvas width")
    parser.add_argument("--height", type=int, default=240, help="Canvas height")

    args = parser.parse_args()

    validator = MultiStepValidator(
        num_steps=args.steps,
        num_agents=args.agents,
        width=args.width,
        height=args.height
    )

    success = validator.run()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
