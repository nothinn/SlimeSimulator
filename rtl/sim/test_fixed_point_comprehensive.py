#!/usr/bin/env python3
"""
Comprehensive Fixed-Point Multiplication Testbench

Tests the fixed_point_mult module extensively to verify it matches Python
implementation for all value ranges and edge cases.
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer
import numpy as np
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from python_reference import FixedPoint

INT_BITS = 12
FRAC_BITS = 12
TOTAL_BITS = INT_BITS + FRAC_BITS + 1  # 25 bits


def fp_to_signed(val: int, bits: int) -> int:
    """Convert unsigned to signed integer."""
    if val >= (1 << (bits - 1)):
        return val - (1 << bits)
    return val


def signed_to_fp(val: int, bits: int) -> int:
    """Convert signed to unsigned fixed-point."""
    return val & ((1 << bits) - 1)


@cocotb.test()
async def test_fixed_point_mult_comprehensive(dut):
    """Comprehensive test of fixed-point multiplication."""

    fp = FixedPoint(INT_BITS, FRAC_BITS)

    # Test cases: (a_float, b_float, description)
    test_cases = [
        # Basic multiplication
        (1.0, 1.0, "1 * 1"),
        (2.0, 2.0, "2 * 2"),
        (0.5, 0.5, "0.5 * 0.5"),
        (1.5, 2.5, "1.5 * 2.5"),

        # Zero
        (0.0, 1.0, "0 * 1"),
        (1.0, 0.0, "1 * 0"),
        (0.0, 0.0, "0 * 0"),

        # Negative
        (-1.0, 1.0, "-1 * 1"),
        (1.0, -1.0, "1 * -1"),
        (-1.0, -1.0, "-1 * -1"),
        (-2.0, 3.0, "-2 * 3"),

        # Fractional
        (0.25, 0.25, "0.25 * 0.25"),
        (0.125, 8.0, "0.125 * 8"),
        (3.14159, 2.0, "π * 2"),

        # Trigonometric values (cos/sin multiplication with speed)
        (0.0, 1.0, "cos(90°) * speed=1 → 0"),
        (0.7071, 1.0, "cos(45°) * speed=1 → 0.707"),
        (0.7071, 2.0, "cos(45°) * speed=2 → 1.414"),
        (1.0, 1.0, "cos(0°) * speed=1 → 1.0"),
        (-1.0, 1.0, "cos(180°) * speed=1 → -1.0"),

        # Edge cases
        (0.001, 0.001, "Very small numbers"),
        (100.0, 0.1, "Large * small"),
        (2047.999, 0.0625, "Large positive * small"),
        (-2047.999, 0.0625, "Large negative * small"),
    ]

    errors = []
    total = 0

    for a_float, b_float, desc in test_cases:
        total += 1

        # Convert to fixed-point
        a_fp = fp.to_fixed(a_float)
        b_fp = fp.to_fixed(b_float)

        # Compute expected result
        expected_result = fp.multiply(a_fp, b_fp)
        expected_float = fp.from_fixed(expected_result)

        # Apply to RTL
        dut.a.value = a_fp & ((1 << TOTAL_BITS) - 1)
        dut.b.value = b_fp & ((1 << TOTAL_BITS) - 1)
        await Timer(1, unit="ns")

        rtl_result = int(dut.result.value)
        rtl_float = fp.from_fixed(rtl_result)

        # Check match
        if rtl_result != expected_result:
            error_desc = (f"MISMATCH: {desc}\n"
                         f"  a={a_float:.6f}, b={b_float:.6f}\n"
                         f"  Expected: {expected_float:.6f} ({expected_result:025b})\n"
                         f"  RTL:      {rtl_float:.6f} ({rtl_result:025b})\n"
                         f"  Diff:     {rtl_float - expected_float:.6e}")
            errors.append(error_desc)
            dut._log.error(error_desc)
        else:
            dut._log.info(f"PASS: {desc} = {rtl_float:.6f}")

    # Summary
    dut._log.info(f"\n{'='*70}")
    dut._log.info(f"Fixed-Point Multiplication Test Summary")
    dut._log.info(f"{'='*70}")
    dut._log.info(f"Total tests: {total}")
    dut._log.info(f"Passed: {total - len(errors)}")
    dut._log.info(f"Failed: {len(errors)}")

    if errors:
        dut._log.error("\nFailed tests:")
        for err in errors:
            dut._log.error(err)

    assert len(errors) == 0, f"Fixed-point multiplication had {len(errors)} errors"
    dut._log.info("All tests PASSED!")


@cocotb.test()
async def test_movement_multiplies_sequence(dut):
    """
    Test a sequence of multiplies simulating movement calculation.

    This mimics what happens in CALC_MOVE_X and CALC_MOVE_Y states.
    """

    fp = FixedPoint(INT_BITS, FRAC_BITS)

    # Movement calculation parameters
    move_speed = 1.0  # pixels/step

    # Test angles and expected movements
    angles_degrees = [0, 45, 90, 135, 180, 225, 270, 315]
    move_speed_fp = fp.to_fixed(move_speed)

    dut._log.info("Movement Multiplication Sequence Test")
    dut._log.info(f"move_speed = {move_speed} (FP: {move_speed_fp:025b})")
    dut._log.info("")

    for angle_deg in angles_degrees:
        angle_rad = angle_deg * np.pi / 180.0

        # Compute sin/cos
        sin_val = np.sin(angle_rad)
        cos_val = np.cos(angle_rad)

        sin_fp = fp.to_fixed(sin_val)
        cos_fp = fp.to_fixed(cos_val)

        # Expected movements (using Python multiply)
        dx_expected = fp.from_fixed(fp.multiply(cos_fp, move_speed_fp))
        dy_expected = fp.from_fixed(fp.multiply(sin_fp, move_speed_fp))

        # Test cos * speed (CALC_MOVE_X equivalent)
        dut.a.value = cos_fp & ((1 << TOTAL_BITS) - 1)
        dut.b.value = move_speed_fp & ((1 << TOTAL_BITS) - 1)
        await Timer(1, unit="ns")

        dx_rtl = fp.from_fixed(int(dut.result.value))

        # Test sin * speed (CALC_MOVE_Y equivalent)
        dut.a.value = sin_fp & ((1 << TOTAL_BITS) - 1)
        dut.b.value = move_speed_fp & ((1 << TOTAL_BITS) - 1)
        await Timer(1, unit="ns")

        dy_rtl = fp.from_fixed(int(dut.result.value))

        # Compare
        dx_error = abs(dx_rtl - dx_expected)
        dy_error = abs(dy_rtl - dy_expected)

        status = "PASS" if dx_error < 1e-4 and dy_error < 1e-4 else "FAIL"

        dut._log.info(f"Angle {angle_deg:3d}°: "
                     f"dx={dx_rtl:7.4f} (exp {dx_expected:7.4f}), "
                     f"dy={dy_rtl:7.4f} (exp {dy_expected:7.4f}) [{status}]")

        assert dx_error < 1e-4, f"dx error too large at {angle_deg}°: {dx_error}"
        assert dy_error < 1e-4, f"dy error too large at {angle_deg}°: {dy_error}"

    dut._log.info("\nMovement multiplication sequence PASSED!")
