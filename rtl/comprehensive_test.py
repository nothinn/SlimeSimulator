#!/usr/bin/env python3
"""
Comprehensive Test Orchestration Script
Master script to coordinate all testing phases:
1. Python reference generation
2. RTL simulation (cocotb) if available
3. FPGA hardware testing if available
4. Multi-way comparison and analysis
5. Report generation
"""

import subprocess
import sys
import os
from pathlib import Path
import time
import json
from datetime import datetime
import argparse


class ComprehensiveTest:
    """Master test orchestrator."""

    def __init__(self, output_dir="test_results_comprehensive", iterations=None,
                 skip_rtl_sim=False, skip_fpga=False, fpga_threshold=85.0):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.iterations = iterations or [1, 5, 10, 20, 50, 100]
        self.skip_rtl_sim = skip_rtl_sim
        self.skip_fpga = skip_fpga
        self.fpga_threshold = fpga_threshold

        self.results = {
            "start_time": datetime.now().isoformat(),
            "phases": {},
            "summary": {}
        }

        self.test_start_time = time.time()

    def run_phase(self, phase_name, func):
        """Run a test phase with error handling."""
        print("\n" + "="*80)
        print(f"PHASE: {phase_name}")
        print("="*80)

        phase_start = time.time()
        phase_result = {
            "start_time": datetime.now().isoformat(),
            "status": "unknown"
        }

        try:
            result = func()
            phase_result["status"] = "success" if result else "failed"
            phase_result["result"] = result
        except Exception as e:
            print(f"\n✗ ERROR in {phase_name}: {e}")
            phase_result["status"] = "error"
            phase_result["error"] = str(e)
            result = None

        phase_elapsed = time.time() - phase_start
        phase_result["elapsed_sec"] = phase_elapsed
        phase_result["end_time"] = datetime.now().isoformat()

        self.results["phases"][phase_name] = phase_result

        status_symbol = "✓" if phase_result["status"] == "success" else "✗" if phase_result["status"] == "failed" else "⚠"
        print(f"\n{status_symbol} Phase '{phase_name}' {phase_result['status']} ({phase_elapsed:.1f}s)")

        return result

    def phase_python_reference(self):
        """Phase 1: Generate Python reference data."""
        print("Generating Python reference trail maps...")

        iter_str = ','.join(map(str, self.iterations))
        cmd = [
            sys.executable,
            "sim/regression_test.py",
            "--reference-only",
            f"--iterations={iter_str}",
            "--visualize",
            f"--output-dir={self.output_dir / 'python_reference'}"
        ]

        print(f"Command: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=Path.cwd())

        if result.returncode != 0:
            print("✗ Python reference generation failed")
            return False

        print("✓ Python reference generation complete")
        return True

    def phase_rtl_simulation(self):
        """Phase 2: RTL simulation via cocotb (if available)."""
        if self.skip_rtl_sim:
            print("⊘ RTL simulation skipped (--skip-rtl-sim)")
            return None

        print("Checking for cocotb testbench...")

        makefile = Path("sim/Makefile")
        if not makefile.exists():
            print("⊘ No cocotb Makefile found - skipping RTL simulation")
            return None

        # Check if cocotb is installed
        try:
            import cocotb
            print(f"✓ cocotb found (version {cocotb.__version__})")
        except ImportError:
            print("⊘ cocotb not installed - skipping RTL simulation")
            return None

        print("Running RTL simulation...")

        # For now, we'll skip actual simulation as it requires specific testbench setup
        # In a real scenario, this would run:
        # cd sim && make SIM=icarus TOPLEVEL=slime_top MODULE=test_slime_top

        print("⊘ RTL simulation phase not yet fully integrated")
        print("  (Would run: cd sim && make)")

        return None

    def phase_fpga_hardware(self):
        """Phase 3: FPGA hardware testing."""
        if self.skip_fpga:
            print("⊘ FPGA testing skipped (--skip-fpga)")
            return None

        print("Checking for FPGA hardware...")

        # Check if Vivado is available
        vivado_check = subprocess.run(["which", "vivado"], capture_output=True)
        if vivado_check.returncode != 0:
            print("⊘ Vivado not found - skipping FPGA testing")
            return None

        # Check if bitstream exists
        bitstream = Path("vivado_project/slime_simulator.runs/impl_1/slime_top.bit")
        if not bitstream.exists():
            print(f"⊘ Bitstream not found - build first with build.tcl")
            print(f"  Expected: {bitstream}")
            return None

        print("✓ Bitstream found")
        print("⊘ FPGA hardware capture not yet implemented")
        print("  (Would: program FPGA → run iterations → capture via JTAG)")

        return None

    def phase_comparison(self):
        """Phase 4: Multi-way comparison."""
        print("Generating comparison reports...")

        python_dir = self.output_dir / "python_reference"
        if not python_dir.exists():
            print("✗ Python reference not found - cannot compare")
            return False

        # For now, just note that we have Python reference
        print("✓ Python reference available for comparison")

        # Future: Compare with RTL sim if available
        # Future: Compare with FPGA if available

        return True

    def phase_statistical_analysis(self):
        """Phase 5: Detailed statistical analysis."""
        print("Performing statistical analysis...")

        python_dir = self.output_dir / "python_reference"
        if not python_dir.exists():
            print("✗ No data to analyze")
            return False

        # Load and analyze Python results
        stats = {}
        for num_steps in self.iterations:
            iter_dir = python_dir / f"iter_{num_steps:03d}"
            metadata_file = iter_dir / "python_metadata.json"

            if metadata_file.exists():
                with open(metadata_file) as f:
                    metadata = json.load(f)
                    stats[num_steps] = metadata

        # Save analysis
        analysis_file = self.output_dir / "statistical_analysis.json"
        with open(analysis_file, 'w') as f:
            json.dump(stats, f, indent=2)

        print(f"✓ Statistical analysis saved to {analysis_file}")
        return True

    def phase_report_generation(self):
        """Phase 6: Generate comprehensive reports."""
        print("Generating final reports...")

        # Generate summary report
        report_file = self.output_dir / "COMPREHENSIVE_TEST_REPORT.md"

        with open(report_file, 'w') as f:
            f.write("# Comprehensive Test Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Test Duration:** {time.time() - self.test_start_time:.1f} seconds\n\n")

            f.write("## Test Configuration\n\n")
            f.write(f"- Iteration points: {self.iterations}\n")
            f.write(f"- Output directory: `{self.output_dir}`\n")
            f.write(f"- FPGA threshold: {self.fpga_threshold}%\n\n")

            f.write("## Phase Results\n\n")
            for phase_name, phase_data in self.results["phases"].items():
                status = phase_data["status"]
                elapsed = phase_data.get("elapsed_sec", 0)
                symbol = "✓" if status == "success" else "⊘" if status == "skipped" else "✗"

                f.write(f"### {symbol} {phase_name}\n\n")
                f.write(f"- **Status:** {status}\n")
                f.write(f"- **Duration:** {elapsed:.1f}s\n")

                if "error" in phase_data:
                    f.write(f"- **Error:** {phase_data['error']}\n")

                f.write("\n")

            f.write("## Test Data Locations\n\n")
            f.write(f"- Python reference: `{self.output_dir / 'python_reference'}`\n")
            f.write(f"- Full report: `{report_file}`\n\n")

            f.write("## Summary\n\n")

            # Count successes/failures
            phase_statuses = [p["status"] for p in self.results["phases"].values()]
            success_count = phase_statuses.count("success")
            total_phases = len(phase_statuses)

            f.write(f"**{success_count}/{total_phases} phases completed successfully**\n\n")

            if success_count == total_phases:
                f.write("✓ All phases passed!\n")
            elif success_count > 0:
                f.write("⚠ Some phases incomplete or skipped\n")
            else:
                f.write("✗ Test suite encountered errors\n")

        print(f"✓ Comprehensive report saved to {report_file}")

        # Save JSON results
        results_json = self.output_dir / "test_results.json"
        self.results["end_time"] = datetime.now().isoformat()
        self.results["total_elapsed_sec"] = time.time() - self.test_start_time

        with open(results_json, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"✓ JSON results saved to {results_json}")

        return True

    def run_all(self):
        """Run all test phases."""
        print("\n" + "="*80)
        print("COMPREHENSIVE SLIME SIMULATOR TEST SUITE")
        print("="*80)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Output:  {self.output_dir}")
        print("="*80)

        # Phase 1: Python reference (always run)
        self.run_phase("Python Reference Generation", self.phase_python_reference)

        # Phase 2: RTL simulation (optional)
        if not self.skip_rtl_sim:
            self.run_phase("RTL Simulation", self.phase_rtl_simulation)

        # Phase 3: FPGA hardware (optional)
        if not self.skip_fpga:
            self.run_phase("FPGA Hardware Testing", self.phase_fpga_hardware)

        # Phase 4: Comparison
        self.run_phase("Multi-way Comparison", self.phase_comparison)

        # Phase 5: Statistical analysis
        self.run_phase("Statistical Analysis", self.phase_statistical_analysis)

        # Phase 6: Report generation
        self.run_phase("Report Generation", self.phase_report_generation)

        # Final summary
        total_elapsed = time.time() - self.test_start_time

        print("\n" + "="*80)
        print("TEST SUITE COMPLETE")
        print("="*80)
        print(f"Total time: {total_elapsed:.1f} seconds ({total_elapsed/60:.1f} minutes)")
        print(f"Results:    {self.output_dir}")
        print("="*80 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Comprehensive test orchestration for Slime Simulator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all tests (Python only by default, as FPGA may not be available)
  python3 comprehensive_test.py

  # Run with specific iterations
  python3 comprehensive_test.py --iterations 1,10,50,100

  # Skip FPGA testing
  python3 comprehensive_test.py --skip-fpga

  # Custom output directory
  python3 comprehensive_test.py --output-dir my_test_results
        """
    )

    parser.add_argument('--output-dir', default='test_results_comprehensive',
                       help='Output directory for all test results')
    parser.add_argument('--iterations', type=str, default='1,5,10,20,50,100',
                       help='Comma-separated iteration points')
    parser.add_argument('--skip-rtl-sim', action='store_true',
                       help='Skip RTL simulation phase')
    parser.add_argument('--skip-fpga', action='store_true',
                       help='Skip FPGA hardware testing phase')
    parser.add_argument('--fpga-threshold', type=float, default=85.0,
                       help='Acceptance threshold for FPGA comparison (default: 85%%)')

    args = parser.parse_args()

    # Parse iterations
    iterations = [int(x.strip()) for x in args.iterations.split(',')]

    # Run comprehensive test
    test = ComprehensiveTest(
        output_dir=args.output_dir,
        iterations=iterations,
        skip_rtl_sim=args.skip_rtl_sim,
        skip_fpga=args.skip_fpga,
        fpga_threshold=args.fpga_threshold
    )

    test.run_all()


if __name__ == '__main__':
    main()
