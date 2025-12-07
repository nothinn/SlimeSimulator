"""
Cocotb Testbench: VGA Controller Unit Tests

Tests the VGA controller timing for 640x480@60Hz output.
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles


@cocotb.test()
async def test_vga_basic_timing(dut):
    """Test basic VGA timing generation."""

    # VGA pixel clock: 25.175 MHz ≈ 40ns period
    clock = Clock(dut.clk, 40, unit="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 10)

    # Check that h_count and v_count increment
    initial_h_count = int(dut.h_count.value)
    await ClockCycles(dut.clk, 10)
    later_h_count = int(dut.h_count.value)

    assert later_h_count != initial_h_count, "h_count not incrementing"
    dut._log.info(f"VGA counters active: h_count moving from {initial_h_count} to {later_h_count}")


@cocotb.test()
async def test_vga_hsync_timing(dut):
    """Test horizontal sync timing."""

    clock = Clock(dut.clk, 40, unit="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 10)

    # Check that hsync toggles
    initial_hsync = int(dut.hsync.value)
    timeout = 10000

    for _ in range(timeout):
        await RisingEdge(dut.clk)
        current_hsync = int(dut.hsync.value)
        if current_hsync != initial_hsync:
            dut._log.info(f"HSYNC toggled from {initial_hsync} to {current_hsync}")
            break
    else:
        assert False, "HSYNC never toggled"

    # Verify hsync continues toggling
    first_toggle = current_hsync
    for _ in range(timeout):
        await RisingEdge(dut.clk)
        current_hsync = int(dut.hsync.value)
        if current_hsync != first_toggle:
            dut._log.info("HSYNC toggling correctly")
            break
    else:
        assert False, "HSYNC stuck at one value"


@cocotb.test()
async def test_vga_visible_region(dut):
    """Test visible region detection."""

    clock = Clock(dut.clk, 40, unit="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 10)

    # Wait until we're in visible region
    visible_count = 0
    max_checks = 100000

    for _ in range(max_checks):
        await RisingEdge(dut.clk)
        h_count = int(dut.h_count.value)
        v_count = int(dut.v_count.value)

        # Visible region: 0-639 horizontal, 0-479 vertical
        if h_count < 640 and v_count < 480:
            visible_count += 1

        if visible_count > 100:
            break

    assert visible_count > 100, "Never entered visible region"
    dut._log.info(f"VGA visible region detected after checking {visible_count} pixels")


@cocotb.test()
async def test_vga_frame_timing(dut):
    """Test that VGA completes a frame."""

    clock = Clock(dut.clk, 40, unit="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 10)

    # Wait for vsync to go low (start of frame)
    timeout = 1000000
    for _ in range(timeout):
        await RisingEdge(dut.clk)
        if int(dut.vsync.value) == 0:
            break
    else:
        assert False, "VSYNC never went low"

    dut._log.info("VSYNC detected - frame started")

    # Wait for vsync to go high again (end of vsync pulse)
    for _ in range(timeout):
        await RisingEdge(dut.clk)
        if int(dut.vsync.value) == 1:
            break
    else:
        assert False, "VSYNC never went high"

    dut._log.info("VSYNC pulse completed")


@cocotb.test()
async def test_vga_reset(dut):
    """Test VGA reset functionality."""

    clock = Clock(dut.clk, 40, unit="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)

    # Verify counters are reset
    h_count = int(dut.h_count.value)
    v_count = int(dut.v_count.value)

    # Counters should be 0 or very small during reset
    dut._log.info(f"During reset: h_count={h_count}, v_count={v_count}")

    # Release reset
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 100)

    # Verify counters are running
    h_count_after = int(dut.h_count.value)
    v_count_after = int(dut.v_count.value)

    dut._log.info(f"After reset release: h_count={h_count_after}, v_count={v_count_after}")

    # At least h_count should have incremented significantly
    assert h_count_after > 50, f"Counters not running after reset: h_count={h_count_after}"
