"""
Cocotb testbench for Trig Lookup Table
Verifies sin/cos values match expected mathematical results
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
import math


def to_fixed(value, frac_bits):
    """Convert float to fixed-point integer."""
    return int(round(value * (1 << frac_bits)))


def from_fixed(value, frac_bits, total_bits):
    """Convert fixed-point integer to float (handle signed)."""
    if value >= (1 << (total_bits - 1)):
        value -= (1 << total_bits)
    return value / (1 << frac_bits)


@cocotb.test()
async def test_trig_basic(dut):
    """Test basic sin/cos values at key angles"""

    # Create clock
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    addr_bits = int(dut.ADDR_BITS.value)
    data_bits = int(dut.DATA_BITS.value)
    frac_bits = int(dut.FRAC_BITS.value)
    table_size = 1 << addr_bits

    dut._log.info(f"Testing trig LUT: {table_size} entries, Q{data_bits-frac_bits-1}.{frac_bits}")

    # Test key angles: 0, 90, 180, 270 degrees
    # angle_idx = angle_degrees * table_size / 360
    test_angles = [
        (0, 0.0, 1.0),      # sin(0)=0, cos(0)=1
        (table_size // 4, 1.0, 0.0),   # sin(90)=1, cos(90)=0
        (table_size // 2, 0.0, -1.0),  # sin(180)=0, cos(180)=-1
        (3 * table_size // 4, -1.0, 0.0),  # sin(270)=-1, cos(270)=0
    ]

    for angle_idx, expected_sin, expected_cos in test_angles:
        dut.angle_idx.value = angle_idx
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)  # Allow for registered output

        sin_val = from_fixed(int(dut.sin_out.value), frac_bits, data_bits)
        cos_val = from_fixed(int(dut.cos_out.value), frac_bits, data_bits)

        angle_deg = angle_idx * 360 / table_size
        dut._log.info(f"Angle {angle_deg}°: sin={sin_val:.4f} (exp {expected_sin}), "
                      f"cos={cos_val:.4f} (exp {expected_cos})")

        # Allow small error
        sin_error = abs(sin_val - expected_sin)
        cos_error = abs(cos_val - expected_cos)
        max_error = 0.01  # 1% tolerance

        assert sin_error < max_error, f"sin({angle_deg}°) error: {sin_error}"
        assert cos_error < max_error, f"cos({angle_deg}°) error: {cos_error}"


@cocotb.test()
async def test_trig_sweep(dut):
    """Sweep through all angles and verify sin^2 + cos^2 = 1"""

    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    addr_bits = int(dut.ADDR_BITS.value)
    data_bits = int(dut.DATA_BITS.value)
    frac_bits = int(dut.FRAC_BITS.value)
    table_size = 1 << addr_bits

    dut._log.info(f"Sweeping {table_size} angles, checking sin²+cos²=1...")

    max_error = 0
    error_count = 0

    for angle_idx in range(table_size):
        dut.angle_idx.value = angle_idx
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)

        sin_val = from_fixed(int(dut.sin_out.value), frac_bits, data_bits)
        cos_val = from_fixed(int(dut.cos_out.value), frac_bits, data_bits)

        # Check sin^2 + cos^2 = 1
        magnitude = sin_val ** 2 + cos_val ** 2
        error = abs(magnitude - 1.0)

        if error > max_error:
            max_error = error

        if error > 0.01:  # 1% tolerance
            error_count += 1
            if error_count <= 5:
                dut._log.warning(f"Angle idx {angle_idx}: sin²+cos²={magnitude:.6f}, error={error:.6f}")

    dut._log.info(f"Max error: {max_error:.6f}, errors > 1%: {error_count}")
    assert error_count == 0, f"{error_count} angles had sin²+cos²≠1"


@cocotb.test()
async def test_trig_vs_math(dut):
    """Compare LUT values against Python math library"""

    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    addr_bits = int(dut.ADDR_BITS.value)
    data_bits = int(dut.DATA_BITS.value)
    frac_bits = int(dut.FRAC_BITS.value)
    table_size = 1 << addr_bits

    dut._log.info("Comparing against Python math.sin/cos...")

    max_sin_error = 0
    max_cos_error = 0

    # Test every 16th entry for speed
    for angle_idx in range(0, table_size, max(1, table_size // 64)):
        angle_rad = 2 * math.pi * angle_idx / table_size
        expected_sin = math.sin(angle_rad)
        expected_cos = math.cos(angle_rad)

        dut.angle_idx.value = angle_idx
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)

        sin_val = from_fixed(int(dut.sin_out.value), frac_bits, data_bits)
        cos_val = from_fixed(int(dut.cos_out.value), frac_bits, data_bits)

        sin_error = abs(sin_val - expected_sin)
        cos_error = abs(cos_val - expected_cos)

        max_sin_error = max(max_sin_error, sin_error)
        max_cos_error = max(max_cos_error, cos_error)

        if angle_idx < 5 or angle_idx % 64 == 0:
            dut._log.info(f"idx {angle_idx}: sin={sin_val:.4f} vs {expected_sin:.4f}, "
                          f"cos={cos_val:.4f} vs {expected_cos:.4f}")

    dut._log.info(f"Max sin error: {max_sin_error:.6f}, max cos error: {max_cos_error:.6f}")

    # Allow for quantization error (1 LSB = 1/2^frac_bits)
    max_allowed = 2.0 / (1 << frac_bits)
    assert max_sin_error < max_allowed, f"Sin error {max_sin_error} exceeds {max_allowed}"
    assert max_cos_error < max_allowed, f"Cos error {max_cos_error} exceeds {max_allowed}"

    dut._log.info("Trig LUT matches math library within tolerance!")
