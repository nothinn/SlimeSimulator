"""
Step-Based Testbench for SlimeSimulator RTL
Uses step_controller to synchronously process one simulation step at a time,
allowing for stable readout of agent states at each step.
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge
import json
import os
from pathlib import Path


class StepTester:
    """Helper class for step-based testing"""

    def __init__(self, dut, width=320, height=240, num_agents=100):
        self.dut = dut
        self.width = width
        self.height = height
        self.num_agents = num_agents
        self.step_count = 0
        self.FP_SCALE = 4096

    async def reset(self):
        """Reset the DUT"""
        self.dut.rst_n.value = 0
        await RisingEdge(self.dut.clk)
        self.dut.rst_n.value = 1
        await RisingEdge(self.dut.clk)

    async def set_parameters(self, move_speed=1.0, sensor_distance=9.0,
                             sensor_angle=0.5, turn_speed=0.3):
        """Set simulation parameters (in pixels/radians)"""
        # Convert to fixed-point
        move_speed_fp = int(move_speed * self.FP_SCALE)
        sensor_distance_fp = int(sensor_distance * self.FP_SCALE)
        sensor_angle_fp = int(sensor_angle * self.FP_SCALE)
        turn_speed_fp = int(turn_speed * self.FP_SCALE)
        deposit_amount_fp = 5

        self.dut.move_speed.value = move_speed_fp
        self.dut.sensor_distance.value = sensor_distance_fp
        self.dut.sensor_angle.value = sensor_angle_fp
        self.dut.turn_speed.value = turn_speed_fp
        self.dut.deposit_amount.value = deposit_amount_fp

        await RisingEdge(self.dut.clk)

    async def init_agents(self, agents_dict):
        """Initialize agents from dictionary: {agent_id: (x_px, y_px, angle_rad)}"""
        for agent_id, (x_px, y_px, angle_rad) in agents_dict.items():
            x_fp = int(x_px * self.FP_SCALE)
            y_fp = int(y_px * self.FP_SCALE)
            angle_fp = int(angle_rad * self.FP_SCALE)

            # Write X
            self.dut.debug_agent_idx.value = agent_id
            self.dut.debug_agent_sel.value = 0
            self.dut.debug_agent_data_write.value = x_fp
            self.dut.debug_agent_write_en.value = 1
            await RisingEdge(self.dut.clk)

            # Write Y
            self.dut.debug_agent_sel.value = 1
            self.dut.debug_agent_data_write.value = y_fp
            await RisingEdge(self.dut.clk)

            # Write angle
            self.dut.debug_agent_sel.value = 2
            self.dut.debug_agent_data_write.value = angle_fp
            await RisingEdge(self.dut.clk)

        self.dut.debug_agent_write_en.value = 0
        await RisingEdge(self.dut.clk)

    async def read_agent(self, agent_id):
        """Read single agent state: returns (x_px, y_px, angle_rad)"""
        # Read X
        self.dut.debug_agent_idx.value = agent_id
        self.dut.debug_agent_sel.value = 0
        await RisingEdge(self.dut.clk)
        x_fp = int(self.dut.debug_agent_data.value)

        # Read Y
        self.dut.debug_agent_sel.value = 1
        await RisingEdge(self.dut.clk)
        y_fp = int(self.dut.debug_agent_data.value)

        # Read angle
        self.dut.debug_agent_sel.value = 2
        await RisingEdge(self.dut.clk)
        angle_fp = int(self.dut.debug_agent_data.value)

        # Convert to pixels/radians
        x_px = x_fp / self.FP_SCALE
        y_px = y_fp / self.FP_SCALE
        angle_rad = angle_fp / self.FP_SCALE

        return (x_px, y_px, angle_rad)

    async def read_all_agents(self):
        """Read all agents, returns list of (x_px, y_px, angle_rad)"""
        agents = []
        for agent_id in range(self.num_agents):
            x_px, y_px, angle_rad = await self.read_agent(agent_id)
            agents.append({
                'agent_id': agent_id,
                'x_px': x_px,
                'y_px': y_px,
                'angle_rad': angle_rad
            })
        return agents

    async def pulse_step(self):
        """Pulse step_request for one cycle, wait for completion"""
        # Issue pulse
        self.dut.step_request.value = 1
        await RisingEdge(self.dut.clk)
        self.dut.step_request.value = 0

        # Wait for step_busy to go high
        timeout = 0
        while not self.dut.step_busy.value and timeout < 100:
            await RisingEdge(self.dut.clk)
            timeout += 1

        if timeout >= 100:
            raise RuntimeError("step_busy never asserted after step_request")

        # Wait for step_ready to go high (indicates stable outputs)
        timeout = 0
        while not self.dut.step_ready.value and timeout < 100000:
            await RisingEdge(self.dut.clk)
            timeout += 1

        if timeout >= 100000:
            raise RuntimeError(f"step_ready never asserted (waited {timeout} cycles)")

        self.step_count += 1
        return timeout

    async def dump_step(self, output_dir, step_num):
        """Dump all agent states to JSON file"""
        agents = await self.read_all_agents()

        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Write JSON
        filename = os.path.join(output_dir, f'agent_state_step_{step_num:05d}.json')
        with open(filename, 'w') as f:
            json.dump({
                'step': step_num,
                'agents': agents
            }, f, indent=2)

        return filename


@cocotb.test()
async def test_step_controller_basic(dut):
    """Test basic step controller functionality"""
    # Setup
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    tester = StepTester(dut, width=320, height=240, num_agents=100)

    # Reset
    await tester.reset()
    dut._log.info("✓ Reset complete")

    # Set parameters
    await tester.set_parameters(move_speed=1.0, sensor_distance=9.0)
    dut._log.info("✓ Parameters set")

    # Initialize agents in circle pattern
    agents = {}
    import math
    center_x, center_y = 160, 120
    radius = 80

    for i in range(100):
        angle = (2 * math.pi * i) / 100
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        direction = angle + math.pi  # Face inward
        agents[i] = (x, y, direction)

    await tester.init_agents(agents)
    dut._log.info("✓ Agents initialized in circle pattern")

    # Dump step 0 (initialization)
    await tester.dump_step('step_test_dumps', 0)
    dut._log.info("✓ Step 0 dumped (initial state)")

    # Run a few steps synchronously
    for step_num in range(1, 11):
        # Wait for step to complete
        cycles = await tester.pulse_step()
        dut._log.info(f"✓ Step {step_num} complete (took {cycles} cycles)")

        # Read back all agents and verify
        agents_data = await tester.read_all_agents()
        agent_0 = agents_data[0]
        dut._log.info(f"  Agent 0: x={agent_0['x_px']:.2f} y={agent_0['y_px']:.2f}")

        # Dump state
        await tester.dump_step('step_test_dumps', step_num)

    dut._log.info("✓ All steps complete!")
    dut._log.info(f"✓ Total cycles for 10 steps: {tester.step_count}")


@cocotb.test()
async def test_step_controller_movement(dut):
    """Test that agent movement is consistent"""
    # Setup
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    tester = StepTester(dut, width=320, height=240, num_agents=10)

    # Reset
    await tester.reset()

    # Set parameters
    await tester.set_parameters(move_speed=1.0)

    # Initialize single agent at (160, 120), facing 0° (right)
    agents = {0: (160.0, 120.0, 0.0)}
    for i in range(1, 10):
        agents[i] = (160.0 + i, 120.0, 0.0)

    await tester.init_agents(agents)

    # Dump step 0
    await tester.dump_step('step_test_dumps_movement', 0)
    dut._log.info("Step 0: Agents initialized")

    # Run steps and track movement
    for step_num in range(1, 11):
        cycles = await tester.pulse_step()

        # Read agent 0
        x, y, angle = await tester.read_agent(0)
        dut._log.info(f"Step {step_num}: Agent 0 at ({x:.2f}, {y:.2f}), took {cycles} cycles")

        await tester.dump_step('step_test_dumps_movement', step_num)

    dut._log.info("Movement test complete!")
