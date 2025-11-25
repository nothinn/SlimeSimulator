#!/usr/bin/env python3
"""
Python Reference Implementation Validator
==========================================

This script runs the Python reference implementation (slime_simulator.py)
and generates bit-accurate reference outputs at various step counts.

Outputs:
- LFSR states at each step
- Fixed-point arithmetic results
- Trail maps in binary and JSON format
- Complete simulation state dumps

Usage:
    validate_python_reference.py --steps 1,5,10,20,50,100 --seed 0xDEADBEEF
    validate_python_reference.py --steps 10 --save-json --verbose
"""

import sys
import os
import json
import argparse
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add parent directory to path to import slime_simulator
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from slime_simulator import LFSR, FixedPoint, TrigLUT, SimulationConfig, SlimeSimulator
except ImportError:
    print("ERROR: Could not import slime_simulator.py")
    print("Please ensure slime_simulator.py is in the project root directory")
    sys.exit(1)


class ValidationResults:
    """Container for validation test results."""

    def __init__(self):
        self.test_name = "Python Reference Validation"
        self.timestamp = datetime.now().isoformat()
        self.tests = []
        self.passed = 0
        self.failed = 0
        self.warnings = []

    def add_test(self, name: str, passed: bool, details: Dict[str, Any]):
        """Add a test result."""
        self.tests.append({
            'name': name,
            'passed': passed,
            'details': details
        })
        if passed:
            self.passed += 1
        else:
            self.failed += 1

    def add_warning(self, message: str):
        """Add a warning message."""
        self.warnings.append(message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert results to dictionary."""
        return {
            'test_name': self.test_name,
            'timestamp': self.timestamp,
            'summary': {
                'passed': self.passed,
                'failed': self.failed,
                'total': self.passed + self.failed,
                'success_rate': f"{100 * self.passed / max(1, self.passed + self.failed):.1f}%"
            },
            'warnings': self.warnings,
            'tests': self.tests
        }

    def print_summary(self):
        """Print human-readable summary."""
        print("\n" + "="*70)
        print(f"  {self.test_name}")
        print("="*70)
        print(f"Timestamp: {self.timestamp}")
        print(f"\nResults: {self.passed} passed, {self.failed} failed")
        print(f"Success Rate: {100 * self.passed / max(1, self.passed + self.failed):.1f}%")

        if self.warnings:
            print(f"\nWarnings ({len(self.warnings)}):")
            for warn in self.warnings:
                print(f"  - {warn}")

        print("\nTest Details:")
        for test in self.tests:
            status = "PASS" if test['passed'] else "FAIL"
            print(f"  [{status}] {test['name']}")
            if not test['passed'] or args.verbose:
                for key, val in test['details'].items():
                    print(f"        {key}: {val}")
        print("="*70 + "\n")


def validate_lfsr_initialization(config: SimulationConfig, results: ValidationResults):
    """Validate LFSR can be initialized with given seed."""
    try:
        lfsr = LFSR(config.lfsr_width, config.seed)
        initial_state = lfsr.get_state()

        # Check seed was applied correctly
        expected_seed = config.seed & ((1 << config.lfsr_width) - 1)
        if expected_seed == 0:
            expected_seed = 1  # LFSR can't be 0

        passed = (initial_state == expected_seed)

        results.add_test(
            "LFSR Initialization",
            passed,
            {
                'seed': f"0x{config.seed:08X}",
                'width': config.lfsr_width,
                'initial_state': f"0x{initial_state:08X}",
                'expected': f"0x{expected_seed:08X}"
            }
        )
    except Exception as e:
        results.add_test(
            "LFSR Initialization",
            False,
            {'error': str(e)}
        )


def validate_fixed_point_system(config: SimulationConfig, results: ValidationResults):
    """Validate fixed-point system configuration."""
    try:
        fp = FixedPoint(config.integer_bits, config.fractional_bits)

        # Test basic conversions
        test_values = [0.0, 1.0, -1.0, 0.5, 100.5, -100.5, 0.001]
        errors = []
        max_error = 0.0

        for val in test_values:
            fixed = fp.to_fixed(val)
            recovered = fp.from_fixed(fixed)
            error = abs(val - recovered)
            max_error = max(max_error, error)

            # Error should be within 1 LSB
            lsb = 1.0 / fp.scale
            if error > lsb:
                errors.append(f"Value {val}: error {error:.6f} > LSB {lsb:.6f}")

        passed = len(errors) == 0

        results.add_test(
            "Fixed-Point Conversions",
            passed,
            {
                'format': f"Q{config.integer_bits}.{config.fractional_bits}",
                'scale': fp.scale,
                'max_error': f"{max_error:.9f}",
                'lsb': f"{1.0/fp.scale:.9f}",
                'errors': errors if errors else 'None'
            }
        )
    except Exception as e:
        results.add_test(
            "Fixed-Point Conversions",
            False,
            {'error': str(e)}
        )


def generate_reference_output(config: SimulationConfig, num_steps: int,
                              output_dir: Path, verbose: bool = False) -> Dict[str, Any]:
    """Generate reference output for given number of steps."""

    if verbose:
        print(f"\nGenerating reference for {num_steps} steps...")
        print(f"  Width: {config.width}x{config.height}")
        print(f"  Agents: {config.num_agents}")
        print(f"  Seed: 0x{config.seed:08X}")

    # Create simulator
    sim = SlimeSimulator(config)

    # Record initial state
    initial_lfsr = sim.get_lfsr_state()

    # Run simulation
    lfsr_states = []
    for step in range(num_steps):
        sim.step()
        lfsr_states.append(sim.get_lfsr_state())
        if verbose and (step + 1) % max(1, num_steps // 10) == 0:
            print(f"  Step {step + 1}/{num_steps} - LFSR: 0x{sim.get_lfsr_state():08X}")

    # Get final state
    final_lfsr = sim.get_lfsr_state()
    trail_map = sim.trail_map.copy()

    # Create output directory for this run
    run_dir = output_dir / f"steps_{num_steps:04d}"
    run_dir.mkdir(parents=True, exist_ok=True)

    # Save trail map as binary
    trail_bin_file = run_dir / "trail_map.bin"
    trail_map.astype(np.int64).tofile(trail_bin_file)

    # Save trail map as numpy
    trail_npy_file = run_dir / "trail_map.npy"
    np.save(trail_npy_file, trail_map)

    # Save as image
    img_file = run_dir / "trail_map.png"
    sim.save_image(str(img_file))

    # Create state dump
    state_data = {
        'config': {
            'width': config.width,
            'height': config.height,
            'num_agents': config.num_agents,
            'num_steps': num_steps,
            'seed': f"0x{config.seed:08X}",
            'integer_bits': config.integer_bits,
            'fractional_bits': config.fractional_bits,
            'lfsr_width': config.lfsr_width,
            'spawn_pattern': config.spawn_pattern,
        },
        'initial_lfsr_state': f"0x{initial_lfsr:08X}",
        'final_lfsr_state': f"0x{final_lfsr:08X}",
        'lfsr_states': [f"0x{s:08X}" for s in lfsr_states],
        'trail_map_stats': {
            'min': int(trail_map.min()),
            'max': int(trail_map.max()),
            'mean': float(trail_map.mean()),
            'std': float(trail_map.std()),
            'nonzero_pixels': int(np.count_nonzero(trail_map))
        },
        'files': {
            'trail_map_bin': str(trail_bin_file.name),
            'trail_map_npy': str(trail_npy_file.name),
            'trail_map_img': str(img_file.name)
        }
    }

    # Save state as JSON
    state_file = run_dir / "state.json"
    with open(state_file, 'w') as f:
        json.dump(state_data, f, indent=2)

    # Also save LFSR sequence separately
    lfsr_file = run_dir / "lfsr_sequence.txt"
    with open(lfsr_file, 'w') as f:
        f.write(f"# LFSR Sequence for {num_steps} steps\n")
        f.write(f"# Seed: 0x{config.seed:08X}\n")
        f.write(f"# Width: {config.lfsr_width} bits\n\n")
        f.write(f"Initial: 0x{initial_lfsr:08X}\n")
        for i, state in enumerate(lfsr_states):
            f.write(f"Step {i+1:4d}: 0x{state:08X}\n")

    if verbose:
        print(f"  Saved to: {run_dir}")
        print(f"  Trail map range: [{trail_map.min()}, {trail_map.max()}]")
        print(f"  Non-zero pixels: {np.count_nonzero(trail_map)}")

    return state_data


def validate_reproducibility(config: SimulationConfig, num_steps: int,
                             results: ValidationResults, verbose: bool = False):
    """Validate that simulation produces identical results on repeated runs."""

    if verbose:
        print(f"\nValidating reproducibility for {num_steps} steps...")

    try:
        # Run simulation twice
        sim1 = SlimeSimulator(config)
        for _ in range(num_steps):
            sim1.step()
        trail1 = sim1.trail_map.copy()
        lfsr1 = sim1.get_lfsr_state()

        sim2 = SlimeSimulator(config)
        for _ in range(num_steps):
            sim2.step()
        trail2 = sim2.trail_map.copy()
        lfsr2 = sim2.get_lfsr_state()

        # Compare
        trail_match = np.array_equal(trail1, trail2)
        lfsr_match = (lfsr1 == lfsr2)

        passed = trail_match and lfsr_match

        details = {
            'num_steps': num_steps,
            'trail_maps_match': trail_match,
            'lfsr_states_match': lfsr_match,
            'final_lfsr_run1': f"0x{lfsr1:08X}",
            'final_lfsr_run2': f"0x{lfsr2:08X}"
        }

        if not trail_match:
            diff = np.abs(trail1.astype(np.int64) - trail2.astype(np.int64))
            details['trail_diff_max'] = int(diff.max())
            details['trail_diff_mean'] = float(diff.mean())
            details['trail_diff_pixels'] = int(np.count_nonzero(diff))

        results.add_test(
            f"Reproducibility ({num_steps} steps)",
            passed,
            details
        )

    except Exception as e:
        results.add_test(
            f"Reproducibility ({num_steps} steps)",
            False,
            {'error': str(e)}
        )


def main():
    global args

    parser = argparse.ArgumentParser(
        description="Validate Python reference implementation and generate test data",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--steps', type=str, default='1,5,10,20,50,100',
                       help='Comma-separated list of step counts to test (default: 1,5,10,20,50,100)')
    parser.add_argument('--seed', type=lambda x: int(x, 0), default=0xDEADBEEF,
                       help='LFSR seed in hex or decimal (default: 0xDEADBEEF)')
    parser.add_argument('--width', type=int, default=160,
                       help='Simulation width (default: 160)')
    parser.add_argument('--height', type=int, default=120,
                       help='Simulation height (default: 120)')
    parser.add_argument('--agents', type=int, default=1000,
                       help='Number of agents (default: 1000)')
    parser.add_argument('--spawn', type=str, default='center',
                       choices=['circle', 'random', 'center', 'ring'],
                       help='Agent spawn pattern (default: center)')
    parser.add_argument('--output-dir', type=str,
                       default='validation_output/python_reference',
                       help='Output directory for validation results')
    parser.add_argument('--save-json', action='store_true',
                       help='Save detailed JSON reports')
    parser.add_argument('--verbose', action='store_true',
                       help='Verbose output')
    parser.add_argument('--test-reproducibility', action='store_true',
                       help='Test that runs are reproducible')

    args = parser.parse_args()

    # Parse step counts
    try:
        step_counts = [int(s.strip()) for s in args.steps.split(',')]
    except ValueError:
        print(f"ERROR: Invalid step counts: {args.steps}")
        sys.exit(1)

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create validation results
    results = ValidationResults()

    print("="*70)
    print("  Python Reference Implementation Validator")
    print("="*70)
    print(f"Seed: 0x{args.seed:08X}")
    print(f"Resolution: {args.width}x{args.height}")
    print(f"Agents: {args.agents}")
    print(f"Spawn: {args.spawn}")
    print(f"Steps: {step_counts}")
    print(f"Output: {output_dir}")
    print("="*70 + "\n")

    # Create configuration
    config = SimulationConfig(
        width=args.width,
        height=args.height,
        num_agents=args.agents,
        seed=args.seed,
        spawn_pattern=args.spawn,
        num_steps=0,  # We'll run manually
        save_every=999999,  # Don't auto-save
        output_dir=str(output_dir)
    )

    # Run validation tests
    print("Running validation tests...")

    validate_lfsr_initialization(config, results)
    validate_fixed_point_system(config, results)

    # Test reproducibility if requested
    if args.test_reproducibility:
        for steps in step_counts[:3]:  # Test first few only
            validate_reproducibility(config, steps, results, args.verbose)

    # Generate reference outputs for each step count
    print("\nGenerating reference outputs...")
    reference_data = {}

    for steps in step_counts:
        try:
            state_data = generate_reference_output(config, steps, output_dir, args.verbose)
            reference_data[f"steps_{steps}"] = state_data

            results.add_test(
                f"Generate Reference ({steps} steps)",
                True,
                {
                    'steps': steps,
                    'final_lfsr': state_data['final_lfsr_state'],
                    'trail_nonzero': state_data['trail_map_stats']['nonzero_pixels']
                }
            )
        except Exception as e:
            results.add_test(
                f"Generate Reference ({steps} steps)",
                False,
                {'error': str(e)}
            )

    # Save master index
    index_data = {
        'timestamp': datetime.now().isoformat(),
        'configuration': {
            'seed': f"0x{args.seed:08X}",
            'width': args.width,
            'height': args.height,
            'num_agents': args.agents,
            'spawn_pattern': args.spawn,
        },
        'step_counts': step_counts,
        'reference_outputs': reference_data
    }

    index_file = output_dir / "index.json"
    with open(index_file, 'w') as f:
        json.dump(index_data, f, indent=2)

    print(f"\nMaster index saved to: {index_file}")

    # Print results
    results.print_summary()

    # Save JSON report if requested
    if args.save_json:
        report_file = output_dir / f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(results.to_dict(), f, indent=2)
        print(f"JSON report saved to: {report_file}")

    # Exit with appropriate code
    sys.exit(0 if results.failed == 0 else 1)


if __name__ == '__main__':
    main()
