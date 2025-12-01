#!/usr/bin/env python3
"""
Dump Python simulator agent state at each step for trajectory analysis.
"""

import json
import os
import sys
import argparse
from pathlib import Path
from dataclasses import dataclass
from slime_simulator import SlimeSimulator, SimulationConfig

@dataclass
class Config:
    width: int = 320
    height: int = 240
    num_agents: int = 100
    steps: int = 100
    seed: int = 0xDEADBEEF
    output_dir: str = os.environ.get('PYTHON_AGENT_DUMPS_DIR', 'python_agent_dumps')

def dump_agent_state(sim: SlimeSimulator, step: int, output_dir: str):
    """Dump agent state to JSON file."""
    agent_data = {
        'step': step,
        'agents': []
    }

    FP_SCALE = 4096  # Q12.12 format
    import math

    for i in range(len(sim.x)):
        x_fp = int(sim.x[i])
        y_fp = int(sim.y[i])
        angle_fp = int(sim.angles[i])

        # Convert to pixels and degrees
        x_px = x_fp / FP_SCALE
        y_px = y_fp / FP_SCALE
        angle_deg = (angle_fp * 180.0) / (math.pi * FP_SCALE)

        # Normalize angle to [0, 360)
        while angle_deg < 0:
            angle_deg += 360.0
        while angle_deg >= 360.0:
            angle_deg -= 360.0

        agent_data['agents'].append({
            'agent_id': i,
            'x_fp': x_fp,
            'y_fp': y_fp,
            'angle_fp': angle_fp,
            'x_px': round(x_px, 4),
            'y_px': round(y_px, 4),
            'angle_deg': round(angle_deg, 6)
        })

    # Write to file
    filename = os.path.join(output_dir, f'agent_state_step_{step:05d}.json')
    os.makedirs(output_dir, exist_ok=True)

    with open(filename, 'w') as f:
        json.dump(agent_data, f, indent=2)

    return filename

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Dump Python simulator agent states at each step")
    parser.add_argument("--width", type=int, default=320, help="Simulation width (default: 320)")
    parser.add_argument("--height", type=int, default=240, help="Simulation height (default: 240)")
    parser.add_argument("--agents", type=int, default=100, help="Number of agents (default: 100)")
    parser.add_argument("--steps", type=int, default=100, help="Number of simulation steps (default: 100)")
    parser.add_argument("--seed", type=lambda x: int(x, 0), default=0xDEADBEEF, help="Random seed (default: 0xDEADBEEF)")

    args = parser.parse_args()

    cfg = Config(
        width=args.width,
        height=args.height,
        num_agents=args.agents,
        steps=args.steps,
        seed=args.seed,
        output_dir=os.environ.get('PYTHON_AGENT_DUMPS_DIR', 'python_agent_dumps')
    )

    print(f"Creating Python simulator...")
    print(f"  Resolution: {cfg.width}×{cfg.height}")
    print(f"  Agents: {cfg.num_agents}")
    print(f"  Steps: {cfg.steps}")
    print(f"  Seed: 0x{cfg.seed:X}")
    print()

    # Create simulator config
    sim_config = SimulationConfig(
        width=cfg.width,
        height=cfg.height,
        num_agents=cfg.num_agents,
        seed=cfg.seed
    )

    # Create simulator
    sim = SlimeSimulator(sim_config)

    # Create output directory
    os.makedirs(cfg.output_dir, exist_ok=True)

    # Dump initial state (step 0)
    print(f"Step 0: Dumping initial agent state...")
    dump_agent_state(sim, 0, cfg.output_dir)

    # Run simulation and dump state at each step
    for step in range(1, cfg.steps + 1):
        sim.step()

        if step % 10 == 0 or step == cfg.steps:
            print(f"Step {step}/{cfg.steps}: Dumping agent state ({step*100//cfg.steps}%)")

        dump_agent_state(sim, step, cfg.output_dir)

    print()
    print(f"✓ Complete! {cfg.steps + 1} agent state files in {cfg.output_dir}/")
    print(f"  Format: agent_state_step_XXXXX.json")

if __name__ == '__main__':
    main()
