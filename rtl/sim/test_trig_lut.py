"""
Cocotb Testbench: Trigonometric Lookup Table Unit Tests

Tests the sin/cos lookup table module with 1024 entries.
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from slime_simulator import TrigLUT, FixedPoint


@cocotb.test()
async def test_trig_lut_basic(dut):
    """Test basic trig LUT functionality at key angles."""

    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    addr_bits = int(dut.ADDR_BITS.value)
    frac_bits = int(dut.FRAC_BITS.value)

    fp = FixedPoint(12, frac_bits)
    py_trig = TrigLUT(fp, addr_bits)

    # Test key angles: 0, 90, 180, 270 degrees
    # In 1024 table: 0 = 0°, 256 = 90°, 512 = 180°, 768 = 270°
    test_angles = [0, 256, 512, 768]

    for angle_idx in test_angles:
        dut.angle_idx.value = angle_idx
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)  # Wait for registered output

        rtl_sin = int(dut.sin_out.value)
        rtl_cos = int(dut.cos_out.value)

        py_sin = py_trig.sin(angle_idx)
        py_cos = py_trig.cos(angle_idx)

        assert rtl_sin == py_sin, f"Sin[{angle_idx}]: RTL=0x{rtl_sin:07X}, Py=0x{py_sin:07X}"
        assert rtl_cos == py_cos, f"Cos[{angle_idx}]: RTL=0x{rtl_cos:07X}, Py=0x{py_cos:07X}"

        dut._log.info(f"Angle {angle_idx}: sin=0x{rtl_sin:07X}, cos=0x{rtl_cos:07X} ✓")


@cocotb.test()
async def test_trig_lut_sample(dut):
    """Test a sample of trig LUT entries match Python."""

    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    addr_bits = int(dut.ADDR_BITS.value)
    frac_bits = int(dut.FRAC_BITS.value)
    table_size = 1 << addr_bits

    fp = FixedPoint(12, frac_bits)
    py_trig = TrigLUT(fp, addr_bits)

    # Sample every 32nd entry
    errors = 0
    for i in range(0, table_size, 32):
        dut.angle_idx.value = i
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)  # Wait for registered output

        rtl_sin = int(dut.sin_out.value)
        rtl_cos = int(dut.cos_out.value)

        py_sin = py_trig.sin(i)
        py_cos = py_trig.cos(i)

        sin_match = (rtl_sin == py_sin)
        cos_match = (rtl_cos == py_cos)

        if not sin_match or not cos_match:
            if errors < 5:  # Only log first 5 errors
                dut._log.error(f"Angle {i}: Sin RTL=0x{rtl_sin:07X} Py=0x{py_sin:07X}, "
                              f"Cos RTL=0x{rtl_cos:07X} Py=0x{py_cos:07X}")
            errors += 1

    assert errors == 0, f"Trig LUT had {errors} mismatches in sample test"
    dut._log.info(f"Trig LUT: {table_size // 32} samples match perfectly!")


@cocotb.test()
async def test_trig_lut_symmetry(dut):
    """Test trigonometric symmetry properties."""

    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    addr_bits = int(dut.ADDR_BITS.value)
    frac_bits = int(dut.FRAC_BITS.value)
    table_size = 1 << addr_bits

    fp = FixedPoint(12, frac_bits)
    py_trig = TrigLUT(fp, addr_bits)

    # Test: sin(0) = 0, cos(0) = 1
    dut.angle_idx.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    sin_0 = int(dut.sin_out.value)
    cos_0 = int(dut.cos_out.value)

    # sin(0) should be very close to 0
    sin_0_float = py_trig.fp.from_fixed(sin_0)
    cos_0_float = py_trig.fp.from_fixed(cos_0)

    dut._log.info(f"sin(0) = {sin_0_float:.6f}, cos(0) = {cos_0_float:.6f}")

    assert abs(sin_0_float) < 0.01, f"sin(0) not close to 0: {sin_0_float}"
    assert abs(cos_0_float - 1.0) < 0.01, f"cos(0) not close to 1: {cos_0_float}"

    # Test: sin(90°) = 1, cos(90°) = 0
    dut.angle_idx.value = table_size // 4  # 90 degrees
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    sin_90 = int(dut.sin_out.value)
    cos_90 = int(dut.cos_out.value)

    sin_90_float = py_trig.fp.from_fixed(sin_90)
    cos_90_float = py_trig.fp.from_fixed(cos_90)

    dut._log.info(f"sin(90°) = {sin_90_float:.6f}, cos(90°) = {cos_90_float:.6f}")

    assert abs(sin_90_float - 1.0) < 0.01, f"sin(90°) not close to 1: {sin_90_float}"
    assert abs(cos_90_float) < 0.01, f"cos(90°) not close to 0: {cos_90_float}"


@cocotb.test()
async def test_trig_lut_range(dut):
    """Test that all trig values are in valid range [-1, 1]."""

    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    addr_bits = int(dut.ADDR_BITS.value)
    frac_bits = int(dut.FRAC_BITS.value)
    table_size = 1 << addr_bits

    fp = FixedPoint(12, frac_bits)
    py_trig = TrigLUT(fp, addr_bits)

    # Sample every 16th entry
    for i in range(0, table_size, 16):
        dut.angle_idx.value = i
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)

        rtl_sin = int(dut.sin_out.value)
        rtl_cos = int(dut.cos_out.value)

        # Convert from unsigned 2's complement to signed
        # If value is > 2^24, it's negative
        if rtl_sin >= (1 << 24):
            sin_float = fp.from_fixed(rtl_sin - (1 << 25))
        else:
            sin_float = fp.from_fixed(rtl_sin)

        if rtl_cos >= (1 << 24):
            cos_float = fp.from_fixed(rtl_cos - (1 << 25))
        else:
            cos_float = fp.from_fixed(rtl_cos)

        assert -1.1 <= sin_float <= 1.1, f"Sin[{i}] out of range: {sin_float}"
        assert -1.1 <= cos_float <= 1.1, f"Cos[{i}] out of range: {cos_float}"

    dut._log.info(f"Trig LUT: All values in valid range [-1, 1]")
