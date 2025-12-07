"""
Cocotb Testbench: Fixed-Point Multiplier Unit Tests

Tests the Q12.12 fixed-point multiplier module.
"""

import cocotb
from cocotb.triggers import Timer
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from slime_simulator import FixedPoint


@cocotb.test()
async def test_fixed_point_basic(dut):
    """Test basic fixed-point multiplication."""

    frac_bits = int(dut.FRAC_BITS.value)
    total_bits = int(dut.TOTAL_BITS.value)

    fp = FixedPoint(12, frac_bits)

    # Test 1.0 * 1.0 = 1.0
    a_fp = fp.to_fixed(1.0)
    b_fp = fp.to_fixed(1.0)

    dut.a.value = a_fp
    dut.b.value = b_fp
    await Timer(1, unit="ns")

    rtl_result = int(dut.result.value)
    py_result = fp.multiply(a_fp, b_fp)

    assert rtl_result == py_result, f"1.0 * 1.0: RTL=0x{rtl_result:08X}, Py=0x{py_result:08X}"
    dut._log.info(f"1.0 * 1.0 = {fp.from_fixed(rtl_result):.4f} ✓")


@cocotb.test()
async def test_fixed_point_positive(dut):
    """Test positive number multiplication."""

    frac_bits = int(dut.FRAC_BITS.value)
    total_bits = int(dut.TOTAL_BITS.value)

    fp = FixedPoint(12, frac_bits)

    test_cases = [
        (2.0, 2.0),     # 4.0
        (0.5, 0.5),     # 0.25
        (1.5, 2.0),     # 3.0
        (0.125, 8.0),   # 1.0
    ]

    for a_float, b_float in test_cases:
        a_fp = fp.to_fixed(a_float)
        b_fp = fp.to_fixed(b_float)

        dut.a.value = a_fp
        dut.b.value = b_fp
        await Timer(1, unit="ns")

        rtl_result = int(dut.result.value)
        py_result = fp.multiply(a_fp, b_fp)

        # Allow 1 LSB difference due to rounding
        diff = abs((rtl_result & ((1 << total_bits) - 1)) -
                   (py_result & ((1 << total_bits) - 1)))

        assert diff <= 1, f"{a_float} * {b_float}: RTL=0x{rtl_result:08X}, Py=0x{py_result:08X}"
        dut._log.info(f"{a_float} * {b_float} = {fp.from_fixed(rtl_result):.4f} ✓")


@cocotb.test()
async def test_fixed_point_negative(dut):
    """Test negative number multiplication."""

    frac_bits = int(dut.FRAC_BITS.value)
    total_bits = int(dut.TOTAL_BITS.value)

    fp = FixedPoint(12, frac_bits)

    test_cases = [
        (-1.0, 1.0),    # -1.0
        (-1.0, -1.0),   # 1.0
        (1.5, -2.5),    # -3.75
        (-0.5, 0.866),  # ~-0.433
    ]

    for a_float, b_float in test_cases:
        a_fp = fp.to_fixed(a_float)
        b_fp = fp.to_fixed(b_float)

        dut.a.value = a_fp
        dut.b.value = b_fp
        await Timer(1, unit="ns")

        rtl_result = int(dut.result.value)
        py_result = fp.multiply(a_fp, b_fp)

        # Allow 1 LSB difference due to rounding
        diff = abs((rtl_result & ((1 << total_bits) - 1)) -
                   (py_result & ((1 << total_bits) - 1)))

        assert diff <= 1, f"{a_float} * {b_float}: RTL=0x{rtl_result:08X}, Py=0x{py_result:08X}"
        dut._log.info(f"{a_float} * {b_float} = {fp.from_fixed(rtl_result):.4f} ✓")


@cocotb.test()
async def test_fixed_point_zero(dut):
    """Test multiplication with zero."""

    frac_bits = int(dut.FRAC_BITS.value)
    fp = FixedPoint(12, frac_bits)

    # Test 0 * anything = 0
    test_cases = [
        (0.0, 100.0),
        (0.0, -100.0),
        (0.0, 0.0),
    ]

    for a_float, b_float in test_cases:
        a_fp = fp.to_fixed(a_float)
        b_fp = fp.to_fixed(b_float)

        dut.a.value = a_fp
        dut.b.value = b_fp
        await Timer(1, unit="ns")

        rtl_result = int(dut.result.value)
        py_result = fp.multiply(a_fp, b_fp)

        assert rtl_result == py_result, f"{a_float} * {b_float}: RTL=0x{rtl_result:08X}, Py=0x{py_result:08X}"
        dut._log.info(f"{a_float} * {b_float} = 0.0 ✓")


@cocotb.test()
async def test_fixed_point_trig_values(dut):
    """Test with typical trigonometric values."""

    frac_bits = int(dut.FRAC_BITS.value)
    total_bits = int(dut.TOTAL_BITS.value)

    fp = FixedPoint(12, frac_bits)

    test_cases = [
        (0.707, 0.707),  # sin(45) * cos(45) ≈ 0.5
        (0.866, 0.5),    # sin(60) * cos(60) ≈ 0.433
        (1.0, 0.5),      # 0.5
    ]

    for a_float, b_float in test_cases:
        a_fp = fp.to_fixed(a_float)
        b_fp = fp.to_fixed(b_float)

        dut.a.value = a_fp
        dut.b.value = b_fp
        await Timer(1, unit="ns")

        rtl_result = int(dut.result.value)
        py_result = fp.multiply(a_fp, b_fp)

        # Allow 1 LSB difference due to rounding
        diff = abs((rtl_result & ((1 << total_bits) - 1)) -
                   (py_result & ((1 << total_bits) - 1)))

        assert diff <= 1, f"{a_float} * {b_float}: RTL=0x{rtl_result:08X}, Py=0x{py_result:08X}"
        dut._log.info(f"{a_float} * {b_float} = {fp.from_fixed(rtl_result):.4f} ✓")
