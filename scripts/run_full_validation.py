#!/usr/bin/env python3
"""
Full Validation Master Script
Orchestrates the complete validation workflow: tests, build, program, compare.
"""

import argparse
import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime
import time


class FullValidation:
    """Master controller for full validation workflow"""

    def __init__(self, dry_run=False, verbose=False):
        self.dry_run = dry_run
        self.verbose = verbose

        # Set up paths
        self.script_dir = Path(__file__).parent
        self.project_dir = self.script_dir.parent
        self.rtl_dir = self.project_dir / 'rtl'

        # Script paths
        self.scripts = {
            'test_runner': self.script_dir / 'test_runner.py',
            'vivado_build': self.script_dir / 'vivado_build.py',
            'fpga_programmer': self.script_dir / 'fpga_programmer.py',
            'image_capture': self.script_dir / 'image_capture.py'
        }

        # Verify scripts exist
        for name, path in self.scripts.items():
            if not path.exists():
                raise FileNotFoundError(f"Required script not found: {path}")

        # Set up logging
        self.log_dir = self.project_dir / 'validation_logs'
        self.log_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_file = self.log_dir / f"validation_{timestamp}.log"

        # Results tracking
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'steps': {},
            'summary': {}
        }
        self.start_time = None

    def log(self, message, level='INFO'):
        """Log message to console and file"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_msg = f"[{timestamp}] [{level}] {message}"
        print(log_msg)

        with open(self.log_file, 'a') as f:
            f.write(log_msg + '\n')

    def run_script(self, script_name, args):
        """Run one of the automation scripts"""
        script_path = self.scripts[script_name]

        cmd = [sys.executable, str(script_path)] + args

        if self.dry_run and '--dry-run' not in args:
            cmd.append('--dry-run')

        if self.verbose and '--verbose' not in args and '-v' not in args:
            cmd.append('--verbose')

        self.log(f"Running: {' '.join(cmd)}")

        step_start = time.time()

        try:
            result = subprocess.run(
                cmd,
                capture_output=not self.verbose,
                text=True,
                check=False
            )

            step_duration = time.time() - step_start

            # Log output if not verbose (verbose already printed)
            if not self.verbose and result.stdout:
                with open(self.log_file, 'a') as f:
                    f.write(f"\n=== Output from {script_name} ===\n")
                    f.write(result.stdout)
                    f.write("\n")

            if result.returncode != 0:
                self.log(f"Script {script_name} failed with code {result.returncode}", 'ERROR')
                if result.stderr:
                    self.log(f"Error: {result.stderr}", 'ERROR')
                return False, step_duration

            self.log(f"Script {script_name} completed successfully ({step_duration:.1f}s)")
            return True, step_duration

        except Exception as e:
            step_duration = time.time() - step_start
            self.log(f"Error running {script_name}: {e}", 'ERROR')
            return False, step_duration

    def run_tests(self, test_suite='basic'):
        """Run test suite"""
        self.log("=" * 70)
        self.log("STEP: Running Tests")
        self.log("=" * 70)

        args = ['--suite', test_suite, '--save-json']
        success, duration = self.run_script('test_runner', args)

        self.results['steps']['tests'] = {
            'success': success,
            'duration_seconds': duration,
            'suite': test_suite
        }

        return success

    def run_build(self, build_type='main'):
        """Run Vivado build"""
        self.log("=" * 70)
        self.log(f"STEP: Building Design ({build_type})")
        self.log("=" * 70)

        args = [build_type, '--save-json']
        success, duration = self.run_script('vivado_build', args)

        self.results['steps']['build'] = {
            'success': success,
            'duration_seconds': duration,
            'build_type': build_type
        }

        return success

    def run_program(self):
        """Program FPGA"""
        self.log("=" * 70)
        self.log("STEP: Programming FPGA")
        self.log("=" * 70)

        args = ['--info']
        success, duration = self.run_script('fpga_programmer', args)

        self.results['steps']['program'] = {
            'success': success,
            'duration_seconds': duration
        }

        return success

    def run_comparison(self, num_steps=10, num_agents=100):
        """Run trail map comparison"""
        self.log("=" * 70)
        self.log("STEP: Comparing Trail Maps")
        self.log("=" * 70)

        args = [
            'full',
            '--steps', str(num_steps),
            '--agents', str(num_agents),
            '--save-images'
        ]
        success, duration = self.run_script('image_capture', args)

        self.results['steps']['compare'] = {
            'success': success,
            'duration_seconds': duration,
            'steps': num_steps,
            'agents': num_agents
        }

        return success

    def generate_summary(self):
        """Generate final summary"""
        total_duration = time.time() - self.start_time

        completed = sum(1 for step in self.results['steps'].values() if step.get('success', False))
        total = len(self.results['steps'])
        failed = total - completed

        self.results['summary'] = {
            'total_steps': total,
            'completed': completed,
            'failed': failed,
            'total_duration_seconds': total_duration,
            'overall_success': failed == 0
        }

        self.log("=" * 70)
        self.log("VALIDATION SUMMARY")
        self.log("=" * 70)
        self.log(f"Total steps: {total}")
        self.log(f"Completed:   {completed}")
        self.log(f"Failed:      {failed}")
        self.log(f"Total time:  {total_duration / 60:.1f} minutes")
        self.log("=" * 70)

        # Detailed step results
        for step_name, step_data in self.results['steps'].items():
            status = "PASS" if step_data.get('success', False) else "FAIL"
            duration = step_data.get('duration_seconds', 0)
            self.log(f"{step_name.upper():<12} [{status}] ({duration:.1f}s)")

        self.log("=" * 70)

        if self.results['summary']['overall_success']:
            self.log("VALIDATION: PASSED", 'INFO')
        else:
            self.log("VALIDATION: FAILED", 'ERROR')

    def save_results(self):
        """Save results to JSON"""
        results_file = self.log_dir / f"validation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        self.log(f"Results saved to: {results_file}")
        return results_file


def main():
    parser = argparse.ArgumentParser(
        description='Full Validation Workflow - Master Automation Script',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Steps:
  tests          - Run cocotb test suite
  build-vga      - Build VGA test pattern
  build-simple   - Build simplified design
  build-main     - Build full design
  program        - Program FPGA
  compare        - Compare FPGA vs Python reference
  all            - Run all steps in sequence

Examples:
  %(prog)s tests                        # Run tests only
  %(prog)s build-main program           # Build and program
  %(prog)s all                          # Full workflow
  %(prog)s all --dry-run                # Show what would be done
  %(prog)s tests compare --verbose      # Tests and comparison with details

Typical Workflows:
  1. Quick test:
     %(prog)s tests

  2. Build and deploy:
     %(prog)s build-main program

  3. Full validation:
     %(prog)s all

  4. Test-driven development:
     %(prog)s tests build-main program compare
        """
    )

    parser.add_argument('steps',
                       nargs='*',
                       choices=['tests', 'build-vga', 'build-simple', 'build-main',
                               'program', 'compare', 'all'],
                       help='Steps to run')
    parser.add_argument('--test-suite',
                       choices=['basic', 'comparison', 'integration', 'all'],
                       default='basic',
                       help='Test suite to run (default: basic)')
    parser.add_argument('--build-type',
                       choices=['vga', 'simple', 'main', 'debug'],
                       default='main',
                       help='Build type for build step (default: main)')
    parser.add_argument('--compare-steps',
                       type=int,
                       default=10,
                       help='Number of steps for comparison (default: 10)')
    parser.add_argument('--compare-agents',
                       type=int,
                       default=100,
                       help='Number of agents for comparison (default: 100)')
    parser.add_argument('--dry-run',
                       action='store_true',
                       help='Show what would be done without executing')
    parser.add_argument('--verbose', '-v',
                       action='store_true',
                       help='Verbose output from all scripts')
    parser.add_argument('--continue-on-error',
                       action='store_true',
                       help='Continue even if a step fails')

    args = parser.parse_args()

    # Validate arguments
    if not args.steps:
        print("ERROR: No steps specified", file=sys.stderr)
        print("Use --help to see available steps", file=sys.stderr)
        return 1

    try:
        # Create validation instance
        validation = FullValidation(
            dry_run=args.dry_run,
            verbose=args.verbose
        )

        validation.log("=" * 70)
        validation.log("SLIME SIMULATOR - FULL VALIDATION")
        validation.log("=" * 70)
        validation.log(f"Steps: {', '.join(args.steps)}")
        validation.log(f"Dry run: {args.dry_run}")
        validation.log("=" * 70)

        validation.start_time = time.time()

        # Expand 'all' to all steps
        if 'all' in args.steps:
            steps = ['tests', 'build-main', 'program', 'compare']
        else:
            steps = args.steps

        # Execute steps
        for step in steps:
            success = False

            if step == 'tests':
                success = validation.run_tests(args.test_suite)

            elif step.startswith('build-'):
                build_type = step.replace('build-', '')
                success = validation.run_build(build_type)

            elif step == 'program':
                success = validation.run_program()

            elif step == 'compare':
                success = validation.run_comparison(
                    num_steps=args.compare_steps,
                    num_agents=args.compare_agents
                )

            if not success and not args.continue_on_error:
                validation.log(f"Step {step} failed, stopping workflow", 'ERROR')
                break

        # Generate summary
        validation.generate_summary()

        # Save results
        validation.save_results()

        validation.log("=" * 70)
        validation.log(f"Log file: {validation.log_file}")
        validation.log("=" * 70)

        # Exit with appropriate code
        if validation.results['summary']['overall_success']:
            return 0
        else:
            return 1

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
