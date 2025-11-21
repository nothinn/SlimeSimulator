"""
Cocotb testbench for LFSR module
Verifies that RTL LFSR matches Python implementation
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer
import sys
import os

# Add parent directory to path for importing Python simulator
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from slime_simulator import LFSR


@cocotb.test()
async def test_lfsr_sequence(dut):
    """Test that RTL LFSR produces same sequence as Python LFSR"""

    # Create clock
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Get parameters from DUT
    width = int(dut.WIDTH.value)
    seed = int(dut.SEED.value)

    dut._log.info(f"Testing {width}-bit LFSR with seed 0x{seed:X}")

    # Create Python LFSR with same parameters
    py_lfsr = LFSR(width=width, seed=seed)

    # Reset
    dut.rst_n.value = 0
    dut.enable.value = 0
    dut.load.value = 0
    dut.seed_val.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    # Verify initial state matches seed
    rtl_state = int(dut.lfsr_out.value)
    assert rtl_state == seed, f"Initial state mismatch: RTL=0x{rtl_state:X}, expected=0x{seed:X}"
    dut._log.info(f"Initial state: 0x{rtl_state:X}")

    # Step both LFSRs and compare
    num_steps = 1000
    dut._log.info(f"Running {num_steps} LFSR steps...")

    for i in range(num_steps):
        # Step Python LFSR
        py_state = py_lfsr.step()

        # Step RTL LFSR
        dut.enable.value = 1
        await RisingEdge(dut.clk)
        dut.enable.value = 0
        await RisingEdge(dut.clk)

        # Compare
        rtl_state = int(dut.lfsr_out.value)
        assert rtl_state == py_state, \
            f"Step {i}: RTL=0x{rtl_state:X}, Python=0x{py_state:X}"

        if i < 10 or i % 100 == 0:
            dut._log.info(f"Step {i}: 0x{rtl_state:08X} ✓")

    dut._log.info(f"All {num_steps} steps matched!")


@cocotb.test()
async def test_lfsr_load(dut):
    """Test loading a new seed"""

    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    width = int(dut.WIDTH.value)

    # Reset
    dut.rst_n.value = 0
    dut.enable.value = 0
    dut.load.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    # Load new seed
    new_seed = 0x12345678 & ((1 << width) - 1)
    dut._log.info(f"Loading new seed: 0x{new_seed:X}")

    dut.seed_val.value = new_seed
    dut.load.value = 1
    await RisingEdge(dut.clk)
    dut.load.value = 0
    await RisingEdge(dut.clk)

    # Verify new seed loaded
    rtl_state = int(dut.lfsr_out.value)
    assert rtl_state == new_seed, f"Load failed: RTL=0x{rtl_state:X}, expected=0x{new_seed:X}"
    dut._log.info(f"New seed loaded successfully: 0x{rtl_state:X}")

    # Step and verify sequence continues from new seed
    py_lfsr = LFSR(width=width, seed=new_seed)

    for i in range(10):
        py_state = py_lfsr.step()
        dut.enable.value = 1
        await RisingEdge(dut.clk)
        dut.enable.value = 0
        await RisingEdge(dut.clk)

        rtl_state = int(dut.lfsr_out.value)
        assert rtl_state == py_state, \
            f"Step {i} after load: RTL=0x{rtl_state:X}, Python=0x{py_state:X}"

    dut._log.info("Sequence after load matches!")


@cocotb.test()
async def test_lfsr_zero_seed_protection(dut):
    """Test that zero seed is rejected (LFSR would lock up)"""

    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.rst_n.value = 0
    dut.enable.value = 0
    dut.load.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    # Try to load zero seed
    dut.seed_val.value = 0
    dut.load.value = 1
    await RisingEdge(dut.clk)
    dut.load.value = 0
    await RisingEdge(dut.clk)

    # Should fall back to default SEED, not zero
    rtl_state = int(dut.lfsr_out.value)
    assert rtl_state != 0, f"Zero seed was accepted! State=0x{rtl_state:X}"
    dut._log.info(f"Zero seed rejected, state=0x{rtl_state:X} ✓")
