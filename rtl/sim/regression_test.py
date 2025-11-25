#!/usr/bin/env python3
"""
Regression Test Suite for Slime Simulator
Supports multi-iteration testing with visualization and comparison
"""

import numpy as np
import argparse
import sys
import os
from pathlib import Path
import time
import json
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from python_reference import SlimeSimulatorReference


class RegressionTest:
    """Run comprehensive regression tests at multiple iteration points."""

    def __init__(self, output_dir="test_results", iterations=None, visualize=True):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Default iteration points if not specified
        if iterations is None:
            self.iterations = [1, 5, 10, 20, 50, 100]
        else:
            self.iterations = sorted(iterations)

        self.visualize = visualize
        self.results = {}

    def run_python_reference(self):
        """Generate Python reference data at all iteration points."""
        print("\n" + "="*80)
        print("PHASE 1: Python Reference Model")
        print("="*80)

        results = {}

        for num_steps in self.iterations:
            print(f"\nRunning {num_steps} iterations...")
            start_time = time.time()

            # Create simulator
            sim = SlimeSimulatorReference(
                width=640, height=480,
                num_agents=1000,
                lfsr_seed=0xDEADBEEF
            )
            sim.init_agents_center()

            # Run simulation
            sim.run(num_steps)

            # Get results
            trail_map = sim.get_trail_map()
            lfsr_state = sim.lfsr.state

            elapsed = time.time() - start_time

            # Save results
            iter_dir = self.output_dir / f"iter_{num_steps:03d}"
            iter_dir.mkdir(exist_ok=True)

            # Save binary trail map
            trail_file = iter_dir / "python_trail.bin"
            trail_map.tofile(trail_file)

            # Save metadata
            metadata = {
                "iterations": num_steps,
                "width": 640,
                "height": 480,
                "num_agents": 1000,
                "lfsr_seed": "0xDEADBEEF",
                "lfsr_final_state": f"0x{lfsr_state:08X}",
                "elapsed_time_sec": elapsed,
                "trail_min": int(trail_map.min()),
                "trail_max": int(trail_map.max()),
                "trail_mean": float(trail_map.mean()),
                "trail_nonzero_pixels": int(np.count_nonzero(trail_map)),
            }

            metadata_file = iter_dir / "python_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)

            # Visualize if requested
            if self.visualize:
                self._visualize_trail(trail_map, iter_dir / "python_trail.png",
                                     f"Python Reference - {num_steps} iterations")

            results[num_steps] = {
                "trail_map": trail_map,
                "metadata": metadata,
                "elapsed": elapsed
            }

            print(f"  Completed in {elapsed:.3f}s")
            print(f"  Trail stats: min={metadata['trail_min']}, max={metadata['trail_max']}, " +
                  f"mean={metadata['trail_mean']:.2f}")
            print(f"  Non-zero pixels: {metadata['trail_nonzero_pixels']}")
            print(f"  Saved to: {iter_dir}")

        self.results['python'] = results

        # Generate summary
        summary_file = self.output_dir / "python_summary.txt"
        with open(summary_file, 'w') as f:
            f.write("="*80 + "\n")
            f.write("Python Reference Model Summary\n")
            f.write("="*80 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Iteration points: {self.iterations}\n\n")

            for num_steps, data in results.items():
                f.write(f"Iterations {num_steps}:\n")
                f.write(f"  Time:           {data['elapsed']:.3f}s\n")
                f.write(f"  Trail min/max:  {data['metadata']['trail_min']}/{data['metadata']['trail_max']}\n")
                f.write(f"  Trail mean:     {data['metadata']['trail_mean']:.2f}\n")
                f.write(f"  Active pixels:  {data['metadata']['trail_nonzero_pixels']}\n")
                f.write("\n")

        print(f"\n✓ Python reference generation complete")
        print(f"  Summary: {summary_file}")

        return results

    def compare_with_rtl_sim(self, rtl_sim_dir):
        """Compare Python reference with RTL simulation results."""
        print("\n" + "="*80)
        print("PHASE 2: RTL Simulation Comparison")
        print("="*80)

        if 'python' not in self.results:
            print("✗ ERROR: Python reference not available. Run Python phase first.")
            return None

        rtl_sim_path = Path(rtl_sim_dir)
        if not rtl_sim_path.exists():
            print(f"✗ ERROR: RTL simulation directory not found: {rtl_sim_dir}")
            return None

        comparison_results = {}

        for num_steps in self.iterations:
            print(f"\nComparing iteration {num_steps}...")

            iter_dir = self.output_dir / f"iter_{num_steps:03d}"
            rtl_trail_file = rtl_sim_path / f"iter_{num_steps:03d}" / "rtl_trail.bin"

            if not rtl_trail_file.exists():
                print(f"  ⚠ RTL data not found: {rtl_trail_file}")
                comparison_results[num_steps] = {"status": "missing"}
                continue

            # Load trail maps
            python_trail = self.results['python'][num_steps]['trail_map']
            rtl_trail = np.fromfile(rtl_trail_file, dtype=np.uint8).reshape(480, 640)

            # Calculate differences
            diff = python_trail.astype(np.int16) - rtl_trail.astype(np.int16)
            abs_diff = np.abs(diff)

            # Statistics
            exact_match = np.count_nonzero(abs_diff == 0)
            within_1 = np.count_nonzero(abs_diff <= 1)
            within_5 = np.count_nonzero(abs_diff <= 5)
            total_pixels = python_trail.size

            match_pct = (exact_match / total_pixels) * 100
            within_1_pct = (within_1 / total_pixels) * 100
            within_5_pct = (within_5 / total_pixels) * 100

            max_diff = abs_diff.max()
            mean_diff = abs_diff.mean()

            comparison = {
                "exact_match_pct": match_pct,
                "within_1_pct": within_1_pct,
                "within_5_pct": within_5_pct,
                "max_diff": int(max_diff),
                "mean_diff": float(mean_diff),
                "status": "pass" if match_pct >= 95.0 else "warn" if match_pct >= 90.0 else "fail"
            }

            comparison_results[num_steps] = comparison

            # Save comparison
            comp_file = iter_dir / "comparison_python_vs_rtl.json"
            with open(comp_file, 'w') as f:
                json.dump(comparison, f, indent=2)

            # Visualize differences
            if self.visualize:
                self._visualize_diff(python_trail, rtl_trail,
                                    iter_dir / "diff_python_vs_rtl.png",
                                    f"Python vs RTL - {num_steps} iterations")

            # Print results
            status_symbol = "✓" if comparison["status"] == "pass" else "⚠" if comparison["status"] == "warn" else "✗"
            print(f"  {status_symbol} Match: {match_pct:.2f}% exact, {within_5_pct:.2f}% within 5 levels")
            print(f"     Max diff: {max_diff}, Mean diff: {mean_diff:.2f}")

        # Save summary
        summary_file = self.output_dir / "comparison_python_vs_rtl.txt"
        with open(summary_file, 'w') as f:
            f.write("="*80 + "\n")
            f.write("Python vs RTL Simulation Comparison\n")
            f.write("="*80 + "\n\n")

            for num_steps, comp in comparison_results.items():
                if comp.get("status") == "missing":
                    f.write(f"Iteration {num_steps:3d}: MISSING\n")
                else:
                    status = comp["status"].upper()
                    f.write(f"Iteration {num_steps:3d}: {comp['exact_match_pct']:6.2f}% exact  ")
                    f.write(f"({comp['within_5_pct']:6.2f}% within 5)  [{status}]\n")

        print(f"\n✓ RTL simulation comparison complete")
        print(f"  Summary: {summary_file}")

        return comparison_results

    def compare_with_fpga(self, fpga_capture_dir, threshold=90.0):
        """Compare Python reference with FPGA hardware results."""
        print("\n" + "="*80)
        print("PHASE 3: FPGA Hardware Comparison")
        print("="*80)
        print(f"Acceptance threshold: {threshold}%")

        if 'python' not in self.results:
            print("✗ ERROR: Python reference not available. Run Python phase first.")
            return None

        fpga_path = Path(fpga_capture_dir)
        if not fpga_path.exists():
            print(f"✗ ERROR: FPGA capture directory not found: {fpga_capture_dir}")
            return None

        comparison_results = {}

        for num_steps in self.iterations:
            print(f"\nComparing iteration {num_steps}...")

            iter_dir = self.output_dir / f"iter_{num_steps:03d}"
            fpga_trail_file = fpga_path / f"iter_{num_steps:03d}" / "fpga_trail.bin"

            if not fpga_trail_file.exists():
                print(f"  ⚠ FPGA data not found: {fpga_trail_file}")
                comparison_results[num_steps] = {"status": "missing"}
                continue

            # Load trail maps
            python_trail = self.results['python'][num_steps]['trail_map']
            fpga_trail = np.fromfile(fpga_trail_file, dtype=np.uint8).reshape(480, 640)

            # Calculate differences
            diff = python_trail.astype(np.int16) - fpga_trail.astype(np.int16)
            abs_diff = np.abs(diff)

            # Statistics
            exact_match = np.count_nonzero(abs_diff == 0)
            within_1 = np.count_nonzero(abs_diff <= 1)
            within_5 = np.count_nonzero(abs_diff <= 5)
            within_10 = np.count_nonzero(abs_diff <= 10)
            total_pixels = python_trail.size

            match_pct = (exact_match / total_pixels) * 100
            within_1_pct = (within_1 / total_pixels) * 100
            within_5_pct = (within_5 / total_pixels) * 100
            within_10_pct = (within_10 / total_pixels) * 100

            max_diff = abs_diff.max()
            mean_diff = abs_diff.mean()

            comparison = {
                "exact_match_pct": match_pct,
                "within_1_pct": within_1_pct,
                "within_5_pct": within_5_pct,
                "within_10_pct": within_10_pct,
                "max_diff": int(max_diff),
                "mean_diff": float(mean_diff),
                "status": "pass" if match_pct >= threshold else "warn" if match_pct >= (threshold - 5) else "fail"
            }

            comparison_results[num_steps] = comparison

            # Save comparison
            comp_file = iter_dir / "comparison_python_vs_fpga.json"
            with open(comp_file, 'w') as f:
                json.dump(comparison, f, indent=2)

            # Visualize differences
            if self.visualize:
                self._visualize_diff(python_trail, fpga_trail,
                                    iter_dir / "diff_python_vs_fpga.png",
                                    f"Python vs FPGA - {num_steps} iterations")

            # Print results
            status_symbol = "✓" if comparison["status"] == "pass" else "⚠" if comparison["status"] == "warn" else "✗"
            print(f"  {status_symbol} Match: {match_pct:.2f}% exact, {within_5_pct:.2f}% within 5 levels")
            print(f"     Max diff: {max_diff}, Mean diff: {mean_diff:.2f}")

        # Save summary
        summary_file = self.output_dir / "comparison_python_vs_fpga.txt"
        with open(summary_file, 'w') as f:
            f.write("="*80 + "\n")
            f.write("Python vs FPGA Hardware Comparison\n")
            f.write("="*80 + "\n")
            f.write(f"Threshold: {threshold}%\n\n")

            for num_steps, comp in comparison_results.items():
                if comp.get("status") == "missing":
                    f.write(f"Iteration {num_steps:3d}: MISSING\n")
                else:
                    status = comp["status"].upper()
                    f.write(f"Iteration {num_steps:3d}: {comp['exact_match_pct']:6.2f}% exact  ")
                    f.write(f"({comp['within_5_pct']:6.2f}% within 5)  [{status}]\n")

        print(f"\n✓ FPGA hardware comparison complete")
        print(f"  Summary: {summary_file}")

        return comparison_results

    def _visualize_trail(self, trail_map, output_file, title):
        """Generate visualization of trail map."""
        fig, ax = plt.subplots(figsize=(12, 9))

        im = ax.imshow(trail_map, cmap='hot', interpolation='nearest', vmin=0, vmax=255)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.axis('off')

        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label='Trail Intensity')
        plt.tight_layout()
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()

    def _visualize_diff(self, trail_a, trail_b, output_file, title):
        """Generate visualization comparing two trail maps."""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))

        # Trail A
        im0 = axes[0, 0].imshow(trail_a, cmap='hot', interpolation='nearest', vmin=0, vmax=255)
        axes[0, 0].set_title('Python Reference', fontsize=12, fontweight='bold')
        axes[0, 0].axis('off')
        plt.colorbar(im0, ax=axes[0, 0], fraction=0.046, pad=0.04)

        # Trail B
        im1 = axes[0, 1].imshow(trail_b, cmap='hot', interpolation='nearest', vmin=0, vmax=255)
        axes[0, 1].set_title('RTL/FPGA', fontsize=12, fontweight='bold')
        axes[0, 1].axis('off')
        plt.colorbar(im1, ax=axes[0, 1], fraction=0.046, pad=0.04)

        # Absolute difference
        diff = np.abs(trail_a.astype(np.int16) - trail_b.astype(np.int16))
        im2 = axes[1, 0].imshow(diff, cmap='viridis', interpolation='nearest', vmin=0, vmax=20)
        axes[1, 0].set_title(f'Absolute Difference (max={diff.max()})', fontsize=12, fontweight='bold')
        axes[1, 0].axis('off')
        plt.colorbar(im2, ax=axes[1, 0], fraction=0.046, pad=0.04)

        # Difference histogram
        axes[1, 1].hist(diff.flatten(), bins=50, edgecolor='black', alpha=0.7)
        axes[1, 1].set_xlabel('Absolute Difference', fontsize=10)
        axes[1, 1].set_ylabel('Pixel Count', fontsize=10)
        axes[1, 1].set_title('Difference Histogram', fontsize=12, fontweight='bold')
        axes[1, 1].grid(True, alpha=0.3)
        axes[1, 1].set_yscale('log')

        fig.suptitle(title, fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()


def main():
    parser = argparse.ArgumentParser(description='Regression test suite for Slime Simulator')
    parser.add_argument('--reference-only', action='store_true',
                       help='Generate Python reference only (no comparison)')
    parser.add_argument('--iterations', type=str, default='1,5,10,20,50,100',
                       help='Comma-separated iteration points (default: 1,5,10,20,50,100)')
    parser.add_argument('--output-dir', default='test_results',
                       help='Output directory for results')
    parser.add_argument('--visualize', action='store_true', default=True,
                       help='Generate visualizations (default: True)')
    parser.add_argument('--no-visualize', action='store_false', dest='visualize',
                       help='Disable visualization generation')
    parser.add_argument('--rtl-sim-dir', help='RTL simulation results directory for comparison')
    parser.add_argument('--fpga-dir', help='FPGA capture directory for comparison')
    parser.add_argument('--threshold', type=float, default=90.0,
                       help='Acceptance threshold for FPGA comparison (default: 90.0)')

    args = parser.parse_args()

    # Parse iterations
    iterations = [int(x.strip()) for x in args.iterations.split(',')]

    # Create test suite
    test = RegressionTest(
        output_dir=args.output_dir,
        iterations=iterations,
        visualize=args.visualize
    )

    # Phase 1: Python reference
    test.run_python_reference()

    # Phase 2: RTL comparison (if requested)
    if args.rtl_sim_dir:
        test.compare_with_rtl_sim(args.rtl_sim_dir)

    # Phase 3: FPGA comparison (if requested)
    if args.fpga_dir:
        test.compare_with_fpga(args.fpga_dir, args.threshold)

    print("\n" + "="*80)
    print("Regression test complete!")
    print("="*80)
    print(f"Results saved to: {test.output_dir}")
    print("")


if __name__ == '__main__':
    main()
