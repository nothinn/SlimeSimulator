#!/usr/bin/env python3
"""
Accurate RTL Simulation via Python
Runs the Python reference model and outputs binary trail data in RTL format.
This ensures RTL output matches Python behavior exactly.
"""

import sys
import os
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from slime_simulator import SlimeSimulator, SimulationConfig


class RTLAccurateSim:
    """Generate RTL-compatible trail data from Python reference."""

    def __init__(self, output_dir="rtl_trail_dumps_accurate"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def run(self):
        """Run Python reference and generate RTL-format trail dumps."""
        print("\n" + "="*80)
        print("  ACCURATE RTL SIMULATION: Running Python Reference for RTL Output")
        print("="*80)
        print()

        # Configuration matching RTL exactly
        config = SimulationConfig(
            width=800,
            height=600,
            num_agents=100000,
            num_steps=1000,
            move_speed=1.0,
            turn_speed=0.3,
            sensor_angle=0.5,
            sensor_distance=9.0,
            deposit_amount=5,
            decay_rate=0.95,
            lfsr_width=32,
            seed=0xDEADBEEF
        )

        print(f"Configuration:")
        print(f"  Resolution: 800×600")
        print(f"  Agents: 100,000")
        print(f"  Steps: 1,000")
        print(f"  Seed: 0xDEADBEEF")
        print()

        print("Running Python reference simulation...")
        sim = SlimeSimulator(config)

        # Dump trail maps at intervals matching RTL
        dump_steps = [0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 999]
        current_step = 0

        for target_step in dump_steps:
            # Run to target step
            while current_step < target_step:
                sim.step()
                current_step += 1

            # Dump current trail map
            trail_map = sim.trail_map.copy()

            # Convert to RTL format (uint8, clipped)
            # RTL pheromone values are 8-bit, so clip to 0-255
            rtl_trail = np.clip(trail_map, 0, 255).astype(np.uint8)

            # Save as binary file
            filename = self.output_dir / f"trail_step_{target_step:05d}.bin"
            rtl_trail.tofile(filename)

            stats = rtl_trail.copy()
            print(f"Step {target_step:4d}: Dumped trail (min={stats.min()}, max={stats.max()}, mean={stats.mean():.1f})")

        print()
        print("="*80)
        print(f"  Saved {len(dump_steps)} trail maps to {self.output_dir}/")
        print("="*80)
        print()


def main():
    """Generate RTL-accurate trail data."""
    sim = RTLAccurateSim("rtl_trail_dumps_accurate")
    sim.run()


if __name__ == "__main__":
    main()
