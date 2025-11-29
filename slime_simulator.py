#!/usr/bin/env python3
"""
Slime Mold (Physarum) Simulator - Fixed-Point RTL-Compatible Version

Based on:
- Sebastian Lague's video: https://www.youtube.com/watch?v=X-iSQQgOd1A
- Paper: https://uwe-repository.worktribe.com/output/980579

This simulator uses fixed-point arithmetic and LFSR-based random numbers
for exact replication in RTL simulation.
"""

import numpy as np
from PIL import Image
import os
import argparse
from dataclasses import dataclass
from scipy import ndimage

# Optional pygame import for display mode
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False


class LFSR:
    """
    Linear Feedback Shift Register for deterministic random number generation.
    Uses a maximal-length LFSR with configurable width.

    Common LFSR taps for maximal length sequences:
    - 16-bit: taps at 16, 15, 13, 4
    - 32-bit: taps at 32, 22, 2, 1
    - 64-bit: taps at 64, 63, 61, 60
    """

    # Tap positions for maximal-length LFSRs (1-indexed from MSB)
    TAPS = {
        8:  [8, 6, 5, 4],
        16: [16, 15, 13, 4],
        24: [24, 23, 22, 17],
        32: [32, 22, 2, 1],
        48: [48, 47, 21, 20],
        64: [64, 63, 61, 60],
    }

    def __init__(self, width: int = 32, seed: int = 1):
        """
        Initialize LFSR with given width and seed.

        Args:
            width: Bit width of the LFSR (must be in TAPS dict)
            seed: Initial state (must be non-zero)
        """
        if width not in self.TAPS:
            raise ValueError(f"LFSR width must be one of {list(self.TAPS.keys())}")
        if seed == 0:
            raise ValueError("LFSR seed must be non-zero")

        self.width = width
        self.mask = (1 << width) - 1
        self.state = seed & self.mask
        if self.state == 0:
            self.state = 1
        self.taps = self.TAPS[width]

    def step(self) -> int:
        """Advance LFSR by one step and return new state."""
        # Calculate feedback bit (XOR of tap positions)
        feedback = 0
        for tap in self.taps:
            feedback ^= (self.state >> (self.width - tap)) & 1

        # Shift and insert feedback
        self.state = ((self.state << 1) | feedback) & self.mask
        return self.state

    def next(self) -> int:
        """Get next random value."""
        return self.step()

    def next_n(self, n: int) -> np.ndarray:
        """Get n random values as numpy array."""
        values = np.zeros(n, dtype=np.uint64)
        for i in range(n):
            values[i] = self.step()
        return values

    def next_float(self) -> float:
        """Get next random value as float in [0, 1)."""
        return self.step() / (1 << self.width)

    def next_float_n(self, n: int) -> np.ndarray:
        """Get n random floats in [0, 1)."""
        return self.next_n(n).astype(np.float64) / (1 << self.width)

    def next_bool_n(self, n: int) -> np.ndarray:
        """Get n random booleans (uses LSB of each LFSR output)."""
        values = self.next_n(n)
        return (values & 1).astype(np.bool_)

    def get_state(self) -> int:
        """Get current LFSR state for debugging/verification."""
        return self.state

    def set_state(self, state: int):
        """Set LFSR state directly."""
        self.state = state & self.mask
        if self.state == 0:
            self.state = 1


class FixedPoint:
    """
    Fixed-point number representation and arithmetic.

    Format: Q{integer_bits}.{fractional_bits}
    Total bits = integer_bits + fractional_bits + 1 (sign bit)
    """

    def __init__(self, integer_bits: int = 12, fractional_bits: int = 12):
        """
        Initialize fixed-point configuration.

        Args:
            integer_bits: Number of bits for integer part (excluding sign)
            fractional_bits: Number of bits for fractional part
        """
        self.integer_bits = integer_bits
        self.fractional_bits = fractional_bits
        self.total_bits = integer_bits + fractional_bits + 1  # +1 for sign
        self.scale = 1 << fractional_bits
        self.max_val = (1 << (integer_bits + fractional_bits)) - 1
        self.min_val = -(1 << (integer_bits + fractional_bits))

    def to_fixed(self, value: float) -> int:
        """Convert float to fixed-point integer representation."""
        return int(round(value * self.scale))

    def to_fixed_array(self, values: np.ndarray) -> np.ndarray:
        """Convert float array to fixed-point integer array."""
        return np.round(values * self.scale).astype(np.int64)

    def from_fixed(self, value: int) -> float:
        """Convert fixed-point integer to float."""
        return value / self.scale

    def from_fixed_array(self, values: np.ndarray) -> np.ndarray:
        """Convert fixed-point integer array to float array."""
        return values.astype(np.float64) / self.scale

    def multiply(self, a: int, b: int) -> int:
        """Fixed-point multiplication with proper scaling.

        Properly handles signed arithmetic for operands that may be stored as
        unsigned 2's complement (e.g., from TrigLUT).
        """
        # Sign-extend operands (25-bit to 64-bit signed)
        a_signed = self._to_signed_25bit(a)
        b_signed = self._to_signed_25bit(b)

        # Multiply and shift right by fractional bits
        result = (a_signed * b_signed) >> self.fractional_bits
        return result

    def multiply_array(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Fixed-point array multiplication.

        Properly handles signed arithmetic for operands that may be stored as
        unsigned 2's complement (e.g., from TrigLUT).
        """
        # Sign-extend operands (25-bit to 64-bit signed)
        a_signed = np.where(a >= (1 << 24), a - (1 << 25), a).astype(np.int64)
        b_signed = np.where(b >= (1 << 24), b - (1 << 25), b).astype(np.int64)

        # Multiply and shift right by fractional bits
        result = (a_signed * b_signed) >> self.fractional_bits
        return result.astype(np.int64)

    def _to_signed_25bit(self, val: int) -> int:
        """Convert 25-bit unsigned 2's complement to signed int."""
        if val >= (1 << 24):
            return val - (1 << 25)
        return val

    def divide(self, a: int, b: int) -> int:
        """Fixed-point division with proper scaling."""
        if b == 0:
            return self.max_val if a >= 0 else self.min_val
        # Shift left before division to maintain precision
        result = (a << self.fractional_bits) // b
        return result

    def clamp(self, value: int) -> int:
        """Clamp value to valid fixed-point range."""
        return max(self.min_val, min(self.max_val, value))

    def clamp_array(self, values: np.ndarray) -> np.ndarray:
        """Clamp array to valid fixed-point range."""
        return np.clip(values, self.min_val, self.max_val)


# Pre-computed sine/cosine lookup table for fixed-point
class TrigLUT:
    """
    Lookup table for sine and cosine in fixed-point.
    Uses a quarter-wave table with symmetry for full 2*pi range.

    IMPORTANT: Returns unsigned 2's complement values matching RTL hex files.
    Negative values are stored as (1 << 25) + signed_value to match gen_trig_lut.py.
    """

    def __init__(self, fp: FixedPoint, table_bits: int = 10):
        """
        Initialize trig lookup table.

        Args:
            fp: FixedPoint configuration
            table_bits: Number of bits for angle indexing (table size = 2^table_bits)
        """
        self.fp = fp
        self.table_bits = table_bits
        self.table_size = 1 << table_bits
        self.angle_mask = self.table_size - 1

        # Full 2*pi represented as table_size steps
        # Store quarter wave (0 to pi/2) and use symmetry
        quarter_size = self.table_size // 4

        # Build sine table for one full period
        # CRITICAL: Generate unsigned 2's complement values matching RTL
        angles = np.linspace(0, 2 * np.pi, self.table_size, endpoint=False)
        sin_signed = fp.to_fixed_array(np.sin(angles))
        cos_signed = fp.to_fixed_array(np.cos(angles))

        # Convert negative values to unsigned 2's complement (25-bit)
        # This matches gen_trig_lut.py: if val < 0: val = (1 << 25) + val
        self.sin_table = np.where(sin_signed < 0, (1 << 25) + sin_signed, sin_signed).astype(np.int64)
        self.cos_table = np.where(cos_signed < 0, (1 << 25) + cos_signed, cos_signed).astype(np.int64)

        # Fixed-point representation of 2*pi for angle wrapping
        self.two_pi_fixed = fp.to_fixed(2 * np.pi)
        self.angle_scale = self.table_size / self.two_pi_fixed

    def sin(self, angle_fixed: int) -> int:
        """Get sine of fixed-point angle."""
        # Convert angle to table index
        # angle is in fixed-point radians, table covers 0 to 2*pi
        idx = int((angle_fixed * self.angle_scale)) & self.angle_mask
        return self.sin_table[idx]

    def cos(self, angle_fixed: int) -> int:
        """Get cosine of fixed-point angle."""
        idx = int((angle_fixed * self.angle_scale)) & self.angle_mask
        return self.cos_table[idx]

    def sin_array(self, angles_fixed: np.ndarray) -> np.ndarray:
        """Get sine of fixed-point angle array."""
        indices = ((angles_fixed * self.angle_scale).astype(np.int64)) & self.angle_mask
        return self.sin_table[indices]

    def cos_array(self, angles_fixed: np.ndarray) -> np.ndarray:
        """Get cosine of fixed-point angle array."""
        indices = ((angles_fixed * self.angle_scale).astype(np.int64)) & self.angle_mask
        return self.cos_table[indices]


@dataclass
class SimulationConfig:
    """Configuration for the slime simulation."""
    width: int = 800
    height: int = 600
    num_agents: int = 100000

    # Agent settings
    move_speed: float = 1.0
    turn_speed: float = 0.3  # Rotation amount (radians)

    # Sensor settings
    sensor_angle: float = 0.5  # Angle offset for left/right sensors (radians)
    sensor_distance: float = 9.0  # Distance ahead to sense
    sensor_size: int = 1  # Size of sensor (radius)

    # Trail settings
    deposit_amount: float = 5.0
    decay_rate: float = 0.95  # Trail decay per step
    diffuse_rate: float = 0.2  # How much trail diffuses to neighbors

    # Simulation settings
    num_steps: int = 500
    save_every: int = 10
    output_dir: str = "output_images"

    # Initial spawn pattern: 'circle', 'random', 'center', 'ring'
    spawn_pattern: str = 'circle'

    # Fixed-point settings
    integer_bits: int = 12  # Bits for integer part
    fractional_bits: int = 12  # Bits for fractional part

    # LFSR settings
    lfsr_width: int = 32  # LFSR bit width
    seed: int = 0xDEADBEEF  # Random seed

    # Trig LUT settings
    trig_table_bits: int = 10  # 1024 entry trig table


class SlimeSimulator:
    """Main slime mold simulator using fixed-point arithmetic and LFSR."""

    def __init__(self, config: SimulationConfig):
        self.config = config
        self.width = config.width
        self.height = config.height

        # Initialize fixed-point system
        self.fp = FixedPoint(config.integer_bits, config.fractional_bits)

        # Initialize trig lookup table
        self.trig = TrigLUT(self.fp, config.trig_table_bits)

        # Initialize LFSR
        self.lfsr = LFSR(config.lfsr_width, config.seed)

        # Pre-compute fixed-point constants
        self.move_speed_fp = self.fp.to_fixed(config.move_speed)
        self.turn_speed_fp = self.fp.to_fixed(config.turn_speed)
        self.sensor_angle_fp = self.fp.to_fixed(config.sensor_angle)
        self.sensor_distance_fp = self.fp.to_fixed(config.sensor_distance)
        self.deposit_amount_fp = self.fp.to_fixed(config.deposit_amount)
        self.decay_rate_fp = self.fp.to_fixed(config.decay_rate)
        self.diffuse_rate_fp = self.fp.to_fixed(config.diffuse_rate)
        self.one_minus_diffuse_fp = self.fp.to_fixed(1.0 - config.diffuse_rate)
        self.width_fp = self.fp.to_fixed(config.width)
        self.height_fp = self.fp.to_fixed(config.height)
        self.two_pi_fp = self.fp.to_fixed(2 * np.pi)
        self.half_fp = self.fp.to_fixed(0.5)

        # Initialize trail map (fixed-point, but stored as integers)
        # Trail values are in Q8.8 or similar, clamped to 0-255 for display
        self.trail_map = np.zeros((config.height, config.width), dtype=np.int64)

        # Initialize agents as arrays (vectorized, fixed-point)
        self._spawn_agents()

        # Diffusion kernel (3x3 box blur) - use integer division by 9
        self.diffuse_kernel = np.ones((3, 3), dtype=np.float32) / 9.0

    def seed(self, seed_value: int):
        """Reset the LFSR with a new seed."""
        self.lfsr = LFSR(self.config.lfsr_width, seed_value)

    def get_lfsr_state(self) -> int:
        """Get current LFSR state for RTL verification."""
        return self.lfsr.get_state()

    def _lfsr_uniform_fp(self, n: int, max_val_fp: int) -> np.ndarray:
        """Generate n uniform random fixed-point values in [0, max_val_fp)."""
        # Get raw LFSR values
        raw = self.lfsr.next_n(n)
        # Scale to [0, max_val_fp) using fixed-point multiply
        # raw is in [0, 2^lfsr_width), we want [0, max_val_fp)
        # result = (raw * max_val_fp) >> lfsr_width
        result = (raw.astype(np.int64) * max_val_fp) >> self.config.lfsr_width
        return result

    def _lfsr_uniform_angle_fp(self, n: int) -> np.ndarray:
        """Generate n uniform random angles in [0, 2*pi) as fixed-point."""
        return self._lfsr_uniform_fp(n, self.two_pi_fp)

    def _lfsr_bool_n(self, n: int) -> np.ndarray:
        """Generate n random booleans using LFSR."""
        return self.lfsr.next_bool_n(n)

    def _spawn_agents(self):
        """Spawn agents based on the configured pattern using LFSR."""
        n = self.config.num_agents
        cx_fp = self.fp.to_fixed(self.width / 2)
        cy_fp = self.fp.to_fixed(self.height / 2)

        if self.config.spawn_pattern == 'circle':
            # Spawn in a circle pointing inward (deterministic, matching RTL)
            # Agents are evenly spaced around the circle at angles: 2π * i / NUM_AGENTS
            radius_fp = self.fp.to_fixed(min(self.width, self.height) * 0.4)

            # Generate deterministic spawn angles: 2π * i / NUM_AGENTS for i in [0, n)
            spawn_angles_fp = np.array(
                [self.fp.to_fixed(2 * np.pi * i / n) for i in range(n)],
                dtype=np.int64
            )

            # x = cx + cos(angle) * radius
            cos_vals = self.trig.cos_array(spawn_angles_fp)
            sin_vals = self.trig.sin_array(spawn_angles_fp)

            self.x = cx_fp + self.fp.multiply_array(cos_vals, np.full(n, radius_fp, dtype=np.int64))
            self.y = cy_fp + self.fp.multiply_array(sin_vals, np.full(n, radius_fp, dtype=np.int64))
            # Point toward center (angle + pi), with proper wrapping to [0, 2π)
            pi_fp = self.fp.to_fixed(np.pi)
            two_pi_fp = self.fp.to_fixed(2 * np.pi)
            self.angles = spawn_angles_fp + pi_fp
            # Normalize angles to [0, 2π)
            self.angles = np.where(self.angles >= two_pi_fp, self.angles - two_pi_fp, self.angles)

        elif self.config.spawn_pattern == 'random':
            # Random positions and angles
            self.x = self._lfsr_uniform_fp(n, self.width_fp)
            self.y = self._lfsr_uniform_fp(n, self.height_fp)
            self.angles = self._lfsr_uniform_angle_fp(n)

        elif self.config.spawn_pattern == 'center':
            # All spawn at center with small random offset
            offset_range_fp = self.fp.to_fixed(10)  # ±5 pixels
            offsets_x = self._lfsr_uniform_fp(n, offset_range_fp) - self.fp.to_fixed(5)
            offsets_y = self._lfsr_uniform_fp(n, offset_range_fp) - self.fp.to_fixed(5)
            self.x = np.full(n, cx_fp, dtype=np.int64) + offsets_x
            self.y = np.full(n, cy_fp, dtype=np.int64) + offsets_y
            self.angles = self._lfsr_uniform_angle_fp(n)

        elif self.config.spawn_pattern == 'ring':
            # Spawn in a thin ring
            radius_fp = self.fp.to_fixed(min(self.width, self.height) * 0.3)
            spawn_angles_fp = self._lfsr_uniform_angle_fp(n)

            cos_vals = self.trig.cos_array(spawn_angles_fp)
            sin_vals = self.trig.sin_array(spawn_angles_fp)

            self.x = cx_fp + self.fp.multiply_array(cos_vals, np.full(n, radius_fp, dtype=np.int64))
            self.y = cy_fp + self.fp.multiply_array(sin_vals, np.full(n, radius_fp, dtype=np.int64))
            self.angles = self._lfsr_uniform_angle_fp(n)
        else:
            raise ValueError(f"Unknown spawn pattern: {self.config.spawn_pattern}")

        # Ensure arrays are int64
        self.x = self.x.astype(np.int64)
        self.y = self.y.astype(np.int64)
        self.angles = self.angles.astype(np.int64)

    def _sense(self, angle_offset_fp: int) -> np.ndarray:
        """
        Sense the trail map at a given angle offset from agents' directions.
        Returns the trail values at sensor positions for all agents (fixed-point).
        """
        sense_angles = self.angles + angle_offset_fp

        # Compute sensor position using trig LUT
        cos_vals = self.trig.cos_array(sense_angles)
        sin_vals = self.trig.sin_array(sense_angles)

        sense_x = self.x + self.fp.multiply_array(cos_vals,
                    np.full(self.config.num_agents, self.sensor_distance_fp, dtype=np.int64))
        sense_y = self.y + self.fp.multiply_array(sin_vals,
                    np.full(self.config.num_agents, self.sensor_distance_fp, dtype=np.int64))

        # Convert to integer pixel coordinates with wrapping
        # Divide by scale to get integer part
        sx = (sense_x // self.fp.scale) % self.width
        sy = (sense_y // self.fp.scale) % self.height

        # Ensure non-negative indices
        sx = sx % self.width
        sy = sy % self.height

        # Sample the trail map
        return self.trail_map[sy.astype(np.int32), sx.astype(np.int32)]

    def _sensory_stage(self):
        """
        Sensory stage: sample trail map and adjust direction for all agents.
        Fixed-point vectorized implementation.
        """
        # Sample in three directions
        forward = self._sense(0)
        forward_left = self._sense(self.sensor_angle_fp)
        forward_right = self._sense(-self.sensor_angle_fp)

        # Random booleans for random turning decisions (from LFSR)
        random_turn_left = self._lfsr_bool_n(self.config.num_agents)

        # Decide turning based on sensory input
        turn_speed = self.turn_speed_fp

        # Case 1: F > FL and F > FR -> stay facing same direction (no change)
        case1 = (forward > forward_left) & (forward > forward_right)

        # Case 2: F < FL and F < FR -> rotate randomly
        case2 = (forward < forward_left) & (forward < forward_right)
        random_turn = np.where(random_turn_left, turn_speed, -turn_speed)
        self.angles = np.where(case2, self.angles + random_turn, self.angles)

        # Case 3: FL < FR -> rotate right (only if not case 1 or case 2)
        case3 = ~case1 & ~case2 & (forward_left < forward_right)
        self.angles = np.where(case3, self.angles - turn_speed, self.angles)

        # Case 4: FR < FL -> rotate left
        case4 = ~case1 & ~case2 & ~case3 & (forward_right < forward_left)
        self.angles = np.where(case4, self.angles + turn_speed, self.angles)

        # Wrap angles to [0, 2*pi)
        self.angles = self.angles % self.two_pi_fp

    def _motor_stage(self):
        """
        Motor stage: move forward and deposit trail for all agents.
        Fixed-point vectorized implementation.
        """
        # Calculate velocity components using trig LUT
        cos_vals = self.trig.cos_array(self.angles)
        sin_vals = self.trig.sin_array(self.angles)

        # Calculate new positions
        dx = self.fp.multiply_array(cos_vals,
                np.full(self.config.num_agents, self.move_speed_fp, dtype=np.int64))
        dy = self.fp.multiply_array(sin_vals,
                np.full(self.config.num_agents, self.move_speed_fp, dtype=np.int64))

        self.x = self.x + dx
        self.y = self.y + dy

        # Wrap around (toroidal world)
        self.x = self.x % self.width_fp
        self.y = self.y % self.height_fp

        # Ensure positive values after modulo
        self.x = np.where(self.x < 0, self.x + self.width_fp, self.x)
        self.y = np.where(self.y < 0, self.y + self.height_fp, self.y)

        # Deposit trail at new locations
        px = (self.x // self.fp.scale).astype(np.int32) % self.width
        py = (self.y // self.fp.scale).astype(np.int32) % self.height

        # Use np.add.at for atomic-like addition at indices
        np.add.at(self.trail_map, (py, px), self.deposit_amount_fp)

    def _diffuse_and_decay(self):
        """
        Apply diffusion and decay to the trail map.
        Uses fixed-point arithmetic.
        """
        # Apply diffusion with box blur kernel (wrap mode for toroidal)
        # For RTL, this would be done with shifts and adds
        # Here we use scipy for convenience but the math is the same
        trail_float = self.trail_map.astype(np.float64) / self.fp.scale
        diffused = ndimage.convolve(trail_float, self.diffuse_kernel, mode='wrap')
        diffused_fp = (diffused * self.fp.scale).astype(np.int64)

        # Blend: result = original * (1 - diffuse_rate) + diffused * diffuse_rate
        # In fixed-point: result = (original * one_minus_diffuse + diffused * diffuse_rate) >> frac_bits
        blended = (self.fp.multiply_array(self.trail_map,
                      np.full_like(self.trail_map, self.one_minus_diffuse_fp)) +
                   self.fp.multiply_array(diffused_fp,
                      np.full_like(diffused_fp, self.diffuse_rate_fp)))

        # Apply decay
        self.trail_map = self.fp.multiply_array(blended,
                            np.full_like(blended, self.decay_rate_fp))

        # Clamp to valid range (0 to 255 in display space, scaled for fixed-point)
        max_trail_fp = self.fp.to_fixed(255)
        self.trail_map = np.clip(self.trail_map, 0, max_trail_fp)

    def step(self):
        """Perform one simulation step."""
        # Sensory stage first
        self._sensory_stage()
        # Then motor stage
        self._motor_stage()
        # Diffuse and decay trail map
        self._diffuse_and_decay()

    def get_pixels(self) -> np.ndarray:
        """Convert trail map to RGB pixel array."""
        # Convert fixed-point trail to 0-255 range
        normalized = np.clip(self.trail_map // self.fp.scale, 0, 255).astype(np.uint8)

        # Create RGB image with nice slime color gradient
        intensity = normalized.astype(np.float32) / 255.0
        pixels = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        pixels[:, :, 0] = (intensity * 200).astype(np.uint8)  # R
        pixels[:, :, 1] = (intensity * 255).astype(np.uint8)  # G
        pixels[:, :, 2] = (intensity * 200).astype(np.uint8)  # B

        return pixels

    def get_image(self) -> Image.Image:
        """Convert trail map to a PIL Image."""
        return Image.fromarray(self.get_pixels())

    def save_image(self, filename: str):
        """Save the current state as an image."""
        img = self.get_image()
        img.save(filename)

    def dump_state(self, filename: str):
        """Dump simulation state for RTL verification."""
        state = {
            'lfsr_state': self.lfsr.get_state(),
            'agent_x': self.x.tolist(),
            'agent_y': self.y.tolist(),
            'agent_angles': self.angles.tolist(),
            'trail_map': self.trail_map.tolist(),
            'config': {
                'width': self.width,
                'height': self.height,
                'num_agents': self.config.num_agents,
                'integer_bits': self.config.integer_bits,
                'fractional_bits': self.config.fractional_bits,
                'lfsr_width': self.config.lfsr_width,
                'seed': self.config.seed,
            }
        }
        import json
        with open(filename, 'w') as f:
            json.dump(state, f)
        print(f"State dumped to {filename}")

    def run(self, progress_callback=None):
        """Run the full simulation."""
        os.makedirs(self.config.output_dir, exist_ok=True)

        print(f"Starting simulation with {self.config.num_agents} agents...")
        print(f"Resolution: {self.width}x{self.height}")
        print(f"Fixed-point: Q{self.config.integer_bits}.{self.config.fractional_bits}")
        print(f"LFSR: {self.config.lfsr_width}-bit, seed=0x{self.config.seed:X}")
        print(f"Steps: {self.config.num_steps}")
        print(f"Output directory: {self.config.output_dir}")
        print()

        for step in range(self.config.num_steps):
            self.step()

            if step % self.config.save_every == 0 or step == self.config.num_steps - 1:
                filename = os.path.join(self.config.output_dir, f"frame_{step:05d}.png")
                self.save_image(filename)
                print(f"Step {step}/{self.config.num_steps} - Saved {filename} (LFSR: 0x{self.lfsr.get_state():08X})")

            if progress_callback:
                progress_callback(step, self.config.num_steps)

        print(f"\nSimulation complete! Images saved to {self.config.output_dir}/")
        return self.get_image()

    def run_display(self, save_images: bool = False):
        """Run simulation with real-time pygame display."""
        if not PYGAME_AVAILABLE:
            print("Error: pygame is required for display mode.")
            print("Install it with: pip install pygame")
            return

        pygame.init()
        screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Slime Mold Simulator (Fixed-Point)")
        clock = pygame.time.Clock()

        if save_images:
            os.makedirs(self.config.output_dir, exist_ok=True)

        print(f"Starting simulation with {self.config.num_agents} agents...")
        print(f"Resolution: {self.width}x{self.height}")
        print(f"Fixed-point: Q{self.config.integer_bits}.{self.config.fractional_bits}")
        print(f"LFSR: {self.config.lfsr_width}-bit, seed=0x{self.config.seed:X}")
        print("Press ESC or close window to exit")
        print()

        running = True
        step = 0

        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            # Run simulation step
            self.step()

            # Get pixels and display
            pixels = self.get_pixels()
            surface = pygame.surfarray.make_surface(pixels.swapaxes(0, 1))
            screen.blit(surface, (0, 0))
            pygame.display.flip()

            # Save images if requested
            if save_images and (step % self.config.save_every == 0):
                filename = os.path.join(self.config.output_dir, f"frame_{step:05d}.png")
                self.save_image(filename)

            step += 1
            if self.config.num_steps > 0 and step >= self.config.num_steps:
                running = False

            clock.tick(0)
            fps = clock.get_fps()
            pygame.display.set_caption(
                f"Slime Simulator - Step {step} - {fps:.1f} FPS - LFSR: 0x{self.lfsr.get_state():08X}")

        pygame.quit()
        print(f"\nSimulation ended at step {step}")


def main():
    parser = argparse.ArgumentParser(description="Slime Mold (Physarum) Simulator - RTL Compatible")

    # Display settings
    parser.add_argument("--width", type=int, default=800, help="Image width")
    parser.add_argument("--height", type=int, default=600, help="Image height")
    parser.add_argument("--agents", type=int, default=100000, help="Number of agents")
    parser.add_argument("--steps", type=int, default=500, help="Number of simulation steps")
    parser.add_argument("--save-every", type=int, default=10, help="Save image every N steps")
    parser.add_argument("--output", type=str, default="output_images", help="Output directory")
    parser.add_argument("--spawn", type=str, default="circle",
                       choices=["circle", "random", "center", "ring"],
                       help="Agent spawn pattern")

    # Agent parameters
    parser.add_argument("--speed", type=float, default=1.0, help="Agent move speed")
    parser.add_argument("--turn-speed", type=float, default=0.3, help="Turn speed (radians)")
    parser.add_argument("--sensor-angle", type=float, default=0.5, help="Sensor angle offset")
    parser.add_argument("--sensor-distance", type=float, default=9.0, help="Sensor distance")
    parser.add_argument("--decay", type=float, default=0.95, help="Trail decay rate")
    parser.add_argument("--diffuse", type=float, default=0.2, help="Trail diffusion rate")
    parser.add_argument("--deposit", type=float, default=5.0, help="Trail deposit amount")

    # Fixed-point settings
    parser.add_argument("--integer-bits", type=int, default=12,
                       help="Fixed-point integer bits (excluding sign)")
    parser.add_argument("--fractional-bits", type=int, default=12,
                       help="Fixed-point fractional bits")

    # LFSR settings
    parser.add_argument("--lfsr-width", type=int, default=32, choices=[8, 16, 24, 32, 48, 64],
                       help="LFSR bit width")
    parser.add_argument("--seed", type=lambda x: int(x, 0), default=0xDEADBEEF,
                       help="LFSR seed (hex or decimal, e.g., 0xDEADBEEF or 12345)")

    # Trig LUT settings
    parser.add_argument("--trig-bits", type=int, default=10,
                       help="Trig lookup table address bits (table size = 2^n)")

    # Display options
    parser.add_argument("--display", action="store_true", help="Show real-time display window")
    parser.add_argument("--no-save", action="store_true", help="Don't save images (only with --display)")

    # Debug options
    parser.add_argument("--dump-state", type=str, default=None,
                       help="Dump final state to JSON file for RTL verification")

    args = parser.parse_args()

    config = SimulationConfig(
        width=args.width,
        height=args.height,
        num_agents=args.agents,
        num_steps=args.steps,
        save_every=args.save_every,
        output_dir=args.output,
        spawn_pattern=args.spawn,
        move_speed=args.speed,
        turn_speed=args.turn_speed,
        sensor_angle=args.sensor_angle,
        sensor_distance=args.sensor_distance,
        decay_rate=args.decay,
        diffuse_rate=args.diffuse,
        deposit_amount=args.deposit,
        integer_bits=args.integer_bits,
        fractional_bits=args.fractional_bits,
        lfsr_width=args.lfsr_width,
        seed=args.seed,
        trig_table_bits=args.trig_bits,
    )

    sim = SlimeSimulator(config)

    if args.display:
        sim.run_display(save_images=not args.no_save)
    else:
        sim.run()

    if args.dump_state:
        sim.dump_state(args.dump_state)


if __name__ == "__main__":
    main()
