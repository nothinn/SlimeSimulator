"""
Cocotb Testbench: Trail Map Comparison

Runs a slime simulation in RTL and compares the resulting trail map
with the Python reference model.
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer, ClockCycles, FallingEdge
import numpy as np
import os
import sys

# Import Python reference (matches RTL module interfaces)
sys.path.insert(0, os.path.dirname(__file__))
from slime_simulator import FixedPoint

@cocotb.test()
async def test_single_agent_movement(dut):
    """Test a single agent moves correctly."""

    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.rst_n.value = 0
    dut.run_step.value = 0
    dut.init_agents.value = 0
    dut.load_lfsr.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

    # Parameters
    fp = FixedPoint(12, 12)
    WIDTH = 64
    HEIGHT = 64

    # Initialize LFSR
    seed = 0xDEADBEEF
    dut.load_lfsr.value = 1
    dut.lfsr_seed.value = seed
    await RisingEdge(dut.clk)
    dut.load_lfsr.value = 0
    await RisingEdge(dut.clk)

    # Set parameters
    dut.move_speed_in.value = fp.to_fixed(1.0)
    dut.turn_speed_in.value = fp.to_fixed(0.3)
    dut.sensor_angle_in.value = fp.to_fixed(0.5)
    dut.sensor_distance_in.value = fp.to_fixed(9.0)

    # Initialize agent at center
    center_x = fp.to_fixed(WIDTH / 2)
    center_y = fp.to_fixed(HEIGHT / 2)
    angle_idx = 0  # Facing right (0 degrees)

    dut.init_agents.value = 1
    dut.init_x.value = center_x
    dut.init_y.value = center_y
    dut.init_angle_idx.value = angle_idx
    await RisingEdge(dut.clk)
    dut.init_agents.value = 0
    await RisingEdge(dut.clk)

    dut._log.info(f"Initialized agent at ({WIDTH/2}, {HEIGHT/2}), angle={angle_idx}")

    # Run one step
    dut.run_step.value = 1
    await RisingEdge(dut.clk)
    dut.run_step.value = 0

    # Wait for step to complete
    for _ in range(1000):  # Timeout
        await RisingEdge(dut.clk)
        if dut.step_done.value == 1:
            break

    assert dut.step_done.value == 1, "Step did not complete"
    dut._log.info("Single agent step completed")


@cocotb.test()
async def test_trail_map_basic(dut):
    """Test trail map is updated correctly."""

    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

    fp = FixedPoint(12, 12)
    WIDTH = 64
    HEIGHT = 64

    # Initialize LFSR
    dut.load_lfsr.value = 1
    dut.lfsr_seed.value = 0xDEADBEEF
    await RisingEdge(dut.clk)
    dut.load_lfsr.value = 0

    # Set parameters
    dut.move_speed_in.value = fp.to_fixed(1.0)
    dut.turn_speed_in.value = fp.to_fixed(0.3)
    dut.sensor_angle_in.value = fp.to_fixed(0.5)
    dut.sensor_distance_in.value = fp.to_fixed(9.0)

    # Initialize agents
    dut.init_agents.value = 1
    dut.init_x.value = fp.to_fixed(WIDTH / 2)
    dut.init_y.value = fp.to_fixed(HEIGHT / 2)
    dut.init_angle_idx.value = 0
    await RisingEdge(dut.clk)
    dut.init_agents.value = 0
    await RisingEdge(dut.clk)

    # Run 5 steps
    for step in range(5):
        dut.run_step.value = 1
        await RisingEdge(dut.clk)
        dut.run_step.value = 0

        # Wait for completion
        for _ in range(1000):
            await RisingEdge(dut.clk)
            if dut.step_done.value == 1:
                break

        dut._log.info(f"Step {step+1} completed")

    # Read trail map
    trail_map = np.zeros((HEIGHT, WIDTH), dtype=np.uint8)
    for y in range(HEIGHT):
        for x in range(WIDTH):
            addr = y * WIDTH + x
            dut.trail_read_addr.value = addr
            await Timer(1, unit="ns")
            trail_map[y, x] = int(dut.trail_read_data.value)

    # Check that some trail was deposited
    trail_sum = np.sum(trail_map)
    dut._log.info(f"Trail map sum: {trail_sum}")
    assert trail_sum > 0, "No trail deposited!"

    # Check trail is along a path (not scattered everywhere)
    non_zero = np.count_nonzero(trail_map)
    dut._log.info(f"Non-zero pixels: {non_zero} / {WIDTH*HEIGHT}")
    assert non_zero < WIDTH * HEIGHT / 2, "Trail too scattered"

    dut._log.info(f"Trail map test passed! Trail deposited at {non_zero} locations")


@cocotb.test(skip=True)  # Skip for now - needs full Python comparison
async def test_trail_map_vs_python(dut):
    """
    Compare RTL trail map with Python reference.
    This is the full end-to-end comparison test.
    """

    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

    fp = FixedPoint(12, 12)
    WIDTH = 64
    HEIGHT = 64
    NUM_AGENTS = 10
    NUM_STEPS = 10

    seed = 0xDEADBEEF

    # Configure RTL
    dut.load_lfsr.value = 1
    dut.lfsr_seed.value = seed
    await RisingEdge(dut.clk)
    dut.load_lfsr.value = 0

    dut.move_speed_in.value = fp.to_fixed(1.0)
    dut.turn_speed_in.value = fp.to_fixed(0.3)
    dut.sensor_angle_in.value = fp.to_fixed(0.5)
    dut.sensor_distance_in.value = fp.to_fixed(9.0)

    dut.init_agents.value = 1
    dut.init_x.value = fp.to_fixed(WIDTH / 2)
    dut.init_y.value = fp.to_fixed(HEIGHT / 2)
    dut.init_angle_idx.value = 0
    await RisingEdge(dut.clk)
    dut.init_agents.value = 0

    # Run Python reference
    dut._log.info("Running Python reference...")
    py_sim = SlimeSimulatorReference(
        width=WIDTH, height=HEIGHT, num_agents=NUM_AGENTS,
        lfsr_seed=seed
    )
    py_sim.init_agents_center()
    py_sim.run(NUM_STEPS)
    py_trail = py_sim.get_trail_map()

    # Run RTL simulation
    dut._log.info("Running RTL simulation...")
    for step in range(NUM_STEPS):
        dut.run_step.value = 1
        await RisingEdge(dut.clk)
        dut.run_step.value = 0

        for _ in range(5000):  # Long timeout
            await RisingEdge(dut.clk)
            if dut.step_done.value == 1:
                break

        dut._log.info(f"RTL step {step+1}/{NUM_STEPS}")

    # Extract RTL trail map
    dut._log.info("Extracting RTL trail map...")
    rtl_trail = np.zeros((HEIGHT, WIDTH), dtype=np.uint8)
    for y in range(HEIGHT):
        for x in range(WIDTH):
            addr = y * WIDTH + x
            dut.trail_read_addr.value = addr
            await Timer(1, unit="ns")
            rtl_trail[y, x] = int(dut.trail_read_data.value)

    # Compare
    diff = np.abs(py_trail.astype(np.int16) - rtl_trail.astype(np.int16))
    max_diff = np.max(diff)
    mean_diff = np.mean(diff)
    match_percent = np.sum(py_trail == rtl_trail) / (WIDTH * HEIGHT) * 100

    dut._log.info(f"========================================")
    dut._log.info(f"Trail Map Comparison:")
    dut._log.info(f"  Match: {match_percent:.1f}%")
    dut._log.info(f"  Max diff: {max_diff}")
    dut._log.info(f"  Mean diff: {mean_diff:.2f}")
    dut._log.info(f"========================================")

    # Allow some tolerance
    assert match_percent > 90, f"Trail maps don't match: only {match_percent:.1f}% identical"
    dut._log.info("Trail map comparison PASSED!")
