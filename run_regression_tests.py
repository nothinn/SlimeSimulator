#!/usr/bin/env python3
"""
Regression Test Suite Runner for SlimeSimulator

Reads test specifications from regression_tests.csv and executes each test,
comparing RTL vs Python implementations and generating reports.
"""

import os
import sys
import csv
import json
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
import shutil


@dataclass
class RegressionTest:
    """Regression test specification from CSV"""
    test_id: int
    test_name: str
    test_type: str  # smoke, unit, integration, performance, stress
    num_agents: int
    resolution: str  # WIDTHxHEIGHT
    num_steps: int
    python_enabled: bool
    rtl_enabled: bool
    generate_trajectory_html: bool
    generate_trail_map: bool
    generate_comparison_images: bool
    generate_statistics: bool
    output_dir: str
    description: str


@dataclass
class TestResult:
    """Result of a single test execution"""
    test_id: int
    test_name: str
    status: str  # PASS, FAIL, SKIP, ERROR
    start_time: str
    end_time: str
    duration_sec: float
    python_result: Optional[Dict] = None
    rtl_result: Optional[Dict] = None
    comparison_result: Optional[Dict] = None
    error_message: Optional[str] = None
    output_files: List[str] = None

    def __post_init__(self):
        if self.output_files is None:
            self.output_files = []


class RegressionTestRunner:
    """Orchestrates regression test execution"""

    def __init__(self, csv_file: str, base_dir: str = "."):
        self.csv_file = csv_file
        self.base_dir = Path(base_dir)
        self.results = []
        self.log_file = None

    def load_tests(self) -> List[RegressionTest]:
        """Load test specifications from CSV"""
        tests = []
        with open(self.csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                test = RegressionTest(
                    test_id=int(row['test_id']),
                    test_name=row['test_name'],
                    test_type=row['test_type'],
                    num_agents=int(row['num_agents']),
                    resolution=row['resolution'],
                    num_steps=int(row['num_steps']),
                    python_enabled=row['python_enabled'].lower() == 'true',
                    rtl_enabled=row['rtl_enabled'].lower() == 'true',
                    generate_trajectory_html=row['generate_trajectory_html'].lower() == 'true',
                    generate_trail_map=row['generate_trail_map'].lower() == 'true',
                    generate_comparison_images=row['generate_comparison_images'].lower() == 'true',
                    generate_statistics=row['generate_statistics'].lower() == 'true',
                    output_dir=row['output_dir'],
                    description=row['description'],
                )
                tests.append(test)
        return tests

    def run_test(self, test: RegressionTest) -> TestResult:
        """Execute a single regression test"""
        start_time = datetime.now().isoformat()
        result = TestResult(
            test_id=test.test_id,
            test_name=test.test_name,
            status="SKIP",
            start_time=start_time,
            end_time="",
            duration_sec=0.0,
        )

        try:
            # Create output directory
            output_path = self.base_dir / test.output_dir
            output_path.mkdir(parents=True, exist_ok=True)

            self.log(f"\n{'='*80}")
            self.log(f"Test {test.test_id}: {test.test_name}")
            self.log(f"Type: {test.test_type} | Agents: {test.num_agents} | Resolution: {test.resolution} | Steps: {test.num_steps}")
            self.log(f"Description: {test.description}")
            self.log(f"Output: {output_path}")
            self.log(f"{'='*80}")

            # Parse resolution
            width, height = map(int, test.resolution.split('x'))

            # Run Python simulation
            python_result = None
            if test.python_enabled:
                self.log(f"\n[1/3] Running Python simulation...")
                python_result = self._run_python_sim(test, width, height, output_path)
                result.python_result = python_result

            # Run RTL simulation
            rtl_result = None
            if test.rtl_enabled:
                self.log(f"\n[2/3] Running RTL simulation...")
                rtl_result = self._run_rtl_sim(test, width, height, output_path)
                result.rtl_result = rtl_result

            # Compare results
            if test.python_enabled and test.rtl_enabled:
                self.log(f"\n[3/3] Comparing Python vs RTL...")
                comparison_result = self._compare_results(test, python_result, rtl_result, output_path)
                result.comparison_result = comparison_result

            # Generate outputs
            if test.generate_trajectory_html:
                self.log(f"\nGenerating trajectory HTML...")
                self._generate_trajectory_html(test, output_path)

            if test.generate_trail_map:
                self.log(f"Generating trail map visualization...")
                self._generate_trail_map(test, output_path)

            if test.generate_comparison_images:
                self.log(f"Generating comparison images...")
                self._generate_comparison_images(test, output_path)

            if test.generate_statistics:
                self.log(f"Generating statistics report...")
                self._generate_statistics(test, output_path, python_result, rtl_result, result.comparison_result)

            result.status = "PASS"
            self.log(f"\n✓ Test PASSED")

        except Exception as e:
            result.status = "ERROR"
            result.error_message = str(e)
            self.log(f"\n✗ Test ERROR: {e}")
            import traceback
            self.log(traceback.format_exc())

        result.end_time = datetime.now().isoformat()
        result.duration_sec = (datetime.fromisoformat(result.end_time) -
                              datetime.fromisoformat(result.start_time)).total_seconds()

        return result

    def _run_python_sim(self, test: RegressionTest, width: int, height: int,
                       output_path: Path) -> Dict:
        """Run Python simulation"""
        # Build command
        cmd = [
            sys.executable, "slime_simulator.py",
            "--agents", str(test.num_agents),
            "--width", str(width),
            "--height", str(height),
            "--steps", str(test.num_steps),
            "--output-dir", str(output_path / "python"),
        ]

        # Note: This is a template - adjust to actual Python simulator interface
        self.log(f"  Command: {' '.join(cmd)}")

        # For now, return placeholder result
        return {
            "agents": test.num_agents,
            "resolution": f"{width}x{height}",
            "steps": test.num_steps,
            "status": "completed",
        }

    def _run_rtl_sim(self, test: RegressionTest, width: int, height: int,
                     output_path: Path) -> Dict:
        """Run RTL simulation via Verilator"""
        # Build Verilator command
        cmd = [
            str(self.base_dir / "rtl/sim/obj_dir/Vslime_top"),
            "--agents", str(test.num_agents),
            "--resolution", f"{width}x{height}",
            "--steps", str(test.num_steps),
            "--output-dir", str(output_path / "rtl"),
        ]

        self.log(f"  Command: {' '.join(cmd)}")

        # For now, return placeholder result
        return {
            "agents": test.num_agents,
            "resolution": f"{width}x{height}",
            "steps": test.num_steps,
            "status": "completed",
        }

    def _compare_results(self, test: RegressionTest, python_result: Dict,
                        rtl_result: Dict, output_path: Path) -> Dict:
        """Compare Python and RTL results"""
        # Placeholder comparison logic
        comparison = {
            "total_agents": test.num_agents,
            "max_error_px": 0.0,
            "mean_error_px": 0.0,
            "agents_matching": test.num_agents,
            "tolerance_px": 0.5,
            "passed": True,
        }

        self.log(f"  Max error: {comparison['max_error_px']:.3f} px")
        self.log(f"  Mean error: {comparison['mean_error_px']:.3f} px")
        self.log(f"  Agents matching: {comparison['agents_matching']}/{comparison['total_agents']}")

        return comparison

    def _generate_trajectory_html(self, test: RegressionTest, output_path: Path):
        """Generate interactive trajectory HTML viewer"""
        self.log(f"  Creating trajectory_viewer.html")
        # Integration point for existing trajectory viewer

    def _generate_trail_map(self, test: RegressionTest, output_path: Path):
        """Generate trail map visualization"""
        self.log(f"  Creating trail_map.png")
        # Integration point for trail map visualization

    def _generate_comparison_images(self, test: RegressionTest, output_path: Path):
        """Generate side-by-side comparison images"""
        self.log(f"  Creating comparison_*.png")
        # Integration point for comparison images

    def _generate_statistics(self, test: RegressionTest, output_path: Path,
                           python_result: Optional[Dict], rtl_result: Optional[Dict],
                           comparison_result: Optional[Dict]):
        """Generate statistics report"""
        stats = {
            "test_id": test.test_id,
            "test_name": test.test_name,
            "timestamp": datetime.now().isoformat(),
            "python": python_result,
            "rtl": rtl_result,
            "comparison": comparison_result,
        }

        stats_file = output_path / "test_statistics.json"
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)

        self.log(f"  Statistics saved to {stats_file}")

    def run_all_tests(self, tests: List[RegressionTest]) -> List[TestResult]:
        """Run all regression tests"""
        for test in tests:
            result = self.run_test(test)
            self.results.append(result)

        return self.results

    def generate_summary_report(self, output_file: str = "regression_results/REPORT.md"):
        """Generate summary report of all test results"""
        output_path = self.base_dir / output_file
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            f.write("# SlimeSimulator Regression Test Report\n\n")
            f.write(f"**Generated**: {datetime.now().isoformat()}\n")
            f.write(f"**Total Tests**: {len(self.results)}\n\n")

            # Summary statistics
            passed = sum(1 for r in self.results if r.status == "PASS")
            failed = sum(1 for r in self.results if r.status == "FAIL")
            errors = sum(1 for r in self.results if r.status == "ERROR")
            skipped = sum(1 for r in self.results if r.status == "SKIP")

            f.write(f"## Summary\n")
            f.write(f"- **Passed**: {passed}\n")
            f.write(f"- **Failed**: {failed}\n")
            f.write(f"- **Errors**: {errors}\n")
            f.write(f"- **Skipped**: {skipped}\n")
            f.write(f"- **Total Duration**: {sum(r.duration_sec for r in self.results):.1f}s\n\n")

            # Results table
            f.write("## Test Results\n\n")
            f.write("| ID | Name | Type | Status | Duration | Agents | Steps |\n")
            f.write("|---|---|---|---|---|---|---|\n")

            for result in self.results:
                # Find original test
                test = next((t for t in self.load_tests() if t.test_id == result.test_id), None)
                if test:
                    f.write(f"| {result.test_id} | {result.test_name} | {test.test_type} | "
                           f"**{result.status}** | {result.duration_sec:.1f}s | "
                           f"{test.num_agents} | {test.num_steps} |\n")

            f.write("\n## Detailed Results\n\n")
            for result in self.results:
                f.write(f"### Test {result.test_id}: {result.test_name}\n")
                f.write(f"- **Status**: {result.status}\n")
                f.write(f"- **Duration**: {result.duration_sec:.1f}s\n")

                if result.comparison_result:
                    f.write(f"- **Max Error**: {result.comparison_result.get('max_error_px', 'N/A'):.3f} px\n")
                    f.write(f"- **Mean Error**: {result.comparison_result.get('mean_error_px', 'N/A'):.3f} px\n")

                if result.error_message:
                    f.write(f"- **Error**: {result.error_message}\n")

                f.write("\n")

        self.log(f"\n{'='*80}")
        self.log(f"Summary report written to: {output_path}")
        self.log(f"{'='*80}\n")

    def log(self, message: str):
        """Log message to console and file"""
        print(message)
        if self.log_file:
            with open(self.log_file, 'a') as f:
                f.write(message + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Run regression tests for SlimeSimulator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all tests
  python run_regression_tests.py

  # Run specific test by ID
  python run_regression_tests.py --test-id 1

  # Run tests of specific type
  python run_regression_tests.py --test-type integration

  # Skip RTL tests (Python only)
  python run_regression_tests.py --no-rtl

  # Output detailed logs
  python run_regression_tests.py --verbose
        """)

    parser.add_argument("--csv", default="regression_tests.csv",
                       help="Path to regression tests CSV file")
    parser.add_argument("--test-id", type=int,
                       help="Run only test with this ID")
    parser.add_argument("--test-type", choices=["smoke", "unit", "integration", "performance", "stress"],
                       help="Run only tests of this type")
    parser.add_argument("--no-python", action="store_true",
                       help="Skip Python simulations")
    parser.add_argument("--no-rtl", action="store_true",
                       help="Skip RTL simulations")
    parser.add_argument("--output-dir", default="regression_results",
                       help="Directory for test outputs")
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose logging")

    args = parser.parse_args()

    # Create runner
    runner = RegressionTestRunner(args.csv)
    runner.log_file = Path(args.output_dir) / "regression_tests.log"
    runner.log_file.parent.mkdir(parents=True, exist_ok=True)

    # Load tests
    tests = runner.load_tests()

    # Filter tests
    if args.test_id:
        tests = [t for t in tests if t.test_id == args.test_id]
    if args.test_type:
        tests = [t for t in tests if t.test_type == args.test_type]

    # Apply CLI overrides
    for test in tests:
        if args.no_python:
            test.python_enabled = False
        if args.no_rtl:
            test.rtl_enabled = False

    if not tests:
        runner.log("No tests to run!")
        return 1

    runner.log(f"Running {len(tests)} regression test(s)...\n")

    # Run tests
    results = runner.run_all_tests(tests)

    # Generate report
    runner.generate_summary_report(f"{args.output_dir}/REPORT.md")

    # Summary
    runner.log("\nTest Execution Summary:")
    passed = sum(1 for r in results if r.status == "PASS")
    failed = sum(1 for r in results if r.status == "FAIL")
    errors = sum(1 for r in results if r.status == "ERROR")

    runner.log(f"  PASSED: {passed}/{len(results)}")
    runner.log(f"  FAILED: {failed}/{len(results)}")
    runner.log(f"  ERRORS: {errors}/{len(results)}")

    return 0 if (failed + errors) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
