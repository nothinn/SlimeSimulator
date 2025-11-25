#!/usr/bin/env python3
"""
LFSR Validation Script
======================

Tests LFSR sequence generation against both Python reference and RTL simulation.

Features:
- Validates 1000+ step sequences match bit-exactly
- Tests statistical properties (should be ~50% uniform)
- Compares Python LFSR with RTL design values
- Tests all supported LFSR widths
- Validates tap positions and feedback
- Exports test results showing pass/fail

Usage:
    validate_lfsr.py --width 32 --seed 0xDEADBEEF --steps 1000
    validate_lfsr.py --all-widths --statistical-tests
    validate_lfsr.py --compare-rtl rtl_lfsr_output.txt
"""

import sys
import os
import argparse
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from slime_simulator import LFSR
except ImportError:
    print("ERROR: Could not import slime_simulator.py")
    sys.exit(1)


class LFSRValidator:
    """LFSR validation and testing."""

    def __init__(self, width: int = 32, seed: int = 0xDEADBEEF):
        self.width = width
        self.seed = seed
        self.lfsr = LFSR(width, seed)
        self.results = {
            'width': width,
            'seed': f"0x{seed:08X}",
            'tests': [],
            'passed': 0,
            'failed': 0
        }

    def add_test(self, name: str, passed: bool, details: Dict[str, Any]):
        """Add a test result."""
        self.results['tests'].append({
            'name': name,
            'passed': passed,
            'details': details
        })
        if passed:
            self.results['passed'] += 1
        else:
            self.results['failed'] += 1

    def test_initialization(self) -> bool:
        """Test LFSR initializes correctly."""
        try:
            lfsr = LFSR(self.width, self.seed)
            initial_state = lfsr.get_state()

            # Expected seed (masked and non-zero)
            expected = self.seed & ((1 << self.width) - 1)
            if expected == 0:
                expected = 1

            passed = (initial_state == expected)

            self.add_test(
                "Initialization",
                passed,
                {
                    'seed': f"0x{self.seed:08X}",
                    'initial_state': f"0x{initial_state:08X}",
                    'expected': f"0x{expected:08X}"
                }
            )
            return passed
        except Exception as e:
            self.add_test("Initialization", False, {'error': str(e)})
            return False

    def test_sequence_length(self, num_steps: int = 1000) -> bool:
        """Test LFSR can generate requested number of steps."""
        try:
            lfsr = LFSR(self.width, self.seed)
            states = []

            for i in range(num_steps):
                state = lfsr.step()
                states.append(state)

            passed = len(states) == num_steps

            self.add_test(
                f"Sequence Generation ({num_steps} steps)",
                passed,
                {
                    'requested': num_steps,
                    'generated': len(states),
                    'first': f"0x{states[0]:08X}" if states else 'N/A',
                    'last': f"0x{states[-1]:08X}" if states else 'N/A'
                }
            )
            return passed
        except Exception as e:
            self.add_test(f"Sequence Generation ({num_steps} steps)", False, {'error': str(e)})
            return False

    def test_determinism(self, num_steps: int = 1000) -> bool:
        """Test LFSR produces identical sequences on repeated runs."""
        try:
            # Run 1
            lfsr1 = LFSR(self.width, self.seed)
            seq1 = [lfsr1.step() for _ in range(num_steps)]

            # Run 2
            lfsr2 = LFSR(self.width, self.seed)
            seq2 = [lfsr2.step() for _ in range(num_steps)]

            # Compare
            matches = sum(1 for a, b in zip(seq1, seq2) if a == b)
            passed = (matches == num_steps)

            self.add_test(
                f"Determinism ({num_steps} steps)",
                passed,
                {
                    'steps': num_steps,
                    'matches': matches,
                    'mismatches': num_steps - matches
                }
            )
            return passed
        except Exception as e:
            self.add_test(f"Determinism ({num_steps} steps)", False, {'error': str(e)})
            return False

    def test_non_zero(self, num_steps: int = 1000) -> bool:
        """Test LFSR never produces zero state."""
        try:
            lfsr = LFSR(self.width, self.seed)
            zero_count = 0

            for _ in range(num_steps):
                state = lfsr.step()
                if state == 0:
                    zero_count += 1

            passed = (zero_count == 0)

            self.add_test(
                f"Non-Zero States ({num_steps} steps)",
                passed,
                {
                    'steps': num_steps,
                    'zero_states': zero_count
                }
            )
            return passed
        except Exception as e:
            self.add_test(f"Non-Zero States ({num_steps} steps)", False, {'error': str(e)})
            return False

    def test_bit_distribution(self, num_steps: int = 10000) -> bool:
        """Test statistical distribution of bits (should be ~50/50)."""
        try:
            lfsr = LFSR(self.width, self.seed)
            bit_counts = [0] * self.width

            for _ in range(num_steps):
                state = lfsr.step()
                for bit in range(self.width):
                    if state & (1 << bit):
                        bit_counts[bit] += 1

            # Check each bit is approximately 50%
            expected_count = num_steps / 2
            tolerance = num_steps * 0.1  # 10% tolerance

            passed = True
            worst_bit = 0
            worst_deviation = 0

            for bit, count in enumerate(bit_counts):
                deviation = abs(count - expected_count)
                if deviation > worst_deviation:
                    worst_deviation = deviation
                    worst_bit = bit
                if deviation > tolerance:
                    passed = False

            self.add_test(
                f"Bit Distribution ({num_steps} steps)",
                passed,
                {
                    'steps': num_steps,
                    'expected_ones_per_bit': int(expected_count),
                    'tolerance': int(tolerance),
                    'worst_bit': worst_bit,
                    'worst_bit_count': bit_counts[worst_bit],
                    'worst_deviation': int(worst_deviation),
                    'worst_deviation_pct': f"{100 * worst_deviation / num_steps:.2f}%"
                }
            )
            return passed
        except Exception as e:
            self.add_test(f"Bit Distribution ({num_steps} steps)", False, {'error': str(e)})
            return False

    def test_periodicity(self, max_steps: int = 100000) -> Tuple[bool, int]:
        """Test LFSR period (maximal length should be 2^width - 1)."""
        try:
            lfsr = LFSR(self.width, self.seed)
            initial_state = lfsr.get_state()

            period = 0
            max_period = (1 << self.width) - 1  # 2^width - 1

            # Step until we return to initial state or hit max_steps
            for i in range(1, min(max_steps, max_period) + 1):
                state = lfsr.step()
                if state == initial_state:
                    period = i
                    break

            # For maximal-length LFSR, period should be 2^width - 1
            expected_period = max_period
            is_maximal = (period == expected_period)

            # If we didn't find period in max_steps, report that
            if period == 0:
                period_str = f">{max_steps}"
                passed = False  # Inconclusive
            else:
                period_str = str(period)
                passed = is_maximal

            self.add_test(
                "Periodicity",
                passed,
                {
                    'width': self.width,
                    'expected_period': expected_period,
                    'measured_period': period_str,
                    'is_maximal_length': is_maximal,
                    'max_steps_tested': max_steps
                }
            )
            return passed, period

        except Exception as e:
            self.add_test("Periodicity", False, {'error': str(e)})
            return False, 0

    def generate_sequence(self, num_steps: int, output_file: str = None) -> List[int]:
        """Generate and optionally save LFSR sequence."""
        lfsr = LFSR(self.width, self.seed)
        sequence = [lfsr.step() for _ in range(num_steps)]

        if output_file:
            with open(output_file, 'w') as f:
                f.write(f"# LFSR Sequence\n")
                f.write(f"# Width: {self.width} bits\n")
                f.write(f"# Seed: 0x{self.seed:08X}\n")
                f.write(f"# Steps: {num_steps}\n\n")
                for i, state in enumerate(sequence):
                    f.write(f"{i+1:6d}: 0x{state:0{(self.width+3)//4}X}\n")

        return sequence

    def compare_with_rtl(self, rtl_file: str) -> bool:
        """Compare Python LFSR output with RTL simulation output."""
        try:
            # Read RTL output
            rtl_states = []
            with open(rtl_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Parse hex value
                        parts = line.split(':')
                        if len(parts) >= 2:
                            hex_val = parts[1].strip()
                            state = int(hex_val, 16)
                            rtl_states.append(state)

            # Generate Python sequence
            lfsr = LFSR(self.width, self.seed)
            py_states = [lfsr.step() for _ in range(len(rtl_states))]

            # Compare
            matches = sum(1 for a, b in zip(py_states, rtl_states) if a == b)
            total = len(rtl_states)
            passed = (matches == total)

            mismatches = []
            if not passed:
                for i, (py, rtl) in enumerate(zip(py_states, rtl_states)):
                    if py != rtl:
                        mismatches.append({
                            'step': i + 1,
                            'python': f"0x{py:08X}",
                            'rtl': f"0x{rtl:08X}"
                        })
                        if len(mismatches) >= 10:  # Limit to first 10
                            break

            self.add_test(
                "RTL Comparison",
                passed,
                {
                    'rtl_file': rtl_file,
                    'steps_compared': total,
                    'matches': matches,
                    'mismatches': total - matches,
                    'first_mismatches': mismatches if mismatches else 'None'
                }
            )
            return passed

        except Exception as e:
            self.add_test("RTL Comparison", False, {'error': str(e)})
            return False


def run_comprehensive_tests(width: int, seed: int, num_steps: int,
                            output_dir: Path, verbose: bool = False) -> Dict[str, Any]:
    """Run comprehensive LFSR validation tests."""

    if verbose:
        print(f"\nValidating {width}-bit LFSR with seed 0x{seed:08X}...")

    validator = LFSRValidator(width, seed)

    # Run tests
    validator.test_initialization()
    validator.test_sequence_length(num_steps)
    validator.test_determinism(min(num_steps, 1000))
    validator.test_non_zero(min(num_steps, 1000))
    validator.test_bit_distribution(min(num_steps, 10000))

    # Periodicity test only for small widths (too slow for large)
    if width <= 24:
        validator.test_periodicity(100000)

    # Generate reference sequence
    seq_file = output_dir / f"lfsr_{width}bit_seed{seed:08X}_{num_steps}steps.txt"
    validator.generate_sequence(num_steps, str(seq_file))

    if verbose:
        print(f"  Tests: {validator.results['passed']} passed, {validator.results['failed']} failed")

    return validator.results


def main():
    parser = argparse.ArgumentParser(
        description="Validate LFSR implementation",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--width', type=int, default=32,
                       choices=[8, 16, 24, 32, 48, 64],
                       help='LFSR width in bits (default: 32)')
    parser.add_argument('--seed', type=lambda x: int(x, 0), default=0xDEADBEEF,
                       help='LFSR seed (default: 0xDEADBEEF)')
    parser.add_argument('--steps', type=int, default=1000,
                       help='Number of steps to test (default: 1000)')
    parser.add_argument('--all-widths', action='store_true',
                       help='Test all supported LFSR widths')
    parser.add_argument('--statistical-tests', action='store_true',
                       help='Run statistical distribution tests (slower)')
    parser.add_argument('--compare-rtl', type=str, metavar='FILE',
                       help='Compare with RTL simulation output file')
    parser.add_argument('--output-dir', type=str,
                       default='validation_output/lfsr',
                       help='Output directory')
    parser.add_argument('--save-json', action='store_true',
                       help='Save detailed JSON report')
    parser.add_argument('--verbose', action='store_true',
                       help='Verbose output')

    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("="*70)
    print("  LFSR Validation")
    print("="*70)

    all_results = []

    if args.all_widths:
        widths = [8, 16, 24, 32, 48, 64]
        print(f"Testing all LFSR widths: {widths}")
        print(f"Steps per width: {args.steps}")
        print("="*70 + "\n")

        for width in widths:
            results = run_comprehensive_tests(width, args.seed, args.steps,
                                              output_dir, args.verbose)
            all_results.append(results)
    else:
        print(f"Width: {args.width} bits")
        print(f"Seed: 0x{args.seed:08X}")
        print(f"Steps: {args.steps}")
        print("="*70 + "\n")

        validator = LFSRValidator(args.width, args.seed)

        # Run tests
        validator.test_initialization()
        validator.test_sequence_length(args.steps)
        validator.test_determinism(min(args.steps, 1000))
        validator.test_non_zero(min(args.steps, 1000))

        if args.statistical_tests:
            validator.test_bit_distribution(min(args.steps, 10000))
            if args.width <= 24:
                validator.test_periodicity(100000)

        # RTL comparison
        if args.compare_rtl:
            validator.compare_with_rtl(args.compare_rtl)

        # Generate reference sequence
        seq_file = output_dir / f"lfsr_{args.width}bit_{args.steps}steps.txt"
        validator.generate_sequence(args.steps, str(seq_file))
        print(f"\nReference sequence saved to: {seq_file}")

        all_results.append(validator.results)

    # Print summary
    print("\n" + "="*70)
    print("  VALIDATION SUMMARY")
    print("="*70)

    total_passed = sum(r['passed'] for r in all_results)
    total_failed = sum(r['failed'] for r in all_results)
    total_tests = total_passed + total_failed

    for result in all_results:
        width = result['width']
        passed = result['passed']
        failed = result['failed']
        status = "PASS" if failed == 0 else "FAIL"
        print(f"[{status}] {width}-bit LFSR: {passed}/{passed+failed} tests passed")

        if args.verbose or failed > 0:
            for test in result['tests']:
                t_status = "PASS" if test['passed'] else "FAIL"
                print(f"      [{t_status}] {test['name']}")
                if not test['passed']:
                    for key, val in test['details'].items():
                        print(f"            {key}: {val}")

    print("="*70)
    print(f"Overall: {total_passed}/{total_tests} tests passed")
    print(f"Success Rate: {100 * total_passed / max(1, total_tests):.1f}%")
    print("="*70 + "\n")

    # Save JSON report
    if args.save_json:
        report = {
            'timestamp': datetime.now().isoformat(),
            'configuration': {
                'steps': args.steps,
                'seed': f"0x{args.seed:08X}",
                'all_widths': args.all_widths,
                'statistical_tests': args.statistical_tests
            },
            'summary': {
                'total_tests': total_tests,
                'passed': total_passed,
                'failed': total_failed,
                'success_rate': f"{100 * total_passed / max(1, total_tests):.1f}%"
            },
            'results': all_results
        }

        report_file = output_dir / f"lfsr_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"JSON report saved to: {report_file}\n")

    # Exit code
    sys.exit(0 if total_failed == 0 else 1)


if __name__ == '__main__':
    main()
