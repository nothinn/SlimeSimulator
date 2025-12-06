#!/usr/bin/env python3
"""
Trace trig lookup latency through agent_processor movement calculation.

This testbench:
1. Initializes an agent at (256, 120) with angle=0 (pointing right)
2. Runs one complete agent cycle (IDLE → CALC_SENSOR_F_X → ... → DONE_STATE)
3. Dumps every cycle's state including:
   - Current state
   - trig_angle_idx value
   - sin_val, cos_val from trig_lut
   - mult_result (from fixed_point_mult)
   - dx, dy values
   - new_angle

This allows us to see exactly when trig values are stale and when movement calculations are wrong.
"""

import os
import sys
import json
from pathlib import Path

# Add python_reference to path
sys.path.insert(0, str(Path(__file__).parent))

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from cocotb.types import LogicArray

from slime_simulator import FixedPoint, LFSR, TrigLUT, AngleNormalize

# Configuration
AGENT_X_INIT = FixedPoint(256.0)
AGENT_Y_INIT = FixedPoint(120.0)
AGENT_ANGLE_INIT = FixedPoint(0.0)  # Pointing right (cos=1, sin=0)

SENSOR_ANGLE = FixedPoint(0.5)      # ~30 degrees
SENSOR_DISTANCE = FixedPoint(9.0)
MOVE_SPEED = FixedPoint(1.0)
TURN_SPEED = FixedPoint(0.3)
DEPOSIT = FixedPoint(5.0)

# Python reference trig lookup
trig_lut = TrigLUT()


def angle_to_idx(angle_fp):
    """Convert FP angle to trig LUT index (matching RTL function)."""
    angle_int = angle_fp.value
    # Normalize to [0, TWO_PI)
    TWO_PI_FP = int(2.0 * 3.14159265358979 * 4096)
    while angle_int < 0:
        angle_int += TWO_PI_FP
    while angle_int >= TWO_PI_FP:
        angle_int -= TWO_PI_FP
    # Scale to [0, 1024)
    idx = ((angle_int << 10) // 25737) & 0x3FF
    return idx


def rtl_to_fp(val, width=25):
    """Convert RTL unsigned/signed logic value to FixedPoint."""
    if isinstance(val, LogicArray):
        val = int(val)

    # Handle negative numbers (2's complement)
    if val & (1 << (width - 1)):
        val = val - (1 << width)

    return FixedPoint.from_raw(val)


class StateMonitor:
    """Monitor and log state transitions and trig values."""

    def __init__(self):
        self.cycles = []
        self.current_cycle = {}

    def log_cycle(self, cycle_num, dut):
        """Log all relevant signals for this cycle."""
        entry = {
            'cycle': cycle_num,
            'state': int(dut.state),
            'state_name': self._state_name(int(dut.state)),
        }

        # Try to get trig-related signals if they exist
        try:
            entry['trig_angle_idx'] = int(dut.trig_angle_idx)
            entry['sin_val'] = int(dut.sin_val)
            entry['cos_val'] = int(dut.cos_val)
            entry['mult_result'] = int(dut.mult_result)
            entry['mult_a'] = int(dut.mult_a)
            entry['mult_b'] = int(dut.mult_b)
        except:
            pass

        # Registered values
        try:
            entry['dx'] = int(dut.dx)
            entry['dy'] = int(dut.dy)
            entry['new_angle'] = int(dut.new_angle)
            entry['angle_reg'] = int(dut.angle_reg)
        except:
            pass

        self.cycles.append(entry)
        return entry

    def _state_name(self, state_num):
        """Map state number to name."""
        names = {
            0: 'IDLE',
            1: 'CALC_SENSOR_F_X',
            2: 'CALC_SENSOR_F_Y',
            3: 'READ_TRAIL_F',
            4: 'WAIT_TRAIL_F',
            5: 'CALC_SENSOR_L_X',
            6: 'CALC_SENSOR_L_Y',
            7: 'READ_TRAIL_L',
            8: 'WAIT_TRAIL_L',
            9: 'CALC_SENSOR_R_X',
            10: 'CALC_SENSOR_R_Y',
            11: 'READ_TRAIL_R',
            12: 'WAIT_TRAIL_R',
            13: 'SENSORY_DECISION',
            14: 'CALC_MOVE_X',
            15: 'CALC_MOVE_Y',
            16: 'UPDATE_POS',
            17: 'WRITE_TRAIL',
            18: 'DONE_STATE',
        }
        return names.get(state_num, f'UNKNOWN({state_num})')

    def report(self):
        """Generate a detailed report."""
        print("\n" + "="*80)
        print("TRIG LATENCY TRACE REPORT")
        print("="*80)

        for entry in self.cycles:
            print(f"\nCycle {entry['cycle']:3d}: {entry['state_name']:20s} (state={entry['state']})")

            if 'trig_angle_idx' in entry:
                sin_val = rtl_to_fp(entry['sin_val'])
                cos_val = rtl_to_fp(entry['cos_val'])
                mult_result = rtl_to_fp(entry['mult_result'])

                print(f"  trig_angle_idx={entry['trig_angle_idx']:4d}")
                print(f"  sin_val={sin_val:8.4f} ({entry['sin_val']:10d})")
                print(f"  cos_val={cos_val:8.4f} ({entry['cos_val']:10d})")
                print(f"  mult_a={rtl_to_fp(entry['mult_a']):8.4f} mult_b={rtl_to_fp(entry['mult_b']):8.4f}")
                print(f"  mult_result={mult_result:8.4f} ({entry['mult_result']:10d})")

            if 'new_angle' in entry:
                angle_reg = rtl_to_fp(entry['angle_reg'])
                new_angle = rtl_to_fp(entry['new_angle'])
                dx = rtl_to_fp(entry['dx'])
                dy = rtl_to_fp(entry['dy'])
                print(f"  angle_reg={angle_reg:8.4f}")
                print(f"  new_angle={new_angle:8.4f}")
                print(f"  dx={dx:8.4f}, dy={dy:8.4f}")


@cocotb.test()
async def test_trig_latency(dut):
    """Test trig lookup latency in movement calculation."""

    # Start clock
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.rst_n.value = 0
    await Timer(100, "ns")
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    # Setup parameters
    dut.sensor_angle.value = int(SENSOR_ANGLE)
    dut.sensor_distance.value = int(SENSOR_DISTANCE)
    dut.move_speed.value = int(MOVE_SPEED)
    dut.turn_speed.value = int(TURN_SPEED)
    dut.deposit_amount.value = int(DEPOSIT)

    # Mock trail interface
    dut.trail_read_valid.value = 1  # Always valid
    dut.trail_read_data.value = 100  # Dummy trail value

    # Initialize agent via coordinator
    dut.agent_x_in.value = int(AGENT_X_INIT)
    dut.agent_y_in.value = int(AGENT_Y_INIT)
    dut.agent_angle_in.value = int(AGENT_ANGLE_INIT)
    dut.lfsr_bit.value = 0  # Deterministic

    # Create state monitor
    monitor = StateMonitor()

    # Start agent processing
    dut.start.value = 1
    await RisingEdge(dut.clk)
    dut.start.value = 0

    # Run for 30 cycles (enough for full agent processing)
    for cycle in range(30):
        monitor.log_cycle(cycle, dut)
        await RisingEdge(dut.clk)

        # If done, we can stop
        if int(dut.done):
            monitor.log_cycle(cycle + 1, dut)  # Log one more cycle to see IDLE
            break

    # Generate report
    monitor.report()

    # Write JSON trace for analysis
    trace_data = {
        'cycles': monitor.cycles,
        'config': {
            'agent_x_init': float(AGENT_X_INIT),
            'agent_y_init': float(AGENT_Y_INIT),
            'agent_angle_init': float(AGENT_ANGLE_INIT),
        }
    }

    with open('/tmp/trig_latency_trace.json', 'w') as f:
        json.dump(trace_data, f, indent=2)

    cocotb.log.info("Trace saved to /tmp/trig_latency_trace.json")
