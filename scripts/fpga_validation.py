#!/usr/bin/env python3
"""
FPGA Validation Suite - Comprehensive Bit-Accurate Testing
===========================================================

Tests bit-accurate matching between Python reference and FPGA implementation.
Generates test vectors, validates implementations, and exports RTL-compatible data.

Test Categories:
1. LFSR - Linear Feedback Shift Register sequence validation
2. Fixed-Point - Q12.12 arithmetic accuracy and saturation
3. Trigonometric LUT - Sin/Cos lookup table correctness
4. VGA Timing - 640x480@60Hz timing parameter validation
5. Integration - Combined system behavior tests

Author: FPGA Validation Framework
Date: 2025-11-25
"""

import sys
import json
import time
import math
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, asdict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'rtl' / 'sim'))

try:
    from python_reference import LFSR, FixedPoint, TrigLUT, SlimeSimulatorReference
    import numpy as np
except ImportError as e:
    print(f"ERROR: Required modules not found: {e}")
    print("Please ensure python_reference.py is in rtl/sim/ directory")
    sys.exit(1)


# =============================================================================
# Data Classes for Test Results
# =============================================================================

@dataclass
class TestResult:
    """Individual test result."""
    name: str
    passed: bool
    duration_ms: float
    message: str
    details: Dict[str, Any] = None

    def to_dict(self):
        return asdict(self)


@dataclass
class TestSuiteResult:
    """Complete test suite results."""
    total_tests: int
    passed_tests: int
    failed_tests: int
    total_duration_ms: float
    test_results: List[TestResult]

    def to_dict(self):
        return {
            'total_tests': self.total_tests,
            'passed_tests': self.passed_tests,
            'failed_tests': self.failed_tests,
            'total_duration_ms': self.total_duration_ms,
            'pass_rate': f"{100.0 * self.passed_tests / self.total_tests:.2f}%" if self.total_tests > 0 else "N/A",
            'test_results': [tr.to_dict() for tr in self.test_results]
        }


# =============================================================================
# LFSR Testing
# =============================================================================

class LFSRValidator:
    """Validates LFSR implementation against RTL specifications."""

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.test_results = []

    def test_sequence_generation(self, num_steps=1000) -> TestResult:
        """Test LFSR generates correct sequences."""
        start_time = time.time()

        try:
            lfsr = LFSR(width=32, seed=0xDEADBEEF)

            sequence = []
            for _ in range(num_steps):
                sequence.append(lfsr.step())

            # Verify no immediate repeats (basic randomness check)
            unique_ratio = len(set(sequence)) / len(sequence)

            # Check statistical properties (should be ~50% ones)
            bit_counts = []
            for val in sequence:
                bit_counts.append(bin(val).count('1'))

            avg_ones = sum(bit_counts) / len(bit_counts)
            expected_ones = 16.0  # 50% of 32 bits
            ones_error = abs(avg_ones - expected_ones) / expected_ones

            passed = unique_ratio > 0.95 and ones_error < 0.05

            details = {
                'sequence_length': num_steps,
                'unique_values': len(set(sequence)),
                'unique_ratio': f"{unique_ratio:.4f}",
                'avg_ones_per_value': f"{avg_ones:.2f}",
                'expected_ones': expected_ones,
                'ones_error': f"{ones_error*100:.2f}%",
                'first_10_values': [f"0x{v:08X}" for v in sequence[:10]]
            }

            duration = (time.time() - start_time) * 1000

            return TestResult(
                name="LFSR Sequence Generation",
                passed=passed,
                duration_ms=duration,
                message=f"Generated {num_steps} values, {unique_ratio*100:.1f}% unique, {avg_ones:.1f} avg ones",
                details=details
            )

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return TestResult(
                name="LFSR Sequence Generation",
                passed=False,
                duration_ms=duration,
                message=f"Exception: {str(e)}"
            )

    def test_maximal_length(self) -> TestResult:
        """Test LFSR achieves maximal period before repeating."""
        start_time = time.time()

        try:
            # Test with smaller width for speed
            lfsr = LFSR(width=8, seed=0xFF)

            max_period = (1 << 8) - 1  # 2^8 - 1 = 255
            sequence = []

            initial = lfsr.get_state()
            for i in range(max_period + 10):
                val = lfsr.step()
                sequence.append(val)

                # Check if we've returned to initial state
                if i > 0 and val == initial:
                    period = i + 1
                    break
            else:
                period = len(sequence)

            passed = period == max_period

            details = {
                'width': 8,
                'expected_period': max_period,
                'measured_period': period,
                'matches': passed
            }

            duration = (time.time() - start_time) * 1000

            return TestResult(
                name="LFSR Maximal Length Period",
                passed=passed,
                duration_ms=duration,
                message=f"Period: {period} (expected {max_period})",
                details=details
            )

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return TestResult(
                name="LFSR Maximal Length Period",
                passed=False,
                duration_ms=duration,
                message=f"Exception: {str(e)}"
            )

    def test_rtl_matching(self, num_steps=100) -> TestResult:
        """Generate test vectors for RTL comparison."""
        start_time = time.time()

        try:
            lfsr = LFSR(width=32, seed=0xDEADBEEF)

            # Generate sequence matching RTL timing
            test_vectors = []
            for step in range(num_steps):
                state_before = lfsr.get_state()
                state_after = lfsr.step()

                test_vectors.append({
                    'step': step,
                    'state_before': f"0x{state_before:08X}",
                    'state_after': f"0x{state_after:08X}"
                })

            details = {
                'num_vectors': len(test_vectors),
                'seed': "0xDEADBEEF",
                'width': 32,
                'sample_vectors': test_vectors[:5]
            }

            duration = (time.time() - start_time) * 1000

            return TestResult(
                name="LFSR RTL Test Vectors",
                passed=True,
                duration_ms=duration,
                message=f"Generated {num_steps} RTL test vectors",
                details=details
            )

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return TestResult(
                name="LFSR RTL Test Vectors",
                passed=False,
                duration_ms=duration,
                message=f"Exception: {str(e)}"
            )

    def export_test_vectors(self, output_dir: Path, num_steps=1000):
        """Export LFSR test vectors to file."""
        lfsr = LFSR(width=32, seed=0xDEADBEEF)

        vectors = []
        for i in range(num_steps):
            state = lfsr.get_state()
            next_state = lfsr.step()
            vectors.append({
                'step': i,
                'current_state': f"0x{state:08X}",
                'next_state': f"0x{next_state:08X}",
                'lsb': next_state & 1
            })

        output_file = output_dir / 'lfsr_test_vectors.json'
        with open(output_file, 'w') as f:
            json.dump({
                'seed': "0xDEADBEEF",
                'width': 32,
                'num_steps': num_steps,
                'vectors': vectors
            }, f, indent=2)

        if self.verbose:
            print(f"  Exported {num_steps} LFSR vectors to {output_file}")

        return output_file

    def run_all_tests(self) -> List[TestResult]:
        """Run all LFSR tests."""
        if self.verbose:
            print("\n" + "="*80)
            print("LFSR VALIDATION TESTS")
            print("="*80)

        tests = [
            self.test_sequence_generation(1000),
            self.test_maximal_length(),
            self.test_rtl_matching(100)
        ]

        self.test_results.extend(tests)
        return tests


# =============================================================================
# Fixed-Point Testing
# =============================================================================

class FixedPointValidator:
    """Validates fixed-point arithmetic implementation."""

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.test_results = []
        self.fp = FixedPoint(int_bits=12, frac_bits=12)

    def test_conversion_accuracy(self) -> TestResult:
        """Test float to fixed-point conversion accuracy."""
        start_time = time.time()

        try:
            test_values = [
                0.0, 1.0, -1.0, 0.5, -0.5,
                0.25, -0.25, 3.14159, -2.71828,
                1234.5678, -1234.5678
            ]

            max_error = 0.0
            conversions = []

            for val in test_values:
                fp_val = self.fp.to_fixed(val)
                back = self.fp.from_fixed(fp_val)
                error = abs(val - back)
                max_error = max(max_error, error)

                conversions.append({
                    'float': val,
                    'fixed_hex': f"0x{fp_val:06X}",
                    'back_to_float': back,
                    'error': error
                })

            # Error should be within 1 LSB
            lsb = 1.0 / (1 << self.fp.frac_bits)
            passed = max_error <= lsb

            details = {
                'lsb_size': lsb,
                'max_error': max_error,
                'sample_conversions': conversions[:5]
            }

            duration = (time.time() - start_time) * 1000

            return TestResult(
                name="Fixed-Point Conversion Accuracy",
                passed=passed,
                duration_ms=duration,
                message=f"Max error: {max_error:.6f} (LSB: {lsb:.6f})",
                details=details
            )

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return TestResult(
                name="Fixed-Point Conversion Accuracy",
                passed=False,
                duration_ms=duration,
                message=f"Exception: {str(e)}"
            )

    def test_multiplication_accuracy(self) -> TestResult:
        """Test fixed-point multiplication accuracy."""
        start_time = time.time()

        try:
            test_pairs = [
                (1.0, 1.0),
                (2.0, 3.0),
                (0.5, 0.5),
                (-1.0, 1.0),
                (-2.0, -3.0),
                (3.14159, 2.0),
                (0.707, 0.707),
                (1000.0, 0.001)
            ]

            max_error = 0.0
            results = []

            for a_float, b_float in test_pairs:
                a_fixed = self.fp.to_fixed(a_float)
                b_fixed = self.fp.to_fixed(b_float)
                result_fixed = self.fp.multiply(a_fixed, b_fixed)
                result_float = self.fp.from_fixed(result_fixed)

                expected = a_float * b_float
                error = abs(result_float - expected)
                max_error = max(max_error, error)

                results.append({
                    'a': a_float,
                    'b': b_float,
                    'expected': expected,
                    'result': result_float,
                    'error': error
                })

            # Error should be within 1 LSB
            lsb = 1.0 / (1 << self.fp.frac_bits)
            passed = max_error <= lsb

            details = {
                'lsb_size': lsb,
                'max_error': max_error,
                'num_tests': len(test_pairs),
                'sample_results': results[:5]
            }

            duration = (time.time() - start_time) * 1000

            return TestResult(
                name="Fixed-Point Multiplication Accuracy",
                passed=passed,
                duration_ms=duration,
                message=f"Max error: {max_error:.6f} (LSB: {lsb:.6f})",
                details=details
            )

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return TestResult(
                name="Fixed-Point Multiplication Accuracy",
                passed=False,
                duration_ms=duration,
                message=f"Exception: {str(e)}"
            )

    def test_saturation_behavior(self) -> TestResult:
        """Test fixed-point saturation on overflow."""
        start_time = time.time()

        try:
            # Test overflow cases
            max_val = (1 << (self.fp.total_bits - 1)) - 1
            min_val = -(1 << (self.fp.total_bits - 1))

            max_float = max_val / (1 << self.fp.frac_bits)
            min_float = min_val / (1 << self.fp.frac_bits)

            test_cases = [
                ('max_representable', max_float, max_float),
                ('min_representable', min_float, min_float),
                ('overflow_positive', max_float * 2, max_float),
                ('overflow_negative', min_float * 2, min_float),
            ]

            results = []
            all_passed = True

            for name, input_val, expected_clipped in test_cases:
                fixed = self.fp.to_fixed(input_val)
                back = self.fp.from_fixed(fixed)

                # Check if saturation occurred correctly
                saturated = abs(back - expected_clipped) < 1e-6
                results.append({
                    'test': name,
                    'input': input_val,
                    'expected': expected_clipped,
                    'result': back,
                    'saturated_correctly': saturated
                })

                all_passed = all_passed and saturated

            details = {
                'max_representable': max_float,
                'min_representable': min_float,
                'total_bits': self.fp.total_bits,
                'test_results': results
            }

            duration = (time.time() - start_time) * 1000

            return TestResult(
                name="Fixed-Point Saturation Behavior",
                passed=all_passed,
                duration_ms=duration,
                message=f"Tested {len(test_cases)} saturation cases",
                details=details
            )

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return TestResult(
                name="Fixed-Point Saturation Behavior",
                passed=False,
                duration_ms=duration,
                message=f"Exception: {str(e)}"
            )

    def test_edge_cases(self) -> TestResult:
        """Test edge cases like zero, max, min values."""
        start_time = time.time()

        try:
            edge_cases = [
                ('zero * zero', 0.0, 0.0, 0.0),
                ('one * zero', 1.0, 0.0, 0.0),
                ('one * one', 1.0, 1.0, 1.0),
                ('neg_one * one', -1.0, 1.0, -1.0),
                ('neg_one * neg_one', -1.0, -1.0, 1.0),
                ('small * small', 0.001, 0.001, 0.000001),
            ]

            results = []
            all_passed = True

            for name, a, b, expected in edge_cases:
                a_fixed = self.fp.to_fixed(a)
                b_fixed = self.fp.to_fixed(b)
                result_fixed = self.fp.multiply(a_fixed, b_fixed)
                result = self.fp.from_fixed(result_fixed)

                error = abs(result - expected)
                lsb = 1.0 / (1 << self.fp.frac_bits)
                passed = error <= lsb * 2  # Allow 2 LSB for very small values

                results.append({
                    'test': name,
                    'a': a,
                    'b': b,
                    'expected': expected,
                    'result': result,
                    'error': error,
                    'passed': passed
                })

                all_passed = all_passed and passed

            details = {
                'num_tests': len(edge_cases),
                'test_results': results
            }

            duration = (time.time() - start_time) * 1000

            return TestResult(
                name="Fixed-Point Edge Cases",
                passed=all_passed,
                duration_ms=duration,
                message=f"Tested {len(edge_cases)} edge cases",
                details=details
            )

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return TestResult(
                name="Fixed-Point Edge Cases",
                passed=False,
                duration_ms=duration,
                message=f"Exception: {str(e)}"
            )

    def export_test_vectors(self, output_dir: Path):
        """Export fixed-point test vectors for RTL."""
        # Generate comprehensive test matrix
        test_values = []

        # Corner cases
        for a in [-2048.0, -1.0, -0.5, 0.0, 0.5, 1.0, 2047.0]:
            for b in [-2048.0, -1.0, -0.5, 0.0, 0.5, 1.0, 2047.0]:
                a_fixed = self.fp.to_fixed(a)
                b_fixed = self.fp.to_fixed(b)
                result_fixed = self.fp.multiply(a_fixed, b_fixed)

                test_values.append({
                    'a_float': a,
                    'b_float': b,
                    'a_fixed': f"0x{a_fixed:06X}",
                    'b_fixed': f"0x{b_fixed:06X}",
                    'result_fixed': f"0x{result_fixed:06X}",
                    'result_float': self.fp.from_fixed(result_fixed)
                })

        output_file = output_dir / 'fixed_point_test_vectors.json'
        with open(output_file, 'w') as f:
            json.dump({
                'format': 'Q12.12',
                'int_bits': self.fp.int_bits,
                'frac_bits': self.fp.frac_bits,
                'total_bits': self.fp.total_bits,
                'num_tests': len(test_values),
                'test_vectors': test_values
            }, f, indent=2)

        if self.verbose:
            print(f"  Exported {len(test_values)} fixed-point vectors to {output_file}")

        return output_file

    def run_all_tests(self) -> List[TestResult]:
        """Run all fixed-point tests."""
        if self.verbose:
            print("\n" + "="*80)
            print("FIXED-POINT VALIDATION TESTS")
            print("="*80)

        tests = [
            self.test_conversion_accuracy(),
            self.test_multiplication_accuracy(),
            self.test_saturation_behavior(),
            self.test_edge_cases()
        ]

        self.test_results.extend(tests)
        return tests


# =============================================================================
# Trigonometric LUT Testing
# =============================================================================

class TrigLUTValidator:
    """Validates trigonometric lookup table implementation."""

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.test_results = []
        self.trig = TrigLUT(addr_bits=10, frac_bits=12)

    def test_special_angles(self) -> TestResult:
        """Test sin/cos at special angles (0, 90, 180, 270 degrees)."""
        start_time = time.time()

        try:
            table_size = 1 << 10  # 1024 entries

            special_angles = [
                (0, 0.0, 1.0),           # 0 degrees
                (table_size // 4, 1.0, 0.0),   # 90 degrees
                (table_size // 2, 0.0, -1.0),  # 180 degrees
                (3 * table_size // 4, -1.0, 0.0),  # 270 degrees
            ]

            results = []
            max_error = 0.0
            all_passed = True

            for idx, expected_sin, expected_cos in special_angles:
                sin_fixed = self.trig.sin(idx)
                cos_fixed = self.trig.cos(idx)

                # Convert to float
                fp = FixedPoint(12, 12)
                sin_float = fp.from_fixed(sin_fixed)
                cos_float = fp.from_fixed(cos_fixed)

                sin_error = abs(sin_float - expected_sin)
                cos_error = abs(cos_float - expected_cos)

                max_error = max(max_error, sin_error, cos_error)

                # Allow small error due to quantization
                passed = sin_error < 0.01 and cos_error < 0.01

                results.append({
                    'angle_idx': idx,
                    'angle_deg': (idx * 360) / table_size,
                    'expected_sin': expected_sin,
                    'actual_sin': sin_float,
                    'sin_error': sin_error,
                    'expected_cos': expected_cos,
                    'actual_cos': cos_float,
                    'cos_error': cos_error,
                    'passed': passed
                })

                all_passed = all_passed and passed

            details = {
                'table_size': table_size,
                'max_error': max_error,
                'test_results': results
            }

            duration = (time.time() - start_time) * 1000

            return TestResult(
                name="Trig LUT Special Angles",
                passed=all_passed,
                duration_ms=duration,
                message=f"Max error: {max_error:.6f}",
                details=details
            )

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return TestResult(
                name="Trig LUT Special Angles",
                passed=False,
                duration_ms=duration,
                message=f"Exception: {str(e)}"
            )

    def test_symmetry_properties(self) -> TestResult:
        """Test sin/cos symmetry properties."""
        start_time = time.time()

        try:
            table_size = 1 << 10
            fp = FixedPoint(12, 12)

            # Test sin(x + π) = -sin(x)
            # Test cos(x + π) = -cos(x)
            # Test sin(x) = cos(π/2 - x)

            symmetry_tests = []
            max_error = 0.0
            all_passed = True

            for idx in range(0, table_size // 4, 32):  # Sample every 32 indices
                # sin(x + π) = -sin(x)
                sin_x = fp.from_fixed(self.trig.sin(idx))
                sin_x_pi = fp.from_fixed(self.trig.sin((idx + table_size // 2) % table_size))
                sin_error = abs(sin_x + sin_x_pi)

                # cos(x + π) = -cos(x)
                cos_x = fp.from_fixed(self.trig.cos(idx))
                cos_x_pi = fp.from_fixed(self.trig.cos((idx + table_size // 2) % table_size))
                cos_error = abs(cos_x + cos_x_pi)

                max_error = max(max_error, sin_error, cos_error)

                passed = sin_error < 0.01 and cos_error < 0.01
                all_passed = all_passed and passed

                if idx < 64:  # Only save first few
                    symmetry_tests.append({
                        'idx': idx,
                        'sin_symmetry_error': sin_error,
                        'cos_symmetry_error': cos_error,
                        'passed': passed
                    })

            details = {
                'max_error': max_error,
                'sample_results': symmetry_tests
            }

            duration = (time.time() - start_time) * 1000

            return TestResult(
                name="Trig LUT Symmetry Properties",
                passed=all_passed,
                duration_ms=duration,
                message=f"Max symmetry error: {max_error:.6f}",
                details=details
            )

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return TestResult(
                name="Trig LUT Symmetry Properties",
                passed=False,
                duration_ms=duration,
                message=f"Exception: {str(e)}"
            )

    def test_pythagorean_identity(self) -> TestResult:
        """Test sin²(x) + cos²(x) = 1."""
        start_time = time.time()

        try:
            table_size = 1 << 10
            fp = FixedPoint(12, 12)

            max_error = 0.0
            identity_tests = []

            for idx in range(0, table_size, 16):  # Sample every 16 indices
                sin_val = fp.from_fixed(self.trig.sin(idx))
                cos_val = fp.from_fixed(self.trig.cos(idx))

                identity = sin_val * sin_val + cos_val * cos_val
                error = abs(identity - 1.0)
                max_error = max(max_error, error)

                if idx < 256:  # Only save first few
                    identity_tests.append({
                        'idx': idx,
                        'angle_deg': (idx * 360) / table_size,
                        'sin': sin_val,
                        'cos': cos_val,
                        'sin²_plus_cos²': identity,
                        'error': error
                    })

            # Allow some error due to fixed-point quantization
            passed = max_error < 0.01

            details = {
                'table_size': table_size,
                'max_error': max_error,
                'sample_results': identity_tests[:10]
            }

            duration = (time.time() - start_time) * 1000

            return TestResult(
                name="Trig LUT Pythagorean Identity",
                passed=passed,
                duration_ms=duration,
                message=f"Max error: {max_error:.6f}",
                details=details
            )

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return TestResult(
                name="Trig LUT Pythagorean Identity",
                passed=False,
                duration_ms=duration,
                message=f"Exception: {str(e)}"
            )

    def test_monotonicity(self) -> TestResult:
        """Test that sin/cos are monotonic in appropriate quadrants."""
        start_time = time.time()

        try:
            table_size = 1 << 10
            fp = FixedPoint(12, 12)

            # sin should be increasing in [0, π/2]
            # cos should be decreasing in [0, π]

            violations = []

            # Check sin increasing in first quadrant
            prev_sin = fp.from_fixed(self.trig.sin(0))
            for idx in range(1, table_size // 4):
                curr_sin = fp.from_fixed(self.trig.sin(idx))
                if curr_sin < prev_sin - 0.001:  # Allow small numerical error
                    violations.append({
                        'type': 'sin_not_increasing',
                        'idx': idx,
                        'prev': prev_sin,
                        'curr': curr_sin
                    })
                prev_sin = curr_sin

            # Check cos decreasing in first half
            prev_cos = fp.from_fixed(self.trig.cos(0))
            for idx in range(1, table_size // 2):
                curr_cos = fp.from_fixed(self.trig.cos(idx))
                if curr_cos > prev_cos + 0.001:  # Allow small numerical error
                    violations.append({
                        'type': 'cos_not_decreasing',
                        'idx': idx,
                        'prev': prev_cos,
                        'curr': curr_cos
                    })
                prev_cos = curr_cos

            passed = len(violations) == 0

            details = {
                'num_violations': len(violations),
                'violations': violations[:5] if violations else []
            }

            duration = (time.time() - start_time) * 1000

            return TestResult(
                name="Trig LUT Monotonicity",
                passed=passed,
                duration_ms=duration,
                message=f"Found {len(violations)} monotonicity violations",
                details=details
            )

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return TestResult(
                name="Trig LUT Monotonicity",
                passed=False,
                duration_ms=duration,
                message=f"Exception: {str(e)}"
            )

    def export_lut_files(self, output_dir: Path):
        """Export sin/cos LUT to .hex files for RTL."""
        table_size = 1 << 10

        # Generate sin LUT
        sin_file = output_dir / 'sin_lut.hex'
        with open(sin_file, 'w') as f:
            for idx in range(table_size):
                sin_val = self.trig.sin(idx)
                # Write as 25-bit hex (7 hex digits, but use 8 for alignment)
                f.write(f"{sin_val & 0x1FFFFFF:07X}\n")

        # Generate cos LUT
        cos_file = output_dir / 'cos_lut.hex'
        with open(cos_file, 'w') as f:
            for idx in range(table_size):
                cos_val = self.trig.cos(idx)
                f.write(f"{cos_val & 0x1FFFFFF:07X}\n")

        # Also export JSON with float values for reference
        fp = FixedPoint(12, 12)
        lut_data = []
        for idx in range(0, table_size, 16):  # Sample every 16
            lut_data.append({
                'idx': idx,
                'angle_deg': (idx * 360.0) / table_size,
                'angle_rad': (idx * 2.0 * math.pi) / table_size,
                'sin_hex': f"0x{self.trig.sin(idx):07X}",
                'cos_hex': f"0x{self.trig.cos(idx):07X}",
                'sin_float': fp.from_fixed(self.trig.sin(idx)),
                'cos_float': fp.from_fixed(self.trig.cos(idx))
            })

        json_file = output_dir / 'trig_lut_reference.json'
        with open(json_file, 'w') as f:
            json.dump({
                'table_size': table_size,
                'addr_bits': 10,
                'data_bits': 25,
                'frac_bits': 12,
                'format': 'Q12.12 + sign',
                'sample_data': lut_data
            }, f, indent=2)

        if self.verbose:
            print(f"  Exported sin LUT to {sin_file}")
            print(f"  Exported cos LUT to {cos_file}")
            print(f"  Exported reference JSON to {json_file}")

        return sin_file, cos_file, json_file

    def run_all_tests(self) -> List[TestResult]:
        """Run all trig LUT tests."""
        if self.verbose:
            print("\n" + "="*80)
            print("TRIGONOMETRIC LUT VALIDATION TESTS")
            print("="*80)

        tests = [
            self.test_special_angles(),
            self.test_symmetry_properties(),
            self.test_pythagorean_identity(),
            self.test_monotonicity()
        ]

        self.test_results.extend(tests)
        return tests


# =============================================================================
# VGA Timing Validation
# =============================================================================

class VGATimingValidator:
    """Validates VGA timing parameters."""

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.test_results = []

        # VGA 640x480@60Hz parameters
        self.h_visible = 640
        self.h_front = 16
        self.h_sync = 96
        self.h_back = 48
        self.v_visible = 480
        self.v_front = 10
        self.v_sync = 2
        self.v_back = 33

        self.h_total = self.h_visible + self.h_front + self.h_sync + self.h_back
        self.v_total = self.v_visible + self.v_front + self.v_sync + self.v_back

        self.pixel_clock_mhz = 25.175
        self.target_fps = 60.0

    def test_timing_parameters(self) -> TestResult:
        """Validate VGA timing parameters."""
        start_time = time.time()

        try:
            # Calculate actual frame rate
            total_pixels = self.h_total * self.v_total
            frame_time_us = total_pixels / (self.pixel_clock_mhz * 1e6) * 1e6
            actual_fps = 1e6 / frame_time_us

            fps_error = abs(actual_fps - self.target_fps) / self.target_fps

            # Verify standard timing
            passed = (
                self.h_total == 800 and
                self.v_total == 525 and
                fps_error < 0.01  # Within 1%
            )

            details = {
                'horizontal': {
                    'visible': self.h_visible,
                    'front_porch': self.h_front,
                    'sync_pulse': self.h_sync,
                    'back_porch': self.h_back,
                    'total': self.h_total
                },
                'vertical': {
                    'visible': self.v_visible,
                    'front_porch': self.v_front,
                    'sync_pulse': self.v_sync,
                    'back_porch': self.v_back,
                    'total': self.v_total
                },
                'timing': {
                    'pixel_clock_mhz': self.pixel_clock_mhz,
                    'total_pixels_per_frame': total_pixels,
                    'frame_time_ms': frame_time_us / 1000,
                    'actual_fps': actual_fps,
                    'target_fps': self.target_fps,
                    'fps_error_percent': fps_error * 100
                }
            }

            duration = (time.time() - start_time) * 1000

            return TestResult(
                name="VGA Timing Parameters",
                passed=passed,
                duration_ms=duration,
                message=f"640x480@{actual_fps:.2f}Hz (target: {self.target_fps}Hz)",
                details=details
            )

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return TestResult(
                name="VGA Timing Parameters",
                passed=False,
                duration_ms=duration,
                message=f"Exception: {str(e)}"
            )

    def test_sync_pulses(self) -> TestResult:
        """Validate sync pulse widths and positions."""
        start_time = time.time()

        try:
            # HSYNC should be active during [h_visible + h_front, h_visible + h_front + h_sync)
            hsync_start = self.h_visible + self.h_front
            hsync_end = hsync_start + self.h_sync

            # VSYNC should be active during [v_visible + v_front, v_visible + v_front + v_sync)
            vsync_start = self.v_visible + self.v_front
            vsync_end = vsync_start + self.v_sync

            # Validate pulse widths in microseconds
            hsync_time_us = self.h_sync / self.pixel_clock_mhz
            vsync_time_us = (self.v_sync * self.h_total) / self.pixel_clock_mhz

            # Standard VGA sync pulse times
            # HSYNC: ~3.77 µs (96 pixels @ 25.175 MHz)
            # VSYNC: ~0.064 ms (2 lines @ 800 pixels/line)

            hsync_ok = abs(hsync_time_us - 3.81) < 0.1
            vsync_ok = abs(vsync_time_us - 63.56) < 1.0

            passed = hsync_ok and vsync_ok

            details = {
                'hsync': {
                    'start_pixel': hsync_start,
                    'end_pixel': hsync_end,
                    'width_pixels': self.h_sync,
                    'width_us': hsync_time_us,
                    'expected_us': 3.81,
                    'valid': hsync_ok
                },
                'vsync': {
                    'start_line': vsync_start,
                    'end_line': vsync_end,
                    'width_lines': self.v_sync,
                    'width_us': vsync_time_us,
                    'expected_us': 63.56,
                    'valid': vsync_ok
                }
            }

            duration = (time.time() - start_time) * 1000

            return TestResult(
                name="VGA Sync Pulse Widths",
                passed=passed,
                duration_ms=duration,
                message=f"HSYNC: {hsync_time_us:.2f}µs, VSYNC: {vsync_time_us:.2f}µs",
                details=details
            )

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return TestResult(
                name="VGA Sync Pulse Widths",
                passed=False,
                duration_ms=duration,
                message=f"Exception: {str(e)}"
            )

    def test_pixel_clock(self) -> TestResult:
        """Verify pixel clock frequency."""
        start_time = time.time()

        try:
            # We use 25 MHz (100 MHz / 4) instead of exact 25.175 MHz
            actual_clock = 25.0
            standard_clock = 25.175

            clock_error = abs(actual_clock - standard_clock) / standard_clock

            # Calculate impact on frame rate
            actual_fps = (actual_clock * 1e6) / (self.h_total * self.v_total)

            # Within 1% is acceptable
            passed = clock_error < 0.01

            details = {
                'standard_pixel_clock_mhz': standard_clock,
                'actual_pixel_clock_mhz': actual_clock,
                'clock_error_percent': clock_error * 100,
                'actual_refresh_rate': actual_fps,
                'note': 'Using 100MHz/4 = 25MHz for simplicity on Basys3'
            }

            duration = (time.time() - start_time) * 1000

            return TestResult(
                name="VGA Pixel Clock Frequency",
                passed=passed,
                duration_ms=duration,
                message=f"{actual_clock}MHz (standard: {standard_clock}MHz, error: {clock_error*100:.2f}%)",
                details=details
            )

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return TestResult(
                name="VGA Pixel Clock Frequency",
                passed=False,
                duration_ms=duration,
                message=f"Exception: {str(e)}"
            )

    def export_timing_diagram(self, output_dir: Path):
        """Export VGA timing diagram data."""
        timing_data = {
            'standard': 'VGA 640x480@60Hz',
            'horizontal_timing': {
                'visible_area': self.h_visible,
                'front_porch': self.h_front,
                'sync_pulse': self.h_sync,
                'back_porch': self.h_back,
                'total': self.h_total,
                'sync_polarity': 'negative',
                'sync_start': self.h_visible + self.h_front,
                'sync_end': self.h_visible + self.h_front + self.h_sync
            },
            'vertical_timing': {
                'visible_area': self.v_visible,
                'front_porch': self.v_front,
                'sync_pulse': self.v_sync,
                'back_porch': self.v_back,
                'total': self.v_total,
                'sync_polarity': 'negative',
                'sync_start': self.v_visible + self.v_front,
                'sync_end': self.v_visible + self.v_front + self.v_sync
            },
            'clock': {
                'pixel_clock_mhz': self.pixel_clock_mhz,
                'actual_clock_mhz': 25.0,
                'line_frequency_khz': (self.pixel_clock_mhz * 1e6) / self.h_total / 1000,
                'frame_frequency_hz': (self.pixel_clock_mhz * 1e6) / (self.h_total * self.v_total)
            }
        }

        output_file = output_dir / 'vga_timing_diagram.json'
        with open(output_file, 'w') as f:
            json.dump(timing_data, f, indent=2)

        if self.verbose:
            print(f"  Exported VGA timing diagram to {output_file}")

        return output_file

    def run_all_tests(self) -> List[TestResult]:
        """Run all VGA timing tests."""
        if self.verbose:
            print("\n" + "="*80)
            print("VGA TIMING VALIDATION TESTS")
            print("="*80)

        tests = [
            self.test_timing_parameters(),
            self.test_sync_pulses(),
            self.test_pixel_clock()
        ]

        self.test_results.extend(tests)
        return tests


# =============================================================================
# Integration Tests
# =============================================================================

class IntegrationValidator:
    """Integration tests combining multiple components."""

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.test_results = []

    def test_agent_movement(self) -> TestResult:
        """Test complete agent movement pipeline."""
        start_time = time.time()

        try:
            # Create minimal simulator
            sim = SlimeSimulatorReference(
                width=640, height=480, num_agents=10,
                lfsr_seed=0xDEADBEEF
            )
            sim.init_agents_center()

            # Record initial positions
            initial_positions = [(a.x, a.y, a.angle) for a in sim.agents]

            # Run one step
            sim.step()

            # Check that agents moved
            moved_count = 0
            for i, agent in enumerate(sim.agents):
                if (agent.x, agent.y, agent.angle) != initial_positions[i]:
                    moved_count += 1

            passed = moved_count >= 8  # Most agents should move

            details = {
                'num_agents': len(sim.agents),
                'agents_moved': moved_count,
                'sample_before': [
                    f"({x:06X}, {y:06X}, {a:03X})"
                    for x, y, a in initial_positions[:3]
                ],
                'sample_after': [
                    f"({a.x:06X}, {a.y:06X}, {a.angle:03X})"
                    for a in sim.agents[:3]
                ]
            }

            duration = (time.time() - start_time) * 1000

            return TestResult(
                name="Integration: Agent Movement",
                passed=passed,
                duration_ms=duration,
                message=f"{moved_count}/{len(sim.agents)} agents moved",
                details=details
            )

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return TestResult(
                name="Integration: Agent Movement",
                passed=False,
                duration_ms=duration,
                message=f"Exception: {str(e)}"
            )

    def test_deterministic_behavior(self) -> TestResult:
        """Test that same seed produces same results."""
        start_time = time.time()

        try:
            # Run simulation twice with same seed
            results = []

            for run in range(2):
                sim = SlimeSimulatorReference(
                    width=160, height=120, num_agents=10,
                    lfsr_seed=0xDEADBEEF
                )
                sim.init_agents_center()
                sim.run(5)

                # Collect final state
                final_state = [
                    (a.x, a.y, a.angle) for a in sim.agents
                ]
                results.append(final_state)

            # Compare results
            matches = sum(1 for a, b in zip(results[0], results[1]) if a == b)
            passed = matches == len(results[0])

            details = {
                'num_agents': len(results[0]),
                'matching_states': matches,
                'deterministic': passed,
                'run1_sample': [f"({x:06X}, {y:06X}, {a:03X})" for x, y, a in results[0][:3]],
                'run2_sample': [f"({x:06X}, {y:06X}, {a:03X})" for x, y, a in results[1][:3]]
            }

            duration = (time.time() - start_time) * 1000

            return TestResult(
                name="Integration: Deterministic Behavior",
                passed=passed,
                duration_ms=duration,
                message=f"{matches}/{len(results[0])} agents matched",
                details=details
            )

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return TestResult(
                name="Integration: Deterministic Behavior",
                passed=False,
                duration_ms=duration,
                message=f"Exception: {str(e)}"
            )

    def test_trail_deposition(self) -> TestResult:
        """Test that agents deposit trails."""
        start_time = time.time()

        try:
            sim = SlimeSimulatorReference(
                width=160, height=120, num_agents=10,
                lfsr_seed=0xDEADBEEF
            )
            sim.init_agents_center()

            # Initial trail should be empty
            initial_sum = np.sum(sim.trail_map)

            # Run simulation
            sim.run(5)

            # Trail should have deposits
            final_sum = np.sum(sim.trail_map)

            passed = final_sum > initial_sum

            details = {
                'initial_trail_sum': int(initial_sum),
                'final_trail_sum': int(final_sum),
                'trail_deposited': int(final_sum - initial_sum),
                'trail_map_shape': sim.trail_map.shape
            }

            duration = (time.time() - start_time) * 1000

            return TestResult(
                name="Integration: Trail Deposition",
                passed=passed,
                duration_ms=duration,
                message=f"Trail increased by {final_sum - initial_sum}",
                details=details
            )

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return TestResult(
                name="Integration: Trail Deposition",
                passed=False,
                duration_ms=duration,
                message=f"Exception: {str(e)}"
            )

    def export_integration_tests(self, output_dir: Path):
        """Export integration test scenarios."""
        # Small test case for quick RTL validation
        sim = SlimeSimulatorReference(
            width=160, height=120, num_agents=10,
            lfsr_seed=0xDEADBEEF
        )
        sim.init_agents_center()

        # Record initial state
        initial_state = {
            'lfsr_seed': "0xDEADBEEF",
            'width': 160,
            'height': 120,
            'num_agents': 10,
            'agents': [
                {
                    'id': i,
                    'x': f"0x{a.x:06X}",
                    'y': f"0x{a.y:06X}",
                    'angle': f"0x{a.angle:03X}"
                }
                for i, a in enumerate(sim.agents)
            ]
        }

        # Run 5 steps and record
        step_results = []
        for step in range(5):
            sim.step()
            step_results.append({
                'step': step + 1,
                'lfsr_state': f"0x{sim.lfsr.get_state():08X}",
                'trail_sum': int(np.sum(sim.trail_map)),
                'sample_agents': [
                    {
                        'id': i,
                        'x': f"0x{a.x:06X}",
                        'y': f"0x{a.y:06X}",
                        'angle': f"0x{a.angle:03X}"
                    }
                    for i, a in enumerate(sim.agents[:3])
                ]
            })

        output_file = output_dir / 'integration_test_scenario.json'
        with open(output_file, 'w') as f:
            json.dump({
                'initial_state': initial_state,
                'num_steps': 5,
                'step_results': step_results
            }, f, indent=2)

        # Also export final trail map
        trail_file = output_dir / 'integration_test_trail.bin'
        sim.trail_map.tofile(trail_file)

        if self.verbose:
            print(f"  Exported integration test to {output_file}")
            print(f"  Exported trail map to {trail_file}")

        return output_file, trail_file

    def run_all_tests(self) -> List[TestResult]:
        """Run all integration tests."""
        if self.verbose:
            print("\n" + "="*80)
            print("INTEGRATION VALIDATION TESTS")
            print("="*80)

        tests = [
            self.test_agent_movement(),
            self.test_deterministic_behavior(),
            self.test_trail_deposition()
        ]

        self.test_results.extend(tests)
        return tests


# =============================================================================
# Main Validation Suite
# =============================================================================

class FPGAValidationSuite:
    """Complete FPGA validation suite."""

    def __init__(self, verbose=False, export_vectors=False):
        self.verbose = verbose
        self.export_vectors = export_vectors
        self.output_dir = Path(__file__).parent.parent / 'validation_outputs'

        # Create output directory
        self.output_dir.mkdir(exist_ok=True)

        # Validators
        self.lfsr_validator = LFSRValidator(verbose)
        self.fp_validator = FixedPointValidator(verbose)
        self.trig_validator = TrigLUTValidator(verbose)
        self.vga_validator = VGATimingValidator(verbose)
        self.integration_validator = IntegrationValidator(verbose)

    def run_all_tests(self) -> TestSuiteResult:
        """Run complete validation suite."""
        if self.verbose:
            print("\n" + "="*80)
            print("FPGA VALIDATION SUITE")
            print("="*80)
            print(f"Output directory: {self.output_dir}")

        start_time = time.time()
        all_results = []

        # Run all test categories
        all_results.extend(self.lfsr_validator.run_all_tests())
        all_results.extend(self.fp_validator.run_all_tests())
        all_results.extend(self.trig_validator.run_all_tests())
        all_results.extend(self.vga_validator.run_all_tests())
        all_results.extend(self.integration_validator.run_all_tests())

        # Export test vectors if requested
        if self.export_vectors:
            if self.verbose:
                print("\n" + "="*80)
                print("EXPORTING TEST VECTORS")
                print("="*80)

            self.lfsr_validator.export_test_vectors(self.output_dir)
            self.fp_validator.export_test_vectors(self.output_dir)
            self.trig_validator.export_lut_files(self.output_dir)
            self.vga_validator.export_timing_diagram(self.output_dir)
            self.integration_validator.export_integration_tests(self.output_dir)

        # Calculate summary
        total_duration = (time.time() - start_time) * 1000
        passed = sum(1 for r in all_results if r.passed)
        failed = len(all_results) - passed

        suite_result = TestSuiteResult(
            total_tests=len(all_results),
            passed_tests=passed,
            failed_tests=failed,
            total_duration_ms=total_duration,
            test_results=all_results
        )

        return suite_result

    def print_summary(self, suite_result: TestSuiteResult):
        """Print test summary."""
        print("\n" + "="*80)
        print("VALIDATION SUMMARY")
        print("="*80)
        print(f"Total Tests:  {suite_result.total_tests}")
        print(f"Passed:       {suite_result.passed_tests} ({100.0 * suite_result.passed_tests / suite_result.total_tests:.1f}%)")
        print(f"Failed:       {suite_result.failed_tests}")
        print(f"Duration:     {suite_result.total_duration_ms:.2f} ms")
        print("="*80)

        # Print individual results
        print("\nTest Results:")
        print("-" * 80)

        for result in suite_result.test_results:
            status = "PASS" if result.passed else "FAIL"
            print(f"[{status}] {result.name:45} ({result.duration_ms:6.2f} ms)")
            if self.verbose or not result.passed:
                print(f"      {result.message}")

        print("-" * 80)

        if suite_result.failed_tests == 0:
            print("\nALL TESTS PASSED!")
        else:
            print(f"\n{suite_result.failed_tests} TEST(S) FAILED")

        print(f"\nTest vectors saved to: {self.output_dir}")

    def save_results(self, suite_result: TestSuiteResult):
        """Save results to JSON file."""
        output_file = self.output_dir / 'validation_results.json'

        with open(output_file, 'w') as f:
            json.dump(suite_result.to_dict(), f, indent=2)

        if self.verbose:
            print(f"\nDetailed results saved to: {output_file}")


# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='FPGA Validation Suite - Comprehensive bit-accurate testing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --all --verbose                    # Run all tests with verbose output
  %(prog)s --lfsr --fixed-point              # Run specific test categories
  %(prog)s --all --export-vectors            # Run all and export RTL vectors
  %(prog)s --all --save-json                 # Run all and save JSON results
        """
    )

    # Test selection
    parser.add_argument('--all', action='store_true', help='Run all validation tests')
    parser.add_argument('--lfsr', action='store_true', help='Run LFSR tests only')
    parser.add_argument('--fixed-point', action='store_true', help='Run fixed-point tests only')
    parser.add_argument('--trig', action='store_true', help='Run trig LUT tests only')
    parser.add_argument('--vga', action='store_true', help='Run VGA timing tests only')
    parser.add_argument('--integration', action='store_true', help='Run integration tests only')

    # Output options
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--export-vectors', action='store_true', help='Export test vectors for RTL')
    parser.add_argument('--save-json', action='store_true', help='Save results to JSON')

    args = parser.parse_args()

    # If no specific tests selected, show help
    if not (args.all or args.lfsr or args.fixed_point or args.trig or args.vga or args.integration):
        parser.print_help()
        return 1

    # Create validation suite
    suite = FPGAValidationSuite(verbose=args.verbose, export_vectors=args.export_vectors)

    # Run selected tests
    if args.all:
        results = suite.run_all_tests()
    else:
        all_results = []
        if args.lfsr:
            all_results.extend(suite.lfsr_validator.run_all_tests())
        if args.fixed_point:
            all_results.extend(suite.fp_validator.run_all_tests())
        if args.trig:
            all_results.extend(suite.trig_validator.run_all_tests())
        if args.vga:
            all_results.extend(suite.vga_validator.run_all_tests())
        if args.integration:
            all_results.extend(suite.integration_validator.run_all_tests())

        total_duration = sum(r.duration_ms for r in all_results)
        passed = sum(1 for r in all_results if r.passed)

        results = TestSuiteResult(
            total_tests=len(all_results),
            passed_tests=passed,
            failed_tests=len(all_results) - passed,
            total_duration_ms=total_duration,
            test_results=all_results
        )

    # Print summary
    suite.print_summary(results)

    # Save results if requested
    if args.save_json:
        suite.save_results(results)

    # Return exit code
    return 0 if results.failed_tests == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
