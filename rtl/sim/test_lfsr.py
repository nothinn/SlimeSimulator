"""
Cocotb Testbench: LFSR Unit Tests

Tests the 32-bit LFSR (Linear Feedback Shift Register) module.
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer, ClockCycles
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from slime_simulator import LFSR


@cocotb.test()
async def test_lfsr_basic(dut):
    """Test LFSR basic functionality with reset and load."""

    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.rst_n.value = 0
    dut.enable.value = 0
    dut.load.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

    # Load seed
    seed = 0x12345678
    dut.load.value = 1
    dut.seed_val.value = seed
    await RisingEdge(dut.clk)
    dut.load.value = 0
    await RisingEdge(dut.clk)

    # Verify initial state
    rtl_state = int(dut.lfsr_out.value)
    assert rtl_state == seed, f"Initial state mismatch: RTL={rtl_state:08X}, Expected={seed:08X}"

    dut._log.info(f"LFSR basic test passed! Seed loaded correctly: 0x{seed:08X}")


@cocotb.test()
async def test_lfsr_sequence(dut):
    """Test LFSR produces correct sequence matching Python reference."""

    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.rst_n.value = 0
    dut.enable.value = 0
    dut.load.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

    # Initialize Python LFSR with same seed
    seed = 0xDEADBEEF
    py_lfsr = LFSR(32, seed)

    # Load seed into RTL
    dut.load.value = 1
    dut.seed_val.value = seed
    await RisingEdge(dut.clk)
    dut.load.value = 0
    await RisingEdge(dut.clk)

    # Verify initial state
    rtl_state = int(dut.lfsr_out.value)
    assert rtl_state == seed, f"Initial state mismatch: RTL={rtl_state:08X}, Py={seed:08X}"

    # Run 100 steps and compare
    dut.enable.value = 1
    errors = 0

    for i in range(100):
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")  # Small delay for signals to settle
        rtl_state = int(dut.lfsr_out.value)
        py_state = py_lfsr.step()

        if rtl_state != py_state:
            if errors < 5:  # Only log first 5 errors
                dut._log.error(f"Step {i+1}: RTL=0x{rtl_state:08X}, Py=0x{py_state:08X}")
            errors += 1

    assert errors == 0, f"LFSR sequence had {errors} mismatches in 100 steps"
    dut._log.info("LFSR: 100 steps match perfectly!")


@cocotb.test()
async def test_lfsr_non_zero(dut):
    """Test LFSR never outputs zero (maximal-length sequence property)."""

    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.rst_n.value = 0
    dut.enable.value = 0
    dut.load.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

    # Load non-zero seed
    seed = 0x00000001
    dut.load.value = 1
    dut.seed_val.value = seed
    await RisingEdge(dut.clk)
    dut.load.value = 0
    await RisingEdge(dut.clk)

    # Run 1000 steps and verify never zero
    dut.enable.value = 1

    for i in range(1000):
        await RisingEdge(dut.clk)
        rtl_state = int(dut.lfsr_out.value)
        assert rtl_state != 0, f"LFSR output zero at step {i}"

    dut._log.info("LFSR: Never output zero in 1000 steps!")
