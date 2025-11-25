#!/usr/bin/env python3
"""
Python Reference Model for RTL Comparison

This module provides the same LFSR, Fixed-Point, and TrigLUT implementations
used in the RTL, allowing direct comparison of simulation results.
"""

import numpy as np
import math
from pathlib import Path


class LFSR:
    """LFSR matching RTL implementation."""

    TAPS = {
        8:  [8, 6, 5, 4],
        16: [16, 15, 13, 4],
        24: [24, 23, 22, 17],
        32: [32, 22, 2, 1],
        48: [48, 47, 21, 20],
        64: [64, 63, 61, 60],
    }

    def __init__(self, width: int = 32, seed: int = 0xDEADBEEF):
        if width not in self.TAPS:
            raise ValueError(f"LFSR width must be one of {list(self.TAPS.keys())}")

        self.width = width
        self.mask = (1 << width) - 1
        self.state = seed & self.mask
        if self.state == 0:
            self.state = 1
        self.taps = self.TAPS[width]

    def step(self) -> int:
        """Advance LFSR by one step - matches RTL exactly."""
        feedback = 0
        for tap in self.taps:
            feedback ^= (self.state >> (self.width - tap)) & 1

        self.state = ((self.state << 1) | feedback) & self.mask
        return self.state

    def get_state(self) -> int:
        return self.state


class FixedPoint:
    """Fixed-point arithmetic matching RTL implementation."""

    def __init__(self, int_bits: int = 12, frac_bits: int = 12):
        self.int_bits = int_bits
        self.frac_bits = frac_bits
        self.total_bits = int_bits + frac_bits + 1  # +1 for sign
        self.scale = 1 << frac_bits
        self.max_val = (1 << (self.total_bits - 1)) - 1
        self.min_val = -(1 << (self.total_bits - 1))
        self.mask = (1 << self.total_bits) - 1

    def to_fixed(self, f: float) -> int:
        """Convert float to fixed-point."""
        val = int(round(f * self.scale))
        # Handle overflow
        if val > self.max_val:
            val = self.max_val
        elif val < self.min_val:
            val = self.min_val
        return val & self.mask

    def from_fixed(self, fp: int) -> float:
        """Convert fixed-point to float."""
        # Sign extend if needed
        if fp >= (1 << (self.total_bits - 1)):
            fp -= (1 << self.total_bits)
        return fp / self.scale

    def multiply(self, a: int, b: int) -> int:
        """Fixed-point multiplication matching RTL."""
        # Sign extend operands
        if a >= (1 << (self.total_bits - 1)):
            a_signed = a - (1 << self.total_bits)
        else:
            a_signed = a

        if b >= (1 << (self.total_bits - 1)):
            b_signed = b - (1 << self.total_bits)
        else:
            b_signed = b

        # Multiply and shift
        result = (a_signed * b_signed) >> self.frac_bits
        return result & self.mask


class TrigLUT:
    """Trig lookup table matching RTL implementation."""

    def __init__(self, addr_bits: int = 10, frac_bits: int = 12):
        self.table_size = 1 << addr_bits
        self.frac_bits = frac_bits
        self.scale = 1 << frac_bits
        self.addr_mask = self.table_size - 1

        # Generate tables (same as gen_trig_lut.py)
        self.sin_table = np.zeros(self.table_size, dtype=np.int32)
        self.cos_table = np.zeros(self.table_size, dtype=np.int32)

        for i in range(self.table_size):
            angle = 2.0 * math.pi * i / self.table_size
            sin_val = int(round(math.sin(angle) * self.scale))
            cos_val = int(round(math.cos(angle) * self.scale))

            # Two's complement for 25-bit
            if sin_val < 0:
                sin_val = (1 << 25) + sin_val
            if cos_val < 0:
                cos_val = (1 << 25) + cos_val

            self.sin_table[i] = sin_val
            self.cos_table[i] = cos_val

    def sin(self, idx: int) -> int:
        return int(self.sin_table[idx & self.addr_mask])

    def cos(self, idx: int) -> int:
        return int(self.cos_table[idx & self.addr_mask])


class SlimeAgent:
    """Single slime agent matching RTL implementation."""

    def __init__(self, x: int, y: int, angle: int, fp: FixedPoint):
        self.x = x  # Fixed-point position
        self.y = y
        self.angle = angle  # 10-bit angle index (0-1023)
        self.fp = fp


class SlimeSimulatorReference:
    """
    Reference slime simulator for RTL comparison.
    Uses exact same algorithms as RTL implementation.
    """

    def __init__(self, width: int = 640, height: int = 480, num_agents: int = 1000,
                 int_bits: int = 12, frac_bits: int = 12, lfsr_seed: int = 0xDEADBEEF):
        self.width = width
        self.height = height
        self.num_agents = num_agents

        # Fixed-point arithmetic
        self.fp = FixedPoint(int_bits, frac_bits)

        # LFSR for deterministic random
        self.lfsr = LFSR(32, lfsr_seed)

        # Trig lookup table
        self.trig = TrigLUT(10, frac_bits)

        # Trail map (8-bit intensity per pixel)
        self.trail_map = np.zeros((height, width), dtype=np.uint8)

        # Parameters (fixed-point)
        self.move_speed = self.fp.to_fixed(1.0)
        self.turn_speed = self.fp.to_fixed(0.3)
        self.sensor_angle = self.fp.to_fixed(0.5)  # ~30 degrees
        self.sensor_distance = self.fp.to_fixed(9.0)
        self.deposit_amount = 5
        self.decay_rate = self.fp.to_fixed(0.95)

        # Agents
        self.agents = []

    def init_agents_center(self):
        """Initialize agents at center, pointing outward."""
        self.agents = []
        center_x = self.fp.to_fixed(self.width / 2)
        center_y = self.fp.to_fixed(self.height / 2)

        for i in range(self.num_agents):
            # Random angle (0-1023)
            self.lfsr.step()
            angle = self.lfsr.state & 0x3FF  # 10-bit angle

            self.agents.append(SlimeAgent(center_x, center_y, angle, self.fp))

    def init_agents_random(self):
        """Initialize agents at random positions."""
        self.agents = []

        for i in range(self.num_agents):
            # Random position
            self.lfsr.step()
            x = self.fp.to_fixed((self.lfsr.state & 0xFFFF) % self.width)

            self.lfsr.step()
            y = self.fp.to_fixed((self.lfsr.state & 0xFFFF) % self.height)

            self.lfsr.step()
            angle = self.lfsr.state & 0x3FF

            self.agents.append(SlimeAgent(x, y, angle, self.fp))

    def sense(self, agent: SlimeAgent, angle_offset: int) -> int:
        """Sense trail at given angle offset from agent direction."""
        # Calculate sensor position
        sensor_angle = (agent.angle + angle_offset) & 0x3FF

        sin_val = self.trig.sin(sensor_angle)
        cos_val = self.trig.cos(sensor_angle)

        # sensor_x = agent.x + cos(angle) * distance
        dx = self.fp.multiply(cos_val, self.sensor_distance)
        dy = self.fp.multiply(sin_val, self.sensor_distance)

        sensor_x = (agent.x + dx) & self.fp.mask
        sensor_y = (agent.y + dy) & self.fp.mask

        # Convert to pixel coordinates
        px = self.fp.from_fixed(sensor_x)
        py = self.fp.from_fixed(sensor_y)

        # Bounds check
        px = int(px) % self.width
        py = int(py) % self.height

        return int(self.trail_map[py, px])

    def update_agent(self, agent: SlimeAgent):
        """Update single agent (sense, turn, move, deposit)."""
        # Sense in three directions
        sense_forward = self.sense(agent, 0)

        # Convert sensor_angle from fixed to angle index offset
        # sensor_angle is ~0.5 radians, table has 1024 entries for 2*pi
        # 0.5 / (2*pi) * 1024 ≈ 81
        angle_offset = 81

        sense_left = self.sense(agent, angle_offset)
        sense_right = self.sense(agent, -angle_offset & 0x3FF)

        # Turn based on sensing
        # turn_amount in angle indices: turn_speed * some_factor
        turn_amount = 10  # ~6 degrees per step

        if sense_forward > sense_left and sense_forward > sense_right:
            # Continue straight
            pass
        elif sense_forward < sense_left and sense_forward < sense_right:
            # Random turn
            self.lfsr.step()
            if self.lfsr.state & 1:
                agent.angle = (agent.angle + turn_amount) & 0x3FF
            else:
                agent.angle = (agent.angle - turn_amount) & 0x3FF
        elif sense_left > sense_right:
            agent.angle = (agent.angle + turn_amount) & 0x3FF
        else:
            agent.angle = (agent.angle - turn_amount) & 0x3FF

        # Move forward
        sin_val = self.trig.sin(agent.angle)
        cos_val = self.trig.cos(agent.angle)

        dx = self.fp.multiply(cos_val, self.move_speed)
        dy = self.fp.multiply(sin_val, self.move_speed)

        new_x = (agent.x + dx) & self.fp.mask
        new_y = (agent.y + dy) & self.fp.mask

        # Convert to pixels and wrap
        px = int(self.fp.from_fixed(new_x)) % self.width
        py = int(self.fp.from_fixed(new_y)) % self.height

        # Update position (wrap to valid range)
        agent.x = self.fp.to_fixed(px)
        agent.y = self.fp.to_fixed(py)

        # Deposit trail
        self.trail_map[py, px] = min(255, self.trail_map[py, px] + self.deposit_amount)

    def diffuse_and_decay(self):
        """Apply diffusion and decay to trail map."""
        # Simple 3x3 box blur
        kernel = np.array([[1, 1, 1],
                           [1, 1, 1],
                           [1, 1, 1]], dtype=np.float32) / 9.0

        blurred = np.zeros_like(self.trail_map, dtype=np.float32)

        # Manual convolution (to match simple RTL implementation)
        for y in range(self.height):
            for x in range(self.width):
                total = 0
                for ky in range(-1, 2):
                    for kx in range(-1, 2):
                        ny = (y + ky) % self.height
                        nx = (x + kx) % self.width
                        total += self.trail_map[ny, nx]
                blurred[y, x] = total / 9.0

        # Apply decay
        decay_factor = self.fp.from_fixed(self.decay_rate)
        self.trail_map = (blurred * decay_factor).astype(np.uint8)

    def step(self):
        """Run one simulation step."""
        for agent in self.agents:
            self.update_agent(agent)
        self.diffuse_and_decay()

    def run(self, num_steps: int):
        """Run simulation for given number of steps."""
        for _ in range(num_steps):
            self.step()

    def get_trail_map(self) -> np.ndarray:
        """Get trail map as numpy array."""
        return self.trail_map.copy()

    def dump_trail_map(self, filename: str):
        """Dump trail map to binary file for comparison."""
        self.trail_map.tofile(filename)
        print(f"Dumped trail map to {filename} ({self.trail_map.size} bytes)")

    def dump_state(self, filename: str):
        """Dump full state for RTL comparison."""
        with open(filename, 'w') as f:
            f.write(f"# Slime Simulator State Dump\n")
            f.write(f"# Width: {self.width}, Height: {self.height}\n")
            f.write(f"# Agents: {self.num_agents}\n")
            f.write(f"# LFSR State: 0x{self.lfsr.state:08X}\n\n")

            f.write("# Agent states (x, y, angle) in fixed-point\n")
            for i, agent in enumerate(self.agents):
                f.write(f"{agent.x:08X} {agent.y:08X} {agent.angle:03X}\n")

        print(f"Dumped state to {filename}")


def generate_reference_trail(num_steps: int = 100, output_file: str = "reference_trail.bin"):
    """Generate reference trail map for RTL comparison."""
    sim = SlimeSimulatorReference(
        width=640, height=480, num_agents=1000,
        lfsr_seed=0xDEADBEEF
    )
    sim.init_agents_center()
    sim.run(num_steps)
    sim.dump_trail_map(output_file)
    return sim.get_trail_map()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Generate reference data for RTL comparison')
    parser.add_argument('-n', '--steps', type=int, default=100, help='Number of simulation steps')
    parser.add_argument('-o', '--output', default='reference_trail.bin', help='Output file')
    parser.add_argument('--state', help='Also dump state to this file')

    args = parser.parse_args()

    sim = SlimeSimulatorReference(lfsr_seed=0xDEADBEEF)
    sim.init_agents_center()
    sim.run(args.steps)
    sim.dump_trail_map(args.output)

    if args.state:
        sim.dump_state(args.state)
