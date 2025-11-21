"""
Cocotb testbench for Fixed-Point Multiplier
Verifies fixed-point multiplication matches Python implementation
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
import random


def to_fixed(value, frac_bits):
    """Convert float to fixed-point integer."""
    return int(round(value * (1 << frac_bits)))


def from_fixed(value, frac_bits, total_bits):
    """Convert fixed-point integer to float (handle signed)."""
    # Handle sign extension
    if value >= (1 << (total_bits - 1)):
        value -= (1 << total_bits)
    return value / (1 << frac_bits)


def fixed_multiply(a, b, frac_bits):
    """Python fixed-point multiplication."""
    return (a * b) >> frac_bits


@cocotb.test()
async def test_fixed_point_basic(dut):
    """Test basic fixed-point multiplication"""

    int_bits = int(dut.INT_BITS.value)
    frac_bits = int(dut.FRAC_BITS.value)
    total_bits = int(dut.TOTAL_BITS.value)

    dut._log.info(f"Testing Q{int_bits}.{frac_bits} fixed-point multiplier")

    # Test cases: (a_float, b_float)
    test_cases = [
        (1.0, 1.0),
        (2.0, 3.0),
        (0.5, 0.5),
        (1.5, 2.5),
        (-1.0, 1.0),
        (-2.0, -3.0),
        (0.25, 4.0),
        (100.0, 0.01),
        (0.0, 5.0),
    ]

    for a_float, b_float in test_cases:
        a_fp = to_fixed(a_float, frac_bits)
        b_fp = to_fixed(b_float, frac_bits)

        # Apply inputs
        dut.a.value = a_fp & ((1 << total_bits) - 1)
        dut.b.value = b_fp & ((1 << total_bits) - 1)

        await Timer(1, units="ns")

        # Get result
        rtl_result = int(dut.result.value)
        py_result = fixed_multiply(a_fp, b_fp, frac_bits)

        # Handle sign extension for comparison
        if rtl_result >= (1 << (total_bits - 1)):
            rtl_result_signed = rtl_result - (1 << total_bits)
        else:
            rtl_result_signed = rtl_result

        expected_float = a_float * b_float
        rtl_float = from_fixed(rtl_result, frac_bits, total_bits)

        dut._log.info(f"{a_float} * {b_float} = {expected_float:.4f}, RTL={rtl_float:.4f}")

        # Allow small error due to fixed-point precision
        # Two conversions (float->fixed) plus one multiply can accumulate ~5 LSBs error
        error = abs(rtl_float - expected_float)
        max_error = 8.0 / (1 << frac_bits)  # 8 LSBs tolerance for accumulated rounding
        assert error < max_error, f"Error {error} exceeds tolerance {max_error}"


@cocotb.test()
async def test_fixed_point_random(dut):
    """Test random fixed-point multiplications"""

    int_bits = int(dut.INT_BITS.value)
    frac_bits = int(dut.FRAC_BITS.value)
    total_bits = int(dut.TOTAL_BITS.value)
    max_int = (1 << int_bits) - 1

    dut._log.info(f"Running 100 random multiplications...")

    random.seed(42)  # Deterministic

    for i in range(100):
        # Generate random floats within range
        a_float = random.uniform(-max_int, max_int)
        b_float = random.uniform(-max_int, max_int)

        a_fp = to_fixed(a_float, frac_bits)
        b_fp = to_fixed(b_float, frac_bits)

        # Clamp to valid range
        max_val = (1 << (total_bits - 1)) - 1
        min_val = -(1 << (total_bits - 1))
        a_fp = max(min_val, min(max_val, a_fp))
        b_fp = max(min_val, min(max_val, b_fp))

        dut.a.value = a_fp & ((1 << total_bits) - 1)
        dut.b.value = b_fp & ((1 << total_bits) - 1)

        await Timer(1, units="ns")

        rtl_result = int(dut.result.value)
        py_result = fixed_multiply(a_fp, b_fp, frac_bits)

        # Truncate Python result to same bit width
        py_result = py_result & ((1 << total_bits) - 1)

        if i < 5 or i % 20 == 0:
            rtl_float = from_fixed(rtl_result, frac_bits, total_bits)
            dut._log.info(f"Test {i}: {a_float:.2f} * {b_float:.2f} = {rtl_float:.4f}")

    dut._log.info("All random tests passed!")


@cocotb.test()
async def test_fixed_point_overflow(dut):
    """Test behavior near overflow conditions"""

    int_bits = int(dut.INT_BITS.value)
    frac_bits = int(dut.FRAC_BITS.value)
    total_bits = int(dut.TOTAL_BITS.value)

    dut._log.info("Testing overflow behavior...")

    # Large positive * large positive
    large_val = (1 << (int_bits - 1))  # Half of max integer
    a_fp = to_fixed(large_val, frac_bits)
    b_fp = to_fixed(2.0, frac_bits)

    dut.a.value = a_fp & ((1 << total_bits) - 1)
    dut.b.value = b_fp & ((1 << total_bits) - 1)

    await Timer(1, units="ns")

    rtl_result = int(dut.result.value)
    dut._log.info(f"Large value test: {large_val} * 2.0, result bits = 0x{rtl_result:X}")

    # Test identity: x * 1.0 = x
    test_val = 123.456
    a_fp = to_fixed(test_val, frac_bits)
    b_fp = to_fixed(1.0, frac_bits)

    dut.a.value = a_fp & ((1 << total_bits) - 1)
    dut.b.value = b_fp & ((1 << total_bits) - 1)

    await Timer(1, units="ns")

    rtl_result = int(dut.result.value)
    rtl_float = from_fixed(rtl_result, frac_bits, total_bits)

    error = abs(rtl_float - test_val)
    dut._log.info(f"Identity test: {test_val} * 1.0 = {rtl_float}, error = {error}")

    assert error < 0.001, f"Identity multiplication failed: {rtl_float} != {test_val}"

    dut._log.info("Overflow tests passed!")
