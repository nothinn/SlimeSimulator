#!/usr/bin/env python3
"""Generate reference trail data for different resolutions."""

import sys
sys.path.insert(0, 'rtl/sim')
from python_reference import SlimeSimulatorReference

# Generate for 160x120 (matches RTL memory)
print("Generating reference for 160x120...")
sim = SlimeSimulatorReference(width=160, height=120, num_agents=1000, lfsr_seed=0xDEADBEEF)
sim.init_agents_center()
sim.run(10)
sim.dump_trail_map('rtl/reference_trail_160x120_10steps.bin')
sim.dump_state('rtl/reference_state_160x120_10steps.txt')

# Also generate for 5 steps for easier comparison
print("Generating reference for 160x120, 5 steps...")
sim = SlimeSimulatorReference(width=160, height=120, num_agents=1000, lfsr_seed=0xDEADBEEF)
sim.init_agents_center()
sim.run(5)
sim.dump_trail_map('rtl/reference_trail_160x120_5steps.bin')

# And 1 step for minimal diff
print("Generating reference for 160x120, 1 step...")
sim = SlimeSimulatorReference(width=160, height=120, num_agents=1000, lfsr_seed=0xDEADBEEF)
sim.init_agents_center()
sim.run(1)
sim.dump_trail_map('rtl/reference_trail_160x120_1step.bin')

print("Done!")
