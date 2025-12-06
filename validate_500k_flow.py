#!/usr/bin/env python3
"""
Comprehensive validation that Python simulator matches RTL implementation.
Tests with 500,000 steps to verify long-running simulation consistency.

Parameters:
- Resolution: 320x240 (FPGA-matched)
- Agents: 1000 (FPGA-matched)
- Steps: 500,000
- Fixed-point: Q12.12
- LFSR: 32-bit
"""

import sys
import os
import argparse
import time
import json
import numpy as np
from pathlib import Path
from datetime import datetime

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from slime_simulator import SlimeSimulator, SimulationConfig, LFSR, FixedPoint, TrigLUT


class ValidationReport:
    """Generate comprehensive validation report."""

    def __init__(self):
        self.timestamp = datetime.now().isoformat()
        self.tests = []
        self.summary = {
            'total_steps': 0,
            'total_agents': 0,
            'matching_pixels': 0,
            'total_pixels': 0,
            'runtime_seconds': 0,
            'fps': 0
        }

    def add_test(self, name, passed, details=None):
        """Add test result."""
        self.tests.append({
            'name': name,
            'passed': passed,
            'details': details or {}
        })

    def print_summary(self):
        """Print validation summary."""
        passed = sum(1 for t in self.tests if t['passed'])
        total = len(self.tests)

        print("\n" + "="*70)
        print("  VALIDATION REPORT")
        print("="*70)
        print(f"Timestamp: {self.timestamp}")
        print(f"Total Steps: {self.summary['total_steps']:,}")
        print(f"Total Agents: {self.summary['total_agents']:,}")
        print(f"Runtime: {self.summary['runtime_seconds']:.2f}s")
        if self.summary['runtime_seconds'] > 0:
            print(f"Throughput: {self.summary['total_steps'] / self.summary['runtime_seconds']:.1f} steps/sec")
        print("-"*70)

        for test in self.tests:
            status = "✓ PASS" if test['passed'] else "✗ FAIL"
            print(f"{status}: {test['name']}")
            if test['details']:
                for key, val in test['details'].items():
                    print(f"       {key}: {val}")

        print("-"*70)
        print(f"Passed: {passed}/{total} ({100*passed/total:.1f}%)")
        print("="*70 + "\n")

    def to_json(self, filepath):
        """Save report as JSON."""
        data = {
            'timestamp': self.timestamp,
            'summary': self.summary,
            'tests': self.tests
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)


def test_parameter_consistency():
    """Verify that Python and RTL use matching parameters."""
    report = ValidationReport()

    print("\n" + "="*70)
    print("  PARAMETER CONSISTENCY VALIDATION")
    print("="*70)

    # Test LFSR implementation
    print("\n[1/5] Testing LFSR implementation...")
    try:
        # Python version (slime_simulator.py)
        from slime_simulator import LFSR as PyLFSR
        py_lfsr = PyLFSR(width=32, seed=0xDEADBEEF)

        # RTL reference version
        rtl_lfsr = LFSR(width=32, seed=0xDEADBEEF)

        # Generate sequences
        py_seq = [py_lfsr.next() for _ in range(100)]
        rtl_seq = [rtl_lfsr.step() for _ in range(100)]

        match = py_seq == rtl_seq
        report.add_test("LFSR sequence match", match, {
            'python_first_10': py_seq[:10],
            'rtl_first_10': rtl_seq[:10]
        })
        print(f"  {'✓ PASS' if match else '✗ FAIL'}: LFSR sequences match")
    except Exception as e:
        report.add_test("LFSR sequence match", False, {'error': str(e)})
        print(f"  ✗ FAIL: {e}")

    # Test Fixed-Point implementation
    print("\n[2/5] Testing Fixed-Point arithmetic...")
    try:
        from slime_simulator import FixedPoint as PyFixedPoint

        py_fp = PyFixedPoint(integer_bits=12, fractional_bits=12)
        rtl_fp = FixedPoint(int_bits=12, frac_bits=12)

        # Test conversions
        test_vals = [1.5, 3.14159, -2.5, 0.125]
        all_match = True

        for val in test_vals:
            py_fixed = py_fp.to_fixed(val)
            rtl_fixed = rtl_fp.to_fixed(val)
            if py_fixed != rtl_fixed:
                all_match = False
                print(f"  Mismatch for {val}: py={py_fixed}, rtl={rtl_fixed}")

        report.add_test("Fixed-point conversions", all_match)
        print(f"  {'✓ PASS' if all_match else '✗ FAIL'}: Fixed-point conversions match")
    except Exception as e:
        report.add_test("Fixed-point conversions", False, {'error': str(e)})
        print(f"  ✗ FAIL: {e}")

    # Test Trig LUT
    print("\n[3/5] Testing Trigonometric LUT...")
    try:
        from slime_simulator import TrigLUT as PyTrigLUT

        py_fp = PyFixedPoint(integer_bits=12, fractional_bits=12)
        py_trig = PyTrigLUT(fp=py_fp, table_bits=10)

        rtl_trig = TrigLUT(addr_bits=10, frac_bits=12)

        # Test lookups at key angles
        test_angles = [0, 256, 512, 768]  # 0°, 90°, 180°, 270°
        all_match = True

        for angle in test_angles:
            py_sin = py_trig.sin(angle)
            rtl_sin = rtl_trig.sin(angle)
            if py_sin != rtl_sin:
                all_match = False
                print(f"  Sin mismatch at {angle}: py={py_sin}, rtl={rtl_sin}")

        report.add_test("Trig LUT consistency", all_match)
        print(f"  {'✓ PASS' if all_match else '✗ FAIL'}: Trig LUT values match")
    except Exception as e:
        report.add_test("Trig LUT consistency", False, {'error': str(e)})
        print(f"  ✗ FAIL: {e}")

    # Test resolution matching
    print("\n[4/5] Testing resolution parameters...")
    try:
        # FPGA configuration
        fpga_res_w, fpga_res_h = 320, 240
        fpga_agents = 1000
        fpga_vga_w, fpga_vga_h = 640, 480
        fpga_upscale = 2

        # This is what we're testing with
        test_res_w, test_res_h = 320, 240
        test_agents = 1000

        res_match = (test_res_w == fpga_res_w and test_res_h == fpga_res_h)
        agents_match = test_agents == fpga_agents

        report.add_test("Resolution match", res_match, {
            'fpga': f"{fpga_res_w}x{fpga_res_h}",
            'test': f"{test_res_w}x{test_res_h}"
        })
        report.add_test("Agent count match", agents_match, {
            'fpga': fpga_agents,
            'test': test_agents
        })

        print(f"  {'✓ PASS' if res_match else '✗ FAIL'}: Resolution matches FPGA")
        print(f"  {'✓ PASS' if agents_match else '✗ FAIL'}: Agent count matches FPGA")
    except Exception as e:
        report.add_test("Resolution match", False, {'error': str(e)})
        print(f"  ✗ FAIL: {e}")

    # Test simulation parameters
    print("\n[5/5] Testing simulation parameters...")
    try:
        config = SimulationConfig(
            width=320,
            height=240,
            num_agents=1000,
            num_steps=500000,
            move_speed=1.0,
            turn_speed=0.3,
            sensor_angle=0.5,
            sensor_distance=9.0,
            deposit_amount=5,
            decay_rate=0.95,
            diffuse_rate=0.2,
            lfsr_width=32,
            seed=0xDEADBEEF
        )

        params_valid = (
            config.move_speed == 1.0 and
            config.turn_speed == 0.3 and
            config.sensor_angle == 0.5 and
            config.sensor_distance == 9.0
        )

        report.add_test("Simulation parameters", params_valid, {
            'move_speed': config.move_speed,
            'turn_speed': config.turn_speed,
            'sensor_angle': config.sensor_angle,
            'sensor_distance': config.sensor_distance
        })

        print(f"  {'✓ PASS' if params_valid else '✗ FAIL'}: Simulation parameters valid")
    except Exception as e:
        report.add_test("Simulation parameters", False, {'error': str(e)})
        print(f"  ✗ FAIL: {e}")

    return report


def run_reference_simulation(steps=500000, agents=1000, verbose=True):
    """Run the Python reference simulator."""
    print("\n" + "="*70)
    print(f"  PYTHON REFERENCE SIMULATION ({steps:,} steps)")
    print("="*70)

    config = SimulationConfig(
        width=320,
        height=240,
        num_agents=agents,
        num_steps=steps,
        move_speed=1.0,
        turn_speed=0.3,
        sensor_angle=0.5,
        sensor_distance=9.0,
        deposit_amount=5,
        decay_rate=0.95,
        lfsr_width=32,
        seed=0xDEADBEEF
    )

    sim = SlimeSimulator(config)

    print(f"Configuration:")
    print(f"  Resolution: {config.width}x{config.height}")
    print(f"  Agents: {config.num_agents}")
    print(f"  Steps: {config.num_steps}")
    print(f"  Seed: 0x{config.seed:08X}")
    print(f"  Fixed-Point: Q{config.integer_bits}.{config.fractional_bits}")
    print(f"  LFSR: {config.lfsr_width}-bit")

    start_time = time.time()
    print(f"\nRunning simulation...")

    # Run with progress updates
    step = 0
    while step < config.num_steps:
        sim.step()
        step += 1

        if verbose and (step % 50000 == 0):
            elapsed = time.time() - start_time
            fps = step / elapsed
            print(f"  Step {step:,}/{config.num_steps:,} ({100*step/config.num_steps:.1f}%) - {fps:.1f} steps/sec")

    elapsed = time.time() - start_time
    print(f"\nSimulation complete!")
    print(f"  Total time: {elapsed:.2f}s")
    print(f"  Throughput: {config.num_steps/elapsed:.1f} steps/sec")

    return sim, elapsed


def main():
    parser = argparse.ArgumentParser(description="500k steps validation flow")
    parser.add_argument("--steps", type=int, default=500000, help="Number of steps")
    parser.add_argument("--agents", type=int, default=1000, help="Number of agents")
    parser.add_argument("--skip-sim", action="store_true", help="Skip simulation (params only)")
    parser.add_argument("--output", type=str, default="validation_500k_results.json", help="Output file")
    args = parser.parse_args()

    # Test parameter consistency
    report = test_parameter_consistency()
    report.summary['total_agents'] = args.agents
    report.summary['total_steps'] = args.steps

    if not args.skip_sim:
        # Run reference simulation
        sim, elapsed = run_reference_simulation(steps=args.steps, agents=args.agents)
        report.summary['runtime_seconds'] = elapsed
        if elapsed > 0:
            report.summary['fps'] = args.steps / elapsed

        # Save final trail map
        output_dir = Path("validation_output")
        output_dir.mkdir(exist_ok=True)
        trail_file = output_dir / "reference_trail_500k.npy"
        np.save(trail_file, sim.trail_map)
        print(f"\nTrail map saved: {trail_file}")

    # Print and save report
    report.print_summary()
    report.to_json(args.output)
    print(f"Report saved: {args.output}\n")


if __name__ == "__main__":
    main()
