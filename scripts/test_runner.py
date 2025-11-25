#!/usr/bin/env python3
"""
Test Runner for Slime Simulator
Runs cocotb tests with result tracking and reporting.
"""

import argparse
import subprocess
import sys
import json
import re
from pathlib import Path
from datetime import datetime
import os


class TestRunner:
    """Handles cocotb test execution and result tracking"""

    # Available tests from Makefile
    TESTS = {
        'lfsr': {
            'target': 'test_lfsr',
            'description': 'LFSR random number generator test',
            'module': 'test_lfsr'
        },
        'fixed_point': {
            'target': 'test_fixed_point',
            'description': 'Fixed-point multiplication test',
            'module': 'test_fixed_point'
        },
        'trig': {
            'target': 'test_trig',
            'description': 'Trigonometry LUT test',
            'module': 'test_trig_lut'
        },
        'vga': {
            'target': 'test_vga',
            'description': 'VGA controller test',
            'module': 'test_vga'
        },
        'trail_map': {
            'target': 'test_trail_map',
            'description': 'Trail map integration test',
            'module': 'test_trail_map'
        },
        'rtl_vs_python_lfsr': {
            'target': 'test_rtl_vs_python_lfsr',
            'description': 'Compare LFSR RTL vs Python reference',
            'module': 'test_rtl_vs_python'
        },
        'rtl_vs_python_fp': {
            'target': 'test_rtl_vs_python_fp',
            'description': 'Compare fixed-point RTL vs Python reference',
            'module': 'test_rtl_vs_python'
        },
        'rtl_vs_python_trig': {
            'target': 'test_rtl_vs_python_trig',
            'description': 'Compare trig LUT RTL vs Python reference',
            'module': 'test_rtl_vs_python'
        }
    }

    TEST_SUITES = {
        'basic': ['lfsr', 'fixed_point', 'trig', 'vga'],
        'comparison': ['rtl_vs_python_lfsr', 'rtl_vs_python_fp', 'rtl_vs_python_trig'],
        'integration': ['trail_map'],
        'all': list(TESTS.keys())
    }

    def __init__(self, sim_dir=None, dry_run=False, verbose=False):
        self.dry_run = dry_run
        self.verbose = verbose

        # Set up paths
        if sim_dir:
            self.sim_dir = Path(sim_dir).resolve()
        else:
            script_dir = Path(__file__).parent
            self.sim_dir = script_dir.parent / 'rtl' / 'sim'

        if not self.sim_dir.exists():
            raise FileNotFoundError(f"Simulation directory not found: {self.sim_dir}")

        self.makefile = self.sim_dir / 'Makefile'
        if not self.makefile.exists():
            raise FileNotFoundError(f"Makefile not found: {self.makefile}")

        # Set up logging
        self.log_dir = self.sim_dir / 'test_logs'
        self.log_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_file = self.log_dir / f"test_run_{timestamp}.log"

        # Results tracking
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'summary': {}
        }

    def log(self, message, level='INFO'):
        """Log message to console and file"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_msg = f"[{timestamp}] [{level}] {message}"
        print(log_msg)

        with open(self.log_file, 'a') as f:
            f.write(log_msg + '\n')

    def check_dependencies(self):
        """Check if required tools are available"""
        dependencies = {
            'make': 'GNU Make',
            'iverilog': 'Icarus Verilog',
        }

        missing = []
        for tool, name in dependencies.items():
            try:
                subprocess.run([tool, '--version'],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             check=False)
                self.log(f"Found: {name}")
            except FileNotFoundError:
                self.log(f"Missing: {name}", 'ERROR')
                missing.append(name)

        # Check for cocotb
        try:
            import cocotb
            self.log(f"Found: cocotb {cocotb.__version__}")
        except ImportError:
            self.log("Missing: cocotb", 'ERROR')
            missing.append('cocotb')

        if missing:
            self.log("Missing dependencies:", 'ERROR')
            for dep in missing:
                self.log(f"  - {dep}", 'ERROR')
            return False

        return True

    def clean_test_artifacts(self):
        """Clean previous test artifacts"""
        self.log("Cleaning test artifacts...")

        if self.dry_run:
            self.log("DRY RUN - Would clean test artifacts")
            return

        try:
            subprocess.run(['make', 'clean_all'],
                         cwd=self.sim_dir,
                         check=False,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
        except Exception as e:
            self.log(f"Warning: Could not clean artifacts: {e}", 'WARN')

    def run_test(self, test_name):
        """Run a single test"""
        if test_name not in self.TESTS:
            raise ValueError(f"Unknown test: {test_name}")

        test_config = self.TESTS[test_name]
        target = test_config['target']

        self.log("=" * 60)
        self.log(f"Running test: {test_name}")
        self.log(f"Description: {test_config['description']}")
        self.log("=" * 60)

        if self.dry_run:
            self.log(f"DRY RUN - Would execute: make {target}")
            return {'name': test_name, 'status': 'skipped', 'dry_run': True}

        # Run test
        cmd = ['make', target]
        self.log(f"Command: {' '.join(cmd)}")

        start_time = datetime.now()

        try:
            process = subprocess.Popen(
                cmd,
                cwd=self.sim_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                env=os.environ.copy()
            )

            output_lines = []
            for line in process.stdout:
                line = line.rstrip()
                output_lines.append(line)

                if self.verbose:
                    print(line)

                with open(self.log_file, 'a') as f:
                    f.write(line + '\n')

            process.wait()
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # Parse results
            result = self._parse_test_output(output_lines, process.returncode)
            result['name'] = test_name
            result['description'] = test_config['description']
            result['duration_seconds'] = duration

            # Log result
            status_emoji = {
                'passed': '✓',
                'failed': '✗',
                'error': '!',
            }.get(result['status'], '?')

            self.log(f"Test {test_name}: {result['status'].upper()} {status_emoji} ({duration:.2f}s)")

            if result['status'] == 'failed' and result.get('failures'):
                for failure in result['failures']:
                    self.log(f"  FAIL: {failure}", 'ERROR')

            return result

        except Exception as e:
            self.log(f"Error running test {test_name}: {e}", 'ERROR')
            return {
                'name': test_name,
                'status': 'error',
                'error': str(e)
            }

    def _parse_test_output(self, output_lines, return_code):
        """Parse cocotb test output"""
        result = {
            'status': 'unknown',
            'tests_run': 0,
            'passed': 0,
            'failed': 0,
            'failures': []
        }

        output_text = '\n'.join(output_lines)

        # Look for cocotb result summary
        # Pattern: "X out of Y tests passed"
        summary_match = re.search(r'(\d+)\s+out of\s+(\d+)\s+tests? passed', output_text)
        if summary_match:
            result['passed'] = int(summary_match.group(1))
            result['tests_run'] = int(summary_match.group(2))
            result['failed'] = result['tests_run'] - result['passed']

        # Look for individual test results
        for line in output_lines:
            # Pattern: test_name failed
            if 'failed' in line.lower() and 'test' in line.lower():
                result['failures'].append(line.strip())

            # Check for errors
            if 'error' in line.lower() and ('cocotb' in line.lower() or 'simulation' in line.lower()):
                result['failures'].append(line.strip())

        # Determine overall status
        if return_code == 0 and result['tests_run'] > 0 and result['failed'] == 0:
            result['status'] = 'passed'
        elif result['tests_run'] > 0 and result['failed'] > 0:
            result['status'] = 'failed'
        elif return_code != 0:
            result['status'] = 'error'
        else:
            # Fallback: check for success indicators
            if any('pass' in line.lower() for line in output_lines):
                result['status'] = 'passed'
            else:
                result['status'] = 'error'

        return result

    def run_tests(self, test_names):
        """Run multiple tests"""
        self.log(f"Running {len(test_names)} test(s)")

        for test_name in test_names:
            result = self.run_test(test_name)
            self.results['tests'][test_name] = result

            # Clean between tests
            if not self.dry_run:
                try:
                    subprocess.run(['make', 'clean'],
                                 cwd=self.sim_dir,
                                 check=False,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
                except:
                    pass

        # Generate summary
        self._generate_summary()

    def _generate_summary(self):
        """Generate test summary"""
        total = len(self.results['tests'])
        passed = sum(1 for t in self.results['tests'].values() if t.get('status') == 'passed')
        failed = sum(1 for t in self.results['tests'].values() if t.get('status') == 'failed')
        errors = sum(1 for t in self.results['tests'].values() if t.get('status') == 'error')

        self.results['summary'] = {
            'total': total,
            'passed': passed,
            'failed': failed,
            'errors': errors,
            'success_rate': (passed / total * 100) if total > 0 else 0
        }

        self.log("=" * 60)
        self.log("TEST SUMMARY")
        self.log("=" * 60)
        self.log(f"Total:   {total}")
        self.log(f"Passed:  {passed}")
        self.log(f"Failed:  {failed}")
        self.log(f"Errors:  {errors}")
        self.log(f"Success: {self.results['summary']['success_rate']:.1f}%")
        self.log("=" * 60)

    def save_results_json(self, output_file=None):
        """Save results to JSON file"""
        if not output_file:
            output_file = self.log_dir / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        self.log(f"Results saved to: {output_file}")
        return output_file


def main():
    parser = argparse.ArgumentParser(
        description='Test Runner for Slime Simulator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available Tests:
  lfsr               - LFSR random number generator
  fixed_point        - Fixed-point multiplication
  trig               - Trigonometry LUT
  vga                - VGA controller
  trail_map          - Trail map integration
  rtl_vs_python_*    - RTL vs Python comparison tests

Test Suites:
  basic              - Basic component tests
  comparison         - RTL vs Python comparison tests
  integration        - Integration tests
  all                - All available tests

Examples:
  %(prog)s lfsr                    # Run single test
  %(prog)s lfsr trig vga           # Run multiple tests
  %(prog)s --suite basic           # Run test suite
  %(prog)s --suite all --save-json # Run all tests and save JSON
  %(prog)s --list                  # List available tests
        """
    )

    parser.add_argument('tests',
                       nargs='*',
                       help='Test names to run')
    parser.add_argument('--suite',
                       choices=['basic', 'comparison', 'integration', 'all'],
                       help='Run a predefined test suite')
    parser.add_argument('--list',
                       action='store_true',
                       help='List available tests and exit')
    parser.add_argument('--sim-dir',
                       help='Path to simulation directory (default: ../rtl/sim)')
    parser.add_argument('--clean',
                       action='store_true',
                       help='Clean artifacts before running tests')
    parser.add_argument('--dry-run',
                       action='store_true',
                       help='Show what would be done without executing')
    parser.add_argument('--verbose', '-v',
                       action='store_true',
                       help='Show all test output')
    parser.add_argument('--save-json',
                       action='store_true',
                       help='Save results to JSON file')
    parser.add_argument('--output',
                       help='Output JSON file path')

    args = parser.parse_args()

    # List tests
    if args.list:
        print("\nAvailable Tests:")
        print("=" * 60)
        for name, config in TestRunner.TESTS.items():
            print(f"  {name:<25} - {config['description']}")

        print("\nTest Suites:")
        print("=" * 60)
        for suite_name, tests in TestRunner.TEST_SUITES.items():
            print(f"  {suite_name:<15} - {len(tests)} tests")

        return 0

    # Determine which tests to run
    if args.suite:
        test_names = TestRunner.TEST_SUITES[args.suite]
    elif args.tests:
        test_names = args.tests
        # Validate test names
        for name in test_names:
            if name not in TestRunner.TESTS:
                print(f"ERROR: Unknown test: {name}", file=sys.stderr)
                print(f"Use --list to see available tests", file=sys.stderr)
                return 1
    else:
        print("ERROR: No tests specified. Use --suite or provide test names.", file=sys.stderr)
        print("Use --list to see available tests.", file=sys.stderr)
        return 1

    try:
        # Create runner
        runner = TestRunner(
            sim_dir=args.sim_dir,
            dry_run=args.dry_run,
            verbose=args.verbose
        )

        # Check dependencies
        if not args.dry_run and not runner.check_dependencies():
            print("ERROR: Missing required dependencies", file=sys.stderr)
            return 1

        # Clean if requested
        if args.clean:
            runner.clean_test_artifacts()

        # Run tests
        runner.run_tests(test_names)

        # Save results
        if args.save_json or args.output:
            runner.save_results_json(args.output)

        # Return exit code based on results
        if runner.results['summary']['failed'] > 0 or runner.results['summary']['errors'] > 0:
            return 1

        return 0

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
