#!/usr/bin/env python3
"""
Master Validation Runner
=========================

Runs all validation tests and generates a comprehensive report.

This script executes all validation modules:
1. Python Reference Implementation
2. LFSR Tests
3. Fixed-Point Arithmetic
4. Trigonometric LUTs
5. VGA Timing

Usage:
    run_all_validations.py
    run_all_validations.py --quick
    run_all_validations.py --comprehensive --save-json
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
import json


class ValidationRunner:
    """Runs all validation scripts and collects results."""

    def __init__(self, scripts_dir: Path, output_dir: Path, verbose: bool = False):
        self.scripts_dir = scripts_dir
        self.output_dir = output_dir
        self.verbose = verbose
        self.results = []

    def run_script(self, script_name: str, args: list = None) -> dict:
        """Run a validation script and capture results."""
        script_path = self.scripts_dir / script_name

        if not script_path.exists():
            return {
                'script': script_name,
                'status': 'not_found',
                'error': f"Script not found: {script_path}"
            }

        cmd = [sys.executable, str(script_path)]
        if args:
            cmd.extend(args)

        if self.verbose:
            print(f"\nRunning: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            return {
                'script': script_name,
                'status': 'passed' if result.returncode == 0 else 'failed',
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }

        except subprocess.TimeoutExpired:
            return {
                'script': script_name,
                'status': 'timeout',
                'error': 'Script timed out after 5 minutes'
            }
        except Exception as e:
            return {
                'script': script_name,
                'status': 'error',
                'error': str(e)
            }

    def run_all(self, quick: bool = False, comprehensive: bool = False):
        """Run all validation scripts."""

        print("="*70)
        print("  Master Validation Test Suite")
        print("="*70)
        print(f"Mode: {'Quick' if quick else 'Comprehensive' if comprehensive else 'Standard'}")
        print(f"Output: {self.output_dir}")
        print("="*70 + "\n")

        # 1. Python Reference Validation
        print("1/5 Running Python Reference Validation...")
        ref_args = ['--output-dir', str(self.output_dir / 'python_reference')]
        if quick:
            ref_args.extend(['--steps', '1,5,10'])
        else:
            ref_args.extend(['--steps', '1,5,10,20,50,100'])
        if comprehensive:
            ref_args.append('--test-reproducibility')

        self.results.append(self.run_script('validate_python_reference.py', ref_args))

        # 2. LFSR Validation
        print("2/5 Running LFSR Validation...")
        lfsr_args = ['--output-dir', str(self.output_dir / 'lfsr')]
        if quick:
            lfsr_args.extend(['--steps', '100'])
        else:
            lfsr_args.extend(['--steps', '1000'])
        if comprehensive:
            lfsr_args.extend(['--all-widths', '--statistical-tests'])

        self.results.append(self.run_script('validate_lfsr.py', lfsr_args))

        # 3. Fixed-Point Validation
        print("3/5 Running Fixed-Point Validation...")
        fp_args = ['--output-dir', str(self.output_dir / 'fixed_point')]
        if comprehensive:
            fp_args.extend(['--comprehensive', '--generate-table'])

        self.results.append(self.run_script('validate_fixed_point.py', fp_args))

        # 4. Trig LUT Validation
        print("4/5 Running Trigonometric LUT Validation...")
        trig_args = ['--output-dir', str(self.output_dir / 'trig')]
        trig_args.extend(['--generate-rtl', '--export-csv'])
        if comprehensive:
            trig_args.append('--test-all')

        self.results.append(self.run_script('validate_trig.py', trig_args))

        # 5. VGA Timing Validation
        print("5/5 Running VGA Timing Validation...")
        vga_args = ['--output-dir', str(self.output_dir / 'vga')]
        vga_args.extend(['--simulate-frames', '2' if quick else '10'])
        vga_args.append('--generate-diagram')

        self.results.append(self.run_script('validate_vga.py', vga_args))

    def print_summary(self):
        """Print validation summary."""
        print("\n" + "="*70)
        print("  VALIDATION SUMMARY")
        print("="*70)

        passed = sum(1 for r in self.results if r['status'] == 'passed')
        failed = sum(1 for r in self.results if r['status'] == 'failed')
        errors = sum(1 for r in self.results if r['status'] not in ['passed', 'failed'])

        for result in self.results:
            status_map = {
                'passed': '✓ PASS',
                'failed': '✗ FAIL',
                'timeout': '⏱ TIMEOUT',
                'not_found': '? NOT FOUND',
                'error': '! ERROR'
            }
            status = status_map.get(result['status'], '? UNKNOWN')
            print(f"  [{status}] {result['script']}")

            if self.verbose and result['status'] != 'passed':
                if 'error' in result:
                    print(f"         Error: {result['error']}")
                if 'stderr' in result and result['stderr']:
                    print(f"         Stderr: {result['stderr'][:200]}")

        print("="*70)
        print(f"Passed: {passed}/{len(self.results)}")
        print(f"Failed: {failed}/{len(self.results)}")
        if errors > 0:
            print(f"Errors: {errors}/{len(self.results)}")
        print(f"Success Rate: {100 * passed / len(self.results):.1f}%")
        print("="*70 + "\n")

        return passed, failed, errors

    def save_report(self, report_file: Path):
        """Save detailed JSON report."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_scripts': len(self.results),
            'passed': sum(1 for r in self.results if r['status'] == 'passed'),
            'failed': sum(1 for r in self.results if r['status'] == 'failed'),
            'results': self.results
        }

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"Detailed report saved to: {report_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Run all validation tests",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--quick', action='store_true',
                       help='Run quick validation (fewer test cases)')
    parser.add_argument('--comprehensive', action='store_true',
                       help='Run comprehensive validation (all test cases)')
    parser.add_argument('--output-dir', type=str,
                       default='validation_output',
                       help='Output directory for all results')
    parser.add_argument('--save-json', action='store_true',
                       help='Save detailed JSON report')
    parser.add_argument('--verbose', action='store_true',
                       help='Verbose output')

    args = parser.parse_args()

    # Get scripts directory
    scripts_dir = Path(__file__).parent
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create runner
    runner = ValidationRunner(scripts_dir, output_dir, args.verbose)

    # Run all validations
    runner.run_all(quick=args.quick, comprehensive=args.comprehensive)

    # Print summary
    passed, failed, errors = runner.print_summary()

    # Save report
    if args.save_json:
        report_file = output_dir / f"master_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        runner.save_report(report_file)

    # Exit code
    sys.exit(0 if (failed == 0 and errors == 0) else 1)


if __name__ == '__main__':
    main()
