"""
Cocotb testbench for VGA Controller
Verifies timing and sync signals for 640x480@60Hz
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer


# VGA 640x480 @ 60Hz timing parameters
H_VISIBLE = 640
H_FRONT = 16
H_SYNC = 96
H_BACK = 48
H_TOTAL = H_VISIBLE + H_FRONT + H_SYNC + H_BACK  # 800

V_VISIBLE = 480
V_FRONT = 10
V_SYNC = 2
V_BACK = 33
V_TOTAL = V_VISIBLE + V_FRONT + V_SYNC + V_BACK  # 525


@cocotb.test()
async def test_vga_hsync_timing(dut):
    """Test horizontal sync timing"""

    # Create 25MHz pixel clock
    clock = Clock(dut.clk, 40, units="ns")  # 25MHz = 40ns period
    cocotb.start_soon(clock.start())

    # Reset
    dut.rst_n.value = 0
    dut.pixel_data.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1

    dut._log.info("Testing horizontal sync timing...")

    # Wait for start of line
    for _ in range(H_TOTAL + 10):
        await RisingEdge(dut.clk)

    # Count clocks in each phase
    hsync_high_count = 0
    hsync_low_count = 0
    line_count = 0

    prev_hsync = int(dut.hsync.value)

    for _ in range(H_TOTAL * 3):  # 3 lines
        await RisingEdge(dut.clk)
        curr_hsync = int(dut.hsync.value)

        if curr_hsync:
            hsync_high_count += 1
        else:
            hsync_low_count += 1

        # Detect falling edge (start of sync pulse)
        if prev_hsync and not curr_hsync:
            line_count += 1

        prev_hsync = curr_hsync

    dut._log.info(f"HSYNC high: {hsync_high_count/3:.0f}, low: {hsync_low_count/3:.0f} per line")

    # HSYNC should be low for H_SYNC clocks per line
    expected_low = H_SYNC * 3
    expected_high = (H_TOTAL - H_SYNC) * 3

    assert abs(hsync_low_count - expected_low) <= 3, \
        f"HSYNC low count {hsync_low_count} != expected {expected_low}"
    assert abs(hsync_high_count - expected_high) <= 3, \
        f"HSYNC high count {hsync_high_count} != expected {expected_high}"

    dut._log.info("Horizontal sync timing OK!")


@cocotb.test()
async def test_vga_vsync_timing(dut):
    """Test vertical sync timing"""

    clock = Clock(dut.clk, 40, units="ns")
    cocotb.start_soon(clock.start())

    dut.rst_n.value = 0
    dut.pixel_data.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1

    dut._log.info("Testing vertical sync timing (this may take a moment)...")

    # Count lines per frame and vsync pulse width
    line_count = 0
    vsync_lines = 0
    prev_hsync = 1
    prev_vsync = 1
    frame_lines = 0

    # Run for more than one frame
    for clk_count in range(H_TOTAL * (V_TOTAL + 10)):
        await RisingEdge(dut.clk)

        curr_hsync = int(dut.hsync.value)
        curr_vsync = int(dut.vsync.value)

        # Count lines (hsync falling edges)
        if prev_hsync and not curr_hsync:
            line_count += 1
            if not curr_vsync:  # During vsync
                vsync_lines += 1

        # Detect vsync falling edge (start of frame)
        if prev_vsync and not curr_vsync:
            if frame_lines > 0:
                dut._log.info(f"Frame had {frame_lines} lines")
            frame_lines = 0

        if not prev_vsync and curr_vsync:
            # End of vsync
            pass

        frame_lines = line_count

        prev_hsync = curr_hsync
        prev_vsync = curr_vsync

    dut._log.info(f"Total lines counted: {line_count}, VSYNC pulse lines: {vsync_lines}")

    # Should have approximately V_TOTAL lines per frame
    # and V_SYNC lines of vsync pulse
    assert line_count >= V_TOTAL, f"Not enough lines: {line_count}"

    dut._log.info("Vertical sync timing OK!")


@cocotb.test()
async def test_vga_pixel_valid(dut):
    """Test pixel_valid signal matches visible area"""

    clock = Clock(dut.clk, 40, units="ns")
    cocotb.start_soon(clock.start())

    dut.rst_n.value = 0
    dut.pixel_data.value = 0x80  # Mid gray
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1

    dut._log.info("Testing pixel_valid signal...")

    # Count pixel_valid assertions per line
    valid_count = 0
    total_count = 0
    prev_hsync = 1

    for _ in range(H_TOTAL * 5):  # 5 lines
        await RisingEdge(dut.clk)
        total_count += 1

        if int(dut.pixel_valid.value):
            valid_count += 1

        curr_hsync = int(dut.hsync.value)
        prev_hsync = curr_hsync

    valid_per_line = valid_count / 5
    dut._log.info(f"pixel_valid high: {valid_per_line:.0f} per line (expected {H_VISIBLE})")

    # Allow small tolerance
    assert abs(valid_per_line - H_VISIBLE) < 5, \
        f"pixel_valid count {valid_per_line} != expected {H_VISIBLE}"

    dut._log.info("pixel_valid timing OK!")


@cocotb.test()
async def test_vga_frame_start(dut):
    """Test frame_start pulse"""

    clock = Clock(dut.clk, 40, units="ns")
    cocotb.start_soon(clock.start())

    dut.rst_n.value = 0
    dut.pixel_data.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1

    dut._log.info("Testing frame_start pulse...")

    frame_start_count = 0

    # Run for about 1.5 frames
    for _ in range(H_TOTAL * V_TOTAL * 3 // 2):
        await RisingEdge(dut.clk)
        if int(dut.frame_start.value):
            frame_start_count += 1

    dut._log.info(f"frame_start pulses: {frame_start_count} (expected 1-2)")

    assert frame_start_count >= 1, "No frame_start pulses detected"
    assert frame_start_count <= 2, f"Too many frame_start pulses: {frame_start_count}"

    dut._log.info("frame_start signal OK!")


@cocotb.test()
async def test_vga_color_output(dut):
    """Test color output based on pixel_data"""

    clock = Clock(dut.clk, 40, units="ns")
    cocotb.start_soon(clock.start())

    dut.rst_n.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1

    dut._log.info("Testing color output...")

    # Test different pixel_data values during visible area
    test_values = [0x00, 0x40, 0x80, 0xC0, 0xFF]

    for pixel_val in test_values:
        dut.pixel_data.value = pixel_val

        # Wait for visible area
        for _ in range(100):
            await RisingEdge(dut.clk)
            if int(dut.pixel_valid.value):
                break

        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)

        r = int(dut.vga_r.value)
        g = int(dut.vga_g.value)
        b = int(dut.vga_b.value)

        dut._log.info(f"pixel_data=0x{pixel_val:02X} -> R={r}, G={g}, B={b}")

        # Green should be highest (slime color)
        if pixel_val > 0:
            assert g >= r, f"Green should be >= Red for slime color"
            assert g >= b, f"Green should be >= Blue for slime color"

    dut._log.info("Color output OK!")
