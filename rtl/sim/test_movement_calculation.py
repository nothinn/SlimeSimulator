#!/usr/bin/env python3
"""
Cocotb Testbench: Movement Calculation (dx, dy)

Tests the agent_processor movement calculation (CALC_MOVE_X, CALC_MOVE_Y states)
by comparing RTL outputs with Python reference implementation.

This testbench helps isolate the 2x movement bug by:
1. Testing fixed_point_mult for cos*speed and sin*speed
2. Verifying trig_lut sin/cos outputs match Python
3. Checking dx, dy capture and position update
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer, ClockCycles
import numpy as np
import os
import sys
from pathlib import Path

# Add testbench directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))
from python_reference import FixedPoint, TrigLUT

# Parameters matching agent_processor.sv
INT_BITS = 12
FRAC_BITS = 12
TOTAL_BITS = INT_BITS + FRAC_BITS + 1  # 25 bits


class MovementTestVector:
    """Test vector for movement calculation."""

    def __init__(self, angle_deg: float, move_speed: float, expected_dx: float, expected_dy: float):
        """
        Create test vector.

        Args:
            angle_deg: Agent angle in degrees
            move_speed: Movement speed (pixels per step)
            expected_dx: Expected X displacement in pixels
            expected_dy: Expected Y displacement in pixels
        """
        self.angle_deg = angle_deg
        self.move_speed = move_speed
        self.expected_dx = expected_dx
        self.expected_dy = expected_dy

        # Convert to fixed-point
        self.fp = FixedPoint(INT_BITS, FRAC_BITS)
        self.trig = TrigLUT(10, FRAC_BITS)

        # Angle in radians (0 to 2π)
        self.angle_rad = angle_deg * np.pi / 180.0

        # Compute angle index (0-1023)
        TWO_PI = 2.0 * np.pi
        normalized = self.angle_rad % TWO_PI
        self.angle_idx = int(round((normalized / TWO_PI) * 1024)) & 0x3FF

        # Get sin/cos from RTL tables
        self.sin_rtl = self.trig.sin(self.angle_idx)
        self.cos_rtl = self.trig.cos(self.angle_idx)

        # Compute expected (using Python fixed-point)
        speed_fp = self.fp.to_fixed(move_speed)
        self.dx_fp = self.fp.multiply(self.cos_rtl, speed_fp)
        self.dy_fp = self.fp.multiply(self.sin_rtl, speed_fp)

        # Convert back to float for comparison
        self.dx_expected = self.fp.from_fixed(self.dx_fp)
        self.dy_expected = self.fp.from_fixed(self.dy_fp)


def create_test_vectors():
    """Create test vectors covering cardinal directions and diagonals."""
    vectors = []

    # Cardinal directions (0°, 90°, 180°, 270°)
    vectors.append(MovementTestVector(0.0, 1.0, 1.0, 0.0))      # Right
    vectors.append(MovementTestVector(90.0, 1.0, 0.0, 1.0))     # Down
    vectors.append(MovementTestVector(180.0, 1.0, -1.0, 0.0))   # Left
    vectors.append(MovementTestVector(270.0, 1.0, 0.0, -1.0))   # Up

    # Diagonals (45°, 135°, 225°, 315°)
    sqrt2_half = np.sqrt(2) / 2
    vectors.append(MovementTestVector(45.0, 1.0, sqrt2_half, sqrt2_half))     # Down-right
    vectors.append(MovementTestVector(135.0, 1.0, -sqrt2_half, sqrt2_half))   # Down-left
    vectors.append(MovementTestVector(225.0, 1.0, -sqrt2_half, -sqrt2_half))  # Up-left
    vectors.append(MovementTestVector(315.0, 1.0, sqrt2_half, -sqrt2_half))   # Up-right

    # Different speeds
    vectors.append(MovementTestVector(0.0, 0.5, 0.5, 0.0))
    vectors.append(MovementTestVector(0.0, 2.0, 2.0, 0.0))

    return vectors


@cocotb.test()
async def test_fixed_point_mult_movement(dut):
    """Test fixed_point_mult specifically for movement (cos*speed, sin*speed)."""

    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

    fp = FixedPoint(INT_BITS, FRAC_BITS)

    test_cases = [
        (1.0, 1.0),    # cos(0°)=1, speed=1 → 1.0
        (0.0, 1.0),    # cos(90°)=0, speed=1 → 0.0
        (-1.0, 1.0),   # cos(180°)=-1, speed=1 → -1.0
        (1.0, 0.5),    # cos(0°)=1, speed=0.5 → 0.5
        (1.0, 2.0),    # cos(0°)=1, speed=2 → 2.0
        (0.7071, 1.0), # cos(45°)≈0.707, speed=1 → 0.707
    ]

    errors = 0
    for i, (cos_val, speed) in enumerate(test_cases):
        cos_fp = fp.to_fixed(cos_val)
        speed_fp = fp.to_fixed(speed)
        expected = fp.from_fixed(fp.multiply(cos_fp, speed_fp))

        # Apply to RTL multiplier
        dut.a.value = cos_fp & ((1 << TOTAL_BITS) - 1)
        dut.b.value = speed_fp & ((1 << TOTAL_BITS) - 1)
        await Timer(1, unit="ns")

        result_rtl = int(dut.result.value)
        result_float = fp.from_fixed(result_rtl)

        error = abs(result_float - expected)
        if error > 1e-4:
            dut._log.error(f"Test {i}: cos={cos_val:.4f}, speed={speed}, "
                          f"Expected={expected:.6f}, RTL={result_float:.6f}, "
                          f"Error={error:.6f}")
            errors += 1
        else:
            dut._log.info(f"Test {i}: PASS (cos={cos_val:.4f}, speed={speed})")

    assert errors == 0, f"fixed_point_mult had {errors} errors"
    dut._log.info("fixed_point_mult: All tests PASSED!")


@cocotb.test()
async def test_trig_lut_outputs(dut):
    """Test trig_lut sin/cos table outputs against Python reference."""

    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

    trig = TrigLUT(10, FRAC_BITS)
    fp = FixedPoint(INT_BITS, FRAC_BITS)

    # Test key angles
    test_angles = [0, 256, 512, 768]  # 0°, 90°, 180°, 270°

    errors = 0
    for angle_idx in test_angles:
        dut.angle_idx.value = angle_idx
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")

        sin_rtl = int(dut.sin_out.value)
        cos_rtl = int(dut.cos_out.value)

        sin_py = trig.sin(angle_idx)
        cos_py = trig.cos(angle_idx)

        sin_match = (sin_rtl & ((1 << TOTAL_BITS) - 1)) == (sin_py & ((1 << TOTAL_BITS) - 1))
        cos_match = (cos_rtl & ((1 << TOTAL_BITS) - 1)) == (cos_py & ((1 << TOTAL_BITS) - 1))

        if not sin_match or not cos_match:
            sin_deg = int(angle_idx * 360 / 1024)
            dut._log.error(f"Angle {angle_idx} ({sin_deg}°): "
                          f"sin RTL={sin_rtl:025b} vs Py={sin_py:025b}, "
                          f"cos RTL={cos_rtl:025b} vs Py={cos_py:025b}")
            errors += 1
        else:
            sin_deg = int(angle_idx * 360 / 1024)
            dut._log.info(f"Angle {angle_idx} ({sin_deg}°): PASS")

    assert errors == 0, f"trig_lut had {errors} mismatches"
    dut._log.info("trig_lut: All tests PASSED!")


@cocotb.test()
async def test_movement_calculation_pipeline(dut):
    """
    Test the full movement calculation pipeline.

    This tests the combination of:
    1. Trig LUT reading sin/cos
    2. Fixed-point multiplication (cos*speed, sin*speed)
    3. Capturing dx, dy results
    """

    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.rst_n.value = 0
    dut.start.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

    # Set control parameters
    fp = FixedPoint(INT_BITS, FRAC_BITS)
    move_speed_fp = fp.to_fixed(1.0)  # move_speed = 1.0 pixel/step
    turn_speed_fp = fp.to_fixed(0.3)  # turn_speed = 0.3 rad/turn
    sensor_angle_fp = fp.to_fixed(0.5)  # sensor_angle = 0.5 rad
    sensor_dist_fp = fp.to_fixed(9.0)   # sensor_distance = 9.0 pixels
    deposit_fp = fp.to_fixed(5.0)       # deposit_amount = 5.0

    dut.move_speed.value = move_speed_fp & ((1 << TOTAL_BITS) - 1)
    dut.turn_speed.value = turn_speed_fp & ((1 << TOTAL_BITS) - 1)
    dut.sensor_angle.value = sensor_angle_fp & ((1 << TOTAL_BITS) - 1)
    dut.sensor_distance.value = sensor_dist_fp & ((1 << TOTAL_BITS) - 1)
    dut.deposit_amount.value = deposit_fp & ((1 << TOTAL_BITS) - 1)

    # Test vectors: (angle in degrees, initial X, initial Y, expected final X, expected final Y)
    test_vectors = [
        (0, 100, 100, 101, 100),      # Move right 1 pixel
        (90, 100, 100, 100, 101),     # Move down 1 pixel
        (180, 100, 100, 99, 100),     # Move left 1 pixel
        (270, 100, 100, 100, 99),     # Move up 1 pixel
    ]

    trig = TrigLUT(10, FRAC_BITS)

    for angle_deg, x, y, expected_x, expected_y in test_vectors:
        # Compute angle index
        angle_rad = angle_deg * np.pi / 180.0
        TWO_PI = 2.0 * np.pi
        normalized = angle_rad % TWO_PI
        angle_idx = int(round((normalized / TWO_PI) * 1024)) & 0x3FF

        # Set initial agent state
        x_fp = fp.to_fixed(float(x))
        y_fp = fp.to_fixed(float(y))
        angle_fp = fp.to_fixed(angle_rad)

        dut.agent_x_in.value = x_fp & ((1 << TOTAL_BITS) - 1)
        dut.agent_y_in.value = y_fp & ((1 << TOTAL_BITS) - 1)
        dut.agent_angle_in.value = angle_fp & ((1 << TOTAL_BITS) - 1)

        # Start processing
        dut.start.value = 1
        await RisingEdge(dut.clk)
        dut.start.value = 0

        # Wait for processing to complete (~19 cycles for full pipeline)
        # This is an approximation - actual implementation may vary
        for _ in range(30):
            await RisingEdge(dut.clk)
            if int(dut.done.value) == 1:
                break

        # Read results
        x_out_fp = int(dut.agent_x_out.value)
        y_out_fp = int(dut.agent_y_out.value)

        # Convert to float
        x_out = fp.from_fixed(x_out_fp)
        y_out = fp.from_fixed(y_out_fp)

        # Check against expected (with tolerance for rounding)
        x_error = abs(x_out - expected_x)
        y_error = abs(y_out - expected_y)

        dut._log.info(f"Angle {angle_deg}°: x={x_out:.3f} (expected {expected_x}), "
                     f"y={y_out:.3f} (expected {expected_y})")

        # Allow 0.01 pixel tolerance for rounding
        if x_error < 0.01 and y_error < 0.01:
            dut._log.info(f"  PASS")
        else:
            dut._log.error(f"  FAIL: x_error={x_error:.6f}, y_error={y_error:.6f}")


if __name__ == "__main__":
    # This allows running the test module directly for debugging
    print("This module contains cocotb tests.")
    print("Run with: cd rtl/sim && make test_movement_calculation")
