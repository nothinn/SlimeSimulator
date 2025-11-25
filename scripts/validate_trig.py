#!/usr/bin/env python3
"""
Trigonometric Lookup Table Validation Script
=============================================

Validates sin/cos lookup tables against Python reference and RTL ROMs.

Features:
- Generates all 1024 sin/cos table values
- Verifies bit-exact match with RTL lookup tables
- Tests symmetry properties (sin(π-x) = sin(x), etc.)
- Compares Python trig with actual ROM contents
- Validates periodicity and special angles
- Reports any discrepancies

Usage:
    validate_trig.py --addr-bits 10 --frac-bits 12
    validate_trig.py --compare-rtl sin_lut.hex cos_lut.hex
    validate_trig.py --test-symmetry --save-json
"""

import sys
import os
import argparse
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple
import json
import math

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from slime_simulator import TrigLUT, FixedPoint
except ImportError:
    print("ERROR: Could not import slime_simulator.py")
    sys.exit(1)


class TrigValidator:
    """Trigonometric LUT validator."""

    def __init__(self, addr_bits: int = 10, frac_bits: int = 12):
        self.addr_bits = addr_bits
        self.frac_bits = frac_bits
        self.table_size = 1 << addr_bits
        self.fp = FixedPoint(12, frac_bits)
        self.trig = TrigLUT(self.fp, addr_bits)

        self.results = {
            'addr_bits': addr_bits,
            'frac_bits': frac_bits,
            'table_size': self.table_size,
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

    def test_table_generation(self) -> bool:
        """Test that lookup tables are generated correctly."""
        try:
            # Check table sizes
            sin_size = len(self.trig.sin_table)
            cos_size = len(self.trig.cos_table)

            passed = (sin_size == self.table_size) and (cos_size == self.table_size)

            self.add_test(
                "Table Generation",
                passed,
                {
                    'expected_size': self.table_size,
                    'sin_table_size': sin_size,
                    'cos_table_size': cos_size
                }
            )
            return passed

        except Exception as e:
            self.add_test("Table Generation", False, {'error': str(e)})
            return False

    def test_special_angles(self) -> bool:
        """Test special angle values (0, π/2, π, 3π/2)."""
        try:
            # Map angles to table indices
            # Table covers 0 to 2π in table_size steps
            angles = {
                '0': (0, 0.0, 1.0),
                'π/4': (self.table_size // 8, math.sqrt(2)/2, math.sqrt(2)/2),
                'π/2': (self.table_size // 4, 1.0, 0.0),
                'π': (self.table_size // 2, 0.0, -1.0),
                '3π/2': (3 * self.table_size // 4, -1.0, 0.0),
            }

            tolerance = 2.0 / self.fp.scale  # 2 LSB tolerance
            errors = []

            for name, (idx, expected_sin, expected_cos) in angles.items():
                sin_val = self.fp.from_fixed(self.trig.sin_table[idx])
                cos_val = self.fp.from_fixed(self.trig.cos_table[idx])

                sin_error = abs(sin_val - expected_sin)
                cos_error = abs(cos_val - expected_cos)

                if sin_error > tolerance or cos_error > tolerance:
                    errors.append({
                        'angle': name,
                        'index': idx,
                        'sin_expected': expected_sin,
                        'sin_actual': sin_val,
                        'sin_error': sin_error,
                        'cos_expected': expected_cos,
                        'cos_actual': cos_val,
                        'cos_error': cos_error
                    })

            passed = len(errors) == 0

            self.add_test(
                "Special Angles",
                passed,
                {
                    'tolerance_lsb': 2,
                    'errors': errors if errors else 'None'
                }
            )
            return passed

        except Exception as e:
            self.add_test("Special Angles", False, {'error': str(e)})
            return False

    def test_pythagorean_identity(self) -> bool:
        """Test sin²(x) + cos²(x) = 1 for all table entries."""
        try:
            max_error = 0.0
            errors = []
            tolerance = 5.0 / self.fp.scale  # 5 LSB tolerance due to quantization

            for idx in range(self.table_size):
                sin_val = self.fp.from_fixed(self.trig.sin_table[idx])
                cos_val = self.fp.from_fixed(self.trig.cos_table[idx])

                sum_squares = sin_val**2 + cos_val**2
                error = abs(sum_squares - 1.0)
                max_error = max(max_error, error)

                if error > tolerance:
                    if len(errors) < 10:  # Limit to first 10
                        errors.append({
                            'index': idx,
                            'angle_rad': 2 * math.pi * idx / self.table_size,
                            'sin': sin_val,
                            'cos': cos_val,
                            'sin²+cos²': sum_squares,
                            'error': error
                        })

            passed = len(errors) == 0

            self.add_test(
                "Pythagorean Identity",
                passed,
                {
                    'max_error': max_error,
                    'tolerance': tolerance,
                    'errors': errors if errors else 'None'
                }
            )
            return passed

        except Exception as e:
            self.add_test("Pythagorean Identity", False, {'error': str(e)})
            return False

    def test_symmetry_properties(self) -> bool:
        """Test trigonometric symmetry properties."""
        try:
            errors = []
            tolerance = 2.0 / self.fp.scale  # 2 LSB tolerance

            # Test a subset of indices
            test_indices = range(0, self.table_size // 4, max(1, self.table_size // 40))

            for idx in test_indices:
                angle = 2 * math.pi * idx / self.table_size

                # Get values
                sin_idx = self.fp.from_fixed(self.trig.sin_table[idx])
                cos_idx = self.fp.from_fixed(self.trig.cos_table[idx])

                # Test sin(π - x) = sin(x)
                mirror_idx = (self.table_size // 2 - idx) % self.table_size
                sin_mirror = self.fp.from_fixed(self.trig.sin_table[mirror_idx])

                if abs(sin_idx - sin_mirror) > tolerance:
                    errors.append({
                        'property': 'sin(π-x) = sin(x)',
                        'index': idx,
                        'mirror_index': mirror_idx,
                        'sin(x)': sin_idx,
                        'sin(π-x)': sin_mirror,
                        'error': abs(sin_idx - sin_mirror)
                    })

                # Test cos(2π - x) = cos(x)
                neg_idx = (self.table_size - idx) % self.table_size
                cos_neg = self.fp.from_fixed(self.trig.cos_table[neg_idx])

                if abs(cos_idx - cos_neg) > tolerance:
                    errors.append({
                        'property': 'cos(2π-x) = cos(x)',
                        'index': idx,
                        'neg_index': neg_idx,
                        'cos(x)': cos_idx,
                        'cos(2π-x)': cos_neg,
                        'error': abs(cos_idx - cos_neg)
                    })

            passed = len(errors) == 0

            self.add_test(
                "Symmetry Properties",
                passed,
                {
                    'tolerance_lsb': 2,
                    'errors': errors[:10] if errors else 'None'  # Limit to first 10
                }
            )
            return passed

        except Exception as e:
            self.add_test("Symmetry Properties", False, {'error': str(e)})
            return False

    def test_monotonicity(self) -> bool:
        """Test that sin/cos are monotonic in appropriate quadrants."""
        try:
            errors = []

            # Sin should be monotonically increasing in [0, π/2]
            q1_size = self.table_size // 4
            for idx in range(q1_size - 1):
                sin_curr = self.fp.from_fixed(self.trig.sin_table[idx])
                sin_next = self.fp.from_fixed(self.trig.sin_table[idx + 1])

                if sin_next < sin_curr:
                    errors.append({
                        'property': 'sin increasing in [0, π/2]',
                        'index': idx,
                        'sin[i]': sin_curr,
                        'sin[i+1]': sin_next
                    })

            # Cos should be monotonically decreasing in [0, π/2]
            for idx in range(q1_size - 1):
                cos_curr = self.fp.from_fixed(self.trig.cos_table[idx])
                cos_next = self.fp.from_fixed(self.trig.cos_table[idx + 1])

                if cos_next > cos_curr:
                    errors.append({
                        'property': 'cos decreasing in [0, π/2]',
                        'index': idx,
                        'cos[i]': cos_curr,
                        'cos[i+1]': cos_next
                    })

            passed = len(errors) == 0

            self.add_test(
                "Monotonicity",
                passed,
                {
                    'errors': errors[:10] if errors else 'None'
                }
            )
            return passed

        except Exception as e:
            self.add_test("Monotonicity", False, {'error': str(e)})
            return False

    def test_range_bounds(self) -> bool:
        """Test that all sin/cos values are in [-1, 1]."""
        try:
            sin_min = min(self.fp.from_fixed(v) for v in self.trig.sin_table)
            sin_max = max(self.fp.from_fixed(v) for v in self.trig.sin_table)
            cos_min = min(self.fp.from_fixed(v) for v in self.trig.cos_table)
            cos_max = max(self.fp.from_fixed(v) for v in self.trig.cos_table)

            tolerance = 2.0 / self.fp.scale  # Allow small quantization error

            passed = (
                sin_min >= -1.0 - tolerance and sin_max <= 1.0 + tolerance and
                cos_min >= -1.0 - tolerance and cos_max <= 1.0 + tolerance
            )

            self.add_test(
                "Range Bounds",
                passed,
                {
                    'sin_range': f"[{sin_min:.6f}, {sin_max:.6f}]",
                    'cos_range': f"[{cos_min:.6f}, {cos_max:.6f}]",
                    'expected': '[-1.0, 1.0]'
                }
            )
            return passed

        except Exception as e:
            self.add_test("Range Bounds", False, {'error': str(e)})
            return False

    def generate_rtl_hex_files(self, output_dir: Path) -> bool:
        """Generate RTL-compatible .hex files for sin/cos LUTs."""
        try:
            sin_file = output_dir / "sin_lut_ref.hex"
            cos_file = output_dir / "cos_lut_ref.hex"

            # Convert to 25-bit two's complement representation
            total_bits = 25  # Q12.12 + sign

            with open(sin_file, 'w') as f:
                for val in self.trig.sin_table:
                    # Convert to unsigned representation
                    if val < 0:
                        val_unsigned = (1 << total_bits) + val
                    else:
                        val_unsigned = val

                    # Write as hex (7 hex digits for 25 bits, but use 8 for alignment)
                    f.write(f"{val_unsigned:08x}\n")

            with open(cos_file, 'w') as f:
                for val in self.trig.cos_table:
                    if val < 0:
                        val_unsigned = (1 << total_bits) + val
                    else:
                        val_unsigned = val

                    f.write(f"{val_unsigned:08x}\n")

            return True

        except Exception as e:
            print(f"Error generating RTL hex files: {e}")
            return False

    def compare_with_rtl(self, sin_file: str, cos_file: str) -> bool:
        """Compare Python LUT with RTL ROM files."""
        try:
            # Read RTL sin table
            rtl_sin = []
            with open(sin_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        val = int(line, 16)
                        # Convert from unsigned to signed
                        if val >= (1 << 24):  # Sign bit set
                            val = val - (1 << 25)
                        rtl_sin.append(val)

            # Read RTL cos table
            rtl_cos = []
            with open(cos_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        val = int(line, 16)
                        if val >= (1 << 24):
                            val = val - (1 << 25)
                        rtl_cos.append(val)

            # Compare
            sin_matches = 0
            cos_matches = 0
            sin_errors = []
            cos_errors = []

            for idx in range(min(len(rtl_sin), len(self.trig.sin_table))):
                if rtl_sin[idx] == self.trig.sin_table[idx]:
                    sin_matches += 1
                else:
                    if len(sin_errors) < 10:
                        sin_errors.append({
                            'index': idx,
                            'angle': f"{360 * idx / self.table_size:.2f}°",
                            'python': f"0x{self.trig.sin_table[idx] & 0x1FFFFFF:08X}",
                            'rtl': f"0x{rtl_sin[idx] & 0x1FFFFFF:08X}",
                            'python_dec': self.trig.sin_table[idx],
                            'rtl_dec': rtl_sin[idx]
                        })

            for idx in range(min(len(rtl_cos), len(self.trig.cos_table))):
                if rtl_cos[idx] == self.trig.cos_table[idx]:
                    cos_matches += 1
                else:
                    if len(cos_errors) < 10:
                        cos_errors.append({
                            'index': idx,
                            'angle': f"{360 * idx / self.table_size:.2f}°",
                            'python': f"0x{self.trig.cos_table[idx] & 0x1FFFFFF:08X}",
                            'rtl': f"0x{rtl_cos[idx] & 0x1FFFFFF:08X}",
                            'python_dec': self.trig.cos_table[idx],
                            'rtl_dec': rtl_cos[idx]
                        })

            sin_passed = (sin_matches == len(rtl_sin))
            cos_passed = (cos_matches == len(rtl_cos))
            passed = sin_passed and cos_passed

            self.add_test(
                "RTL Comparison",
                passed,
                {
                    'sin_file': sin_file,
                    'cos_file': cos_file,
                    'sin_matches': sin_matches,
                    'sin_total': len(rtl_sin),
                    'sin_errors': sin_errors if sin_errors else 'None',
                    'cos_matches': cos_matches,
                    'cos_total': len(rtl_cos),
                    'cos_errors': cos_errors if cos_errors else 'None'
                }
            )
            return passed

        except Exception as e:
            self.add_test("RTL Comparison", False, {'error': str(e)})
            return False

    def export_table_csv(self, output_file: str):
        """Export lookup table as CSV for inspection."""
        try:
            with open(output_file, 'w') as f:
                f.write("# Trigonometric Lookup Table\n")
                f.write(f"# Addr bits: {self.addr_bits}, Frac bits: {self.frac_bits}\n")
                f.write(f"# Index, Angle(deg), Angle(rad), "
                       f"Sin(fixed), Sin(float), Cos(fixed), Cos(float), "
                       f"Sin(hex), Cos(hex)\n\n")

                for idx in range(self.table_size):
                    angle_rad = 2 * math.pi * idx / self.table_size
                    angle_deg = 360 * idx / self.table_size

                    sin_fixed = self.trig.sin_table[idx]
                    cos_fixed = self.trig.cos_table[idx]

                    sin_float = self.fp.from_fixed(sin_fixed)
                    cos_float = self.fp.from_fixed(cos_fixed)

                    # Convert to unsigned for hex display
                    sin_hex = sin_fixed if sin_fixed >= 0 else (1 << 25) + sin_fixed
                    cos_hex = cos_fixed if cos_fixed >= 0 else (1 << 25) + cos_fixed

                    f.write(f"{idx}, {angle_deg:.2f}, {angle_rad:.6f}, "
                           f"{sin_fixed}, {sin_float:.6f}, "
                           f"{cos_fixed}, {cos_float:.6f}, "
                           f"0x{sin_hex:08X}, 0x{cos_hex:08X}\n")

            return True
        except Exception as e:
            print(f"Error exporting CSV: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Validate trigonometric lookup tables",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--addr-bits', type=int, default=10,
                       help='Address bits (table size = 2^addr_bits) (default: 10)')
    parser.add_argument('--frac-bits', type=int, default=12,
                       help='Fractional bits for fixed-point (default: 12)')
    parser.add_argument('--test-symmetry', action='store_true',
                       help='Test symmetry properties')
    parser.add_argument('--test-all', action='store_true',
                       help='Run all tests including slow ones')
    parser.add_argument('--compare-rtl', nargs=2, metavar=('SIN_FILE', 'COS_FILE'),
                       help='Compare with RTL sin/cos hex files')
    parser.add_argument('--generate-rtl', action='store_true',
                       help='Generate RTL-compatible hex files')
    parser.add_argument('--export-csv', action='store_true',
                       help='Export lookup table as CSV')
    parser.add_argument('--output-dir', type=str,
                       default='validation_output/trig',
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
    print("  Trigonometric LUT Validation")
    print("="*70)
    print(f"Table size: {1 << args.addr_bits} entries ({args.addr_bits}-bit addressing)")
    print(f"Fixed-point: Q12.{args.frac_bits}")
    print("="*70 + "\n")

    # Create validator
    validator = TrigValidator(args.addr_bits, args.frac_bits)

    # Run basic tests
    validator.test_table_generation()
    validator.test_special_angles()
    validator.test_range_bounds()
    validator.test_pythagorean_identity()

    # Optional tests
    if args.test_symmetry or args.test_all:
        print("Testing symmetry properties...")
        validator.test_symmetry_properties()
        validator.test_monotonicity()

    # RTL comparison
    if args.compare_rtl:
        sin_file, cos_file = args.compare_rtl
        print(f"Comparing with RTL files:\n  Sin: {sin_file}\n  Cos: {cos_file}")
        validator.compare_with_rtl(sin_file, cos_file)

    # Generate RTL files
    if args.generate_rtl:
        print("\nGenerating RTL hex files...")
        if validator.generate_rtl_hex_files(output_dir):
            print(f"  Generated: {output_dir}/sin_lut_ref.hex")
            print(f"  Generated: {output_dir}/cos_lut_ref.hex")

    # Export CSV
    if args.export_csv:
        csv_file = output_dir / "trig_lut_table.csv"
        print(f"\nExporting CSV: {csv_file}")
        validator.export_table_csv(str(csv_file))

    # Print results
    print("\n" + "="*70)
    print("  VALIDATION RESULTS")
    print("="*70)

    passed = validator.results['passed']
    failed = validator.results['failed']
    total = passed + failed

    for test in validator.results['tests']:
        status = "PASS" if test['passed'] else "FAIL"
        print(f"[{status}] {test['name']}")
        if args.verbose or not test['passed']:
            for key, val in test['details'].items():
                if isinstance(val, (list, dict)) and len(str(val)) > 150:
                    print(f"      {key}: [see JSON report]")
                else:
                    print(f"      {key}: {val}")

    print("="*70)
    print(f"Total: {passed}/{total} tests passed")
    print(f"Success Rate: {100 * passed / max(1, total):.1f}%")
    print("="*70 + "\n")

    # Save JSON report
    if args.save_json:
        report = {
            'timestamp': datetime.now().isoformat(),
            'configuration': {
                'addr_bits': args.addr_bits,
                'frac_bits': args.frac_bits,
                'table_size': validator.table_size
            },
            'results': validator.results
        }

        report_file = output_dir / f"trig_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"JSON report saved to: {report_file}\n")

    # Exit code
    sys.exit(0 if failed == 0 else 1)


if __name__ == '__main__':
    main()
