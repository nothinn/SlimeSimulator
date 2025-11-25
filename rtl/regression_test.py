#!/usr/bin/env python3
"""
Master Regression Test Script for Slime Simulator RTL

This script orchestrates the complete regression test workflow:
1. Generate Python reference trail maps
2. Program FPGA with bitstream (optional)
3. Capture RTL trail maps from FPGA
4. Compare reference vs RTL
5. Generate comprehensive test report

Usage:
    # Full workflow
    python regression_test.py --bitstream build/slime_top.bit

    # Skip FPGA programming (already programmed)
    python regression_test.py --no-program

    # Python reference only (for development)
    python regression_test.py --reference-only

    # Custom test configuration
    python regression_test.py --bitstream build/slime_top.bit \\
        --iterations 1,2,5,10,15,20 --threshold 99.0
"""

import sys
import time
import argparse
import subprocess
from pathlib import Path
from datetime import datetime


class RegressionTestRunner:
    """
    Orchestrates the complete regression test workflow.
    """

    def __init__(
        self,
        width: int = 160,
        height: int = 120,
        num_agents: int = 1000,
        iterations: list = [1, 5, 10, 20],
        seed: int = 0xDEADBEEF,
        threshold: float = 95.0,
        output_dir: str = "regression_test_results",
        verbose: bool = True
    ):
        """
        Initialize regression test runner.

        Args:
            width: Simulation width
            height: Simulation height
            num_agents: Number of agents
            iterations: Iteration points to test
            seed: LFSR seed
            threshold: Pass threshold percentage
            output_dir: Base output directory
            verbose: Print detailed messages
        """
        self.width = width
        self.height = height
        self.num_agents = num_agents
        self.iterations = iterations
        self.seed = seed
        self.threshold = threshold
        self.output_dir = Path(output_dir)
        self.verbose = verbose

        # Subdirectories
        self.ref_dir = self.output_dir / "reference"
        self.rtl_dir = self.output_dir / "rtl_capture"

        # Scripts
        self.script_dir = Path(__file__).parent
        self.gen_ref_script = self.script_dir / "generate_python_ref.py"
        self.fpga_script = self.script_dir / "fpga_controller.py"
        self.compare_script = self.script_dir / "compare_trails.py"

        # Results
        self.csv_output = self.output_dir / "comparison_report.csv"
        self.detailed_output = self.output_dir / "detailed_analysis.txt"
        self.summary_output = self.output_dir / "test_summary.txt"

    def log(self, message: str, level: str = "INFO"):
        """Print log message with timestamp."""
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            prefix = {
                "INFO": "[INFO]",
                "STEP": "[STEP]",
                "SUCCESS": "[SUCCESS]",
                "ERROR": "[ERROR]",
                "WARNING": "[WARNING]"
            }.get(level, "[INFO]")
            print(f"{timestamp} {prefix} {message}")

    def run_command(
        self,
        cmd: list,
        description: str,
        timeout: int = 300
    ) -> bool:
        """
        Run a command and return success status.

        Args:
            cmd: Command and arguments as list
            description: Human-readable description
            timeout: Command timeout in seconds

        Returns:
            True if command succeeded, False otherwise
        """
        self.log(f"{description}...")
        self.log(f"  Command: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            if result.returncode != 0:
                self.log(f"Command failed with exit code {result.returncode}", "ERROR")
                if result.stderr:
                    self.log(f"Error output:\n{result.stderr}", "ERROR")
                return False

            self.log(f"{description} completed successfully", "SUCCESS")
            return True

        except subprocess.TimeoutExpired:
            self.log(f"Command timed out after {timeout}s", "ERROR")
            return False
        except Exception as e:
            self.log(f"Command failed: {e}", "ERROR")
            return False

    def generate_reference(self) -> bool:
        """
        Generate Python reference trail maps.

        Returns:
            True if successful
        """
        self.log("=" * 80, "STEP")
        self.log("STEP 1: Generate Python Reference Trail Maps", "STEP")
        self.log("=" * 80, "STEP")

        cmd = [
            sys.executable,
            str(self.gen_ref_script),
            "--width", str(self.width),
            "--height", str(self.height),
            "--agents", str(self.num_agents),
            "--iterations", ",".join(map(str, self.iterations)),
            "--seed", f"0x{self.seed:08X}",
            "--output-dir", str(self.ref_dir)
        ]

        if not self.verbose:
            cmd.append("--quiet")

        return self.run_command(
            cmd,
            "Generating Python reference",
            timeout=300
        )

    def program_fpga(self, bitstream: str) -> bool:
        """
        Program FPGA with bitstream.

        Args:
            bitstream: Path to bitstream file

        Returns:
            True if successful
        """
        self.log("=" * 80, "STEP")
        self.log("STEP 2: Program FPGA with Bitstream", "STEP")
        self.log("=" * 80, "STEP")

        bitstream_path = Path(bitstream)
        if not bitstream_path.exists():
            self.log(f"Bitstream not found: {bitstream}", "ERROR")
            return False

        self.log(f"Bitstream: {bitstream_path.absolute()}")

        cmd = [
            sys.executable,
            str(self.fpga_script),
            "--bitstream", str(bitstream_path),
            "--iterations", ",".join(map(str, self.iterations)),
            "--output-dir", str(self.rtl_dir),
            "--width", str(self.width),
            "--height", str(self.height),
            "--seed", f"0x{self.seed:08X}"
        ]

        if not self.verbose:
            cmd.append("--quiet")

        return self.run_command(
            cmd,
            "Programming FPGA",
            timeout=600
        )

    def capture_rtl(self) -> bool:
        """
        Capture RTL trail maps (without programming).

        Returns:
            True if successful
        """
        self.log("=" * 80, "STEP")
        self.log("STEP 2: Capture RTL Trail Maps", "STEP")
        self.log("=" * 80, "STEP")

        cmd = [
            sys.executable,
            str(self.fpga_script),
            "--no-program",
            "--iterations", ",".join(map(str, self.iterations)),
            "--output-dir", str(self.rtl_dir),
            "--width", str(self.width),
            "--height", str(self.height),
            "--seed", f"0x{self.seed:08X}"
        ]

        if not self.verbose:
            cmd.append("--quiet")

        return self.run_command(
            cmd,
            "Capturing RTL trail maps",
            timeout=600
        )

    def compare_results(self, visualize: bool = False) -> tuple:
        """
        Compare reference and RTL trail maps.

        Args:
            visualize: Generate visualization images

        Returns:
            Tuple of (success, pass_status)
            success: True if comparison ran successfully
            pass_status: True if all tests passed threshold
        """
        self.log("=" * 80, "STEP")
        self.log("STEP 3: Compare Reference vs RTL", "STEP")
        self.log("=" * 80, "STEP")

        cmd = [
            sys.executable,
            str(self.compare_script),
            "--reference", str(self.ref_dir),
            "--rtl", str(self.rtl_dir),
            "--iterations", ",".join(map(str, self.iterations)),
            "--width", str(self.width),
            "--height", str(self.height),
            "--threshold", str(self.threshold),
            "--output", str(self.csv_output),
            "--detailed-output", str(self.detailed_output)
        ]

        if visualize:
            cmd.append("--visualize")

        self.log("Comparing trail maps...")
        self.log(f"  Command: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            # Print comparison output
            if result.stdout:
                print(result.stdout)

            # Return code 0 = pass, 1 = fail, >1 = error
            if result.returncode > 1:
                self.log("Comparison failed with error", "ERROR")
                if result.stderr:
                    self.log(f"Error output:\n{result.stderr}", "ERROR")
                return False, False

            pass_status = (result.returncode == 0)
            self.log("Comparison completed successfully", "SUCCESS")
            return True, pass_status

        except subprocess.TimeoutExpired:
            self.log("Comparison timed out", "ERROR")
            return False, False
        except Exception as e:
            self.log(f"Comparison failed: {e}", "ERROR")
            return False, False

    def generate_summary(self, start_time: float, pass_status: bool):
        """
        Generate test summary file.

        Args:
            start_time: Test start timestamp
            pass_status: Overall pass/fail status
        """
        duration = time.time() - start_time
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(self.summary_output, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("Slime Simulator RTL Regression Test Summary\n")
            f.write("=" * 80 + "\n\n")

            f.write(f"Test Date:           {timestamp}\n")
            f.write(f"Test Duration:       {duration:.1f} seconds\n")
            f.write(f"Overall Status:      {'PASS' if pass_status else 'FAIL'}\n\n")

            f.write("Test Configuration:\n")
            f.write("-" * 80 + "\n")
            f.write(f"  Resolution:        {self.width}x{self.height}\n")
            f.write(f"  Number of Agents:  {self.num_agents}\n")
            f.write(f"  LFSR Seed:         0x{self.seed:08X}\n")
            f.write(f"  Iterations:        {self.iterations}\n")
            f.write(f"  Pass Threshold:    {self.threshold}%\n\n")

            f.write("Output Files:\n")
            f.write("-" * 80 + "\n")
            f.write(f"  Reference Dir:     {self.ref_dir.absolute()}\n")
            f.write(f"  RTL Capture Dir:   {self.rtl_dir.absolute()}\n")
            f.write(f"  Comparison CSV:    {self.csv_output.absolute()}\n")
            f.write(f"  Detailed Analysis: {self.detailed_output.absolute()}\n\n")

            f.write("=" * 80 + "\n")

        self.log(f"Test summary saved to: {self.summary_output.absolute()}")


def main():
    parser = argparse.ArgumentParser(
        description='Run complete RTL regression test workflow',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full workflow (program + test)
  python regression_test.py --bitstream build/slime_top.bit

  # FPGA already programmed
  python regression_test.py --no-program

  # Generate Python reference only
  python regression_test.py --reference-only

  # Custom configuration
  python regression_test.py --bitstream build/slime_top.bit \\
      --iterations 1,5,10,20,50,100 \\
      --threshold 99.0 \\
      --visualize

  # Different resolution (if supported by RTL)
  python regression_test.py --no-program \\
      --width 320 --height 240

Output Structure:
  regression_test_results/
    reference/               # Python reference trail maps
      trail_iter_001.bin
      trail_iter_005.bin
      ...
    rtl_capture/            # RTL captured trail maps
      trail_iter_001.bin
      trail_iter_005.bin
      ...
    comparison_report.csv   # Numerical comparison results
    detailed_analysis.txt   # Detailed text analysis
    test_summary.txt        # Overall test summary
    visualizations/         # Diff images (if --visualize)
      diff_iter_001.png
      diff_iter_005.png
      ...
        """
    )

    parser.add_argument('--bitstream', type=str,
                        help='Path to FPGA bitstream (.bit file)')
    parser.add_argument('--no-program', action='store_true',
                        help='Skip FPGA programming (already programmed)')
    parser.add_argument('--reference-only', action='store_true',
                        help='Generate Python reference only (no FPGA)')

    parser.add_argument('--width', type=int, default=160,
                        help='Simulation width (default: 160)')
    parser.add_argument('--height', type=int, default=120,
                        help='Simulation height (default: 120)')
    parser.add_argument('--agents', type=int, default=1000,
                        help='Number of agents (default: 1000)')
    parser.add_argument('--iterations', type=str, default='1,5,10,20',
                        help='Comma-separated iterations (default: 1,5,10,20)')
    parser.add_argument('--seed', type=lambda x: int(x, 0), default=0xDEADBEEF,
                        help='LFSR seed (default: 0xDEADBEEF)')
    parser.add_argument('--threshold', type=float, default=95.0,
                        help='Pass threshold percentage (default: 95.0)')

    parser.add_argument('--output-dir', type=str,
                        default='regression_test_results',
                        help='Output directory (default: regression_test_results)')
    parser.add_argument('--visualize', action='store_true',
                        help='Generate diff visualization images')
    parser.add_argument('--quiet', action='store_true',
                        help='Suppress detailed progress messages')

    args = parser.parse_args()

    # Validate arguments
    if not args.no_program and not args.reference_only and not args.bitstream:
        parser.error("--bitstream required unless --no-program or --reference-only specified")

    # Parse iterations
    try:
        iterations = [int(x.strip()) for x in args.iterations.split(',')]
    except ValueError:
        print(f"Error: Invalid iterations format: {args.iterations}")
        sys.exit(1)

    # Create test runner
    runner = RegressionTestRunner(
        width=args.width,
        height=args.height,
        num_agents=args.agents,
        iterations=iterations,
        seed=args.seed,
        threshold=args.threshold,
        output_dir=args.output_dir,
        verbose=not args.quiet
    )

    # Create output directory
    runner.output_dir.mkdir(parents=True, exist_ok=True)

    # Start test
    start_time = time.time()
    runner.log("=" * 80)
    runner.log("Starting RTL Regression Test")
    runner.log("=" * 80)
    runner.log(f"Configuration: {args.width}x{args.height}, "
               f"{args.agents} agents, "
               f"iterations {iterations}")

    # Track success
    success = True
    pass_status = False

    try:
        # STEP 1: Generate Python reference
        if not runner.generate_reference():
            runner.log("Failed to generate reference trails", "ERROR")
            success = False
        else:
            # STEP 2: FPGA interaction (unless reference-only)
            if not args.reference_only:
                if args.no_program:
                    # Capture only
                    if not runner.capture_rtl():
                        runner.log("Failed to capture RTL trails", "ERROR")
                        success = False
                else:
                    # Program and capture
                    if not runner.program_fpga(args.bitstream):
                        runner.log("Failed to program FPGA", "ERROR")
                        success = False

                # STEP 3: Compare results
                if success:
                    comp_success, pass_status = runner.compare_results(args.visualize)
                    if not comp_success:
                        runner.log("Comparison failed", "ERROR")
                        success = False

        # Generate summary
        if success:
            runner.generate_summary(start_time, pass_status)

        # Final status
        duration = time.time() - start_time
        runner.log("=" * 80)
        if success:
            if args.reference_only:
                runner.log("Reference generation completed successfully", "SUCCESS")
                runner.log(f"Total time: {duration:.1f} seconds")
            elif pass_status:
                runner.log("REGRESSION TEST PASSED", "SUCCESS")
                runner.log(f"All iterations met {args.threshold}% match threshold")
                runner.log(f"Total time: {duration:.1f} seconds")
            else:
                runner.log("REGRESSION TEST FAILED", "ERROR")
                runner.log(f"Some iterations did not meet {args.threshold}% threshold")
                runner.log(f"Total time: {duration:.1f} seconds")
        else:
            runner.log("REGRESSION TEST FAILED WITH ERRORS", "ERROR")
            runner.log(f"Total time: {duration:.1f} seconds")
        runner.log("=" * 80)

        # Exit with appropriate code
        if args.reference_only:
            sys.exit(0 if success else 1)
        else:
            sys.exit(0 if (success and pass_status) else 1)

    except KeyboardInterrupt:
        runner.log("\nTest interrupted by user", "WARNING")
        sys.exit(1)
    except Exception as e:
        runner.log(f"Unexpected error: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
