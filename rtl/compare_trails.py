#!/usr/bin/env python3
"""
Trail Map Comparison Framework

This script compares trail maps from Python reference and RTL implementation.
It performs pixel-by-pixel comparison and generates detailed statistics and
visualizations to identify where and how the implementations diverge.

Usage:
    python compare_trails.py \\
        --reference regression_test_results/reference \\
        --rtl regression_test_results/rtl_capture \\
        --output regression_test_results/comparison_report.csv
"""

import sys
import argparse
import csv
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, List


class TrailComparator:
    """
    Compares trail maps between reference and RTL implementations.
    """

    def __init__(self, width: int = 160, height: int = 120):
        """
        Initialize comparator.

        Args:
            width: Trail map width
            height: Trail map height
        """
        self.width = width
        self.height = height
        self.size = width * height

    def load_trail_map(self, filename: str) -> np.ndarray:
        """
        Load trail map from binary file.

        Args:
            filename: Path to .bin file

        Returns:
            Trail map as numpy array (height, width)

        Raises:
            ValueError: If file size doesn't match expected dimensions
        """
        data = np.fromfile(filename, dtype=np.uint8)

        if len(data) != self.size:
            raise ValueError(
                f"File {filename} has {len(data)} bytes, "
                f"expected {self.size} ({self.width}x{self.height})"
            )

        return data.reshape(self.height, self.width)

    def compare_maps(
        self,
        reference: np.ndarray,
        rtl: np.ndarray
    ) -> Dict[str, float]:
        """
        Compare two trail maps and compute statistics.

        Args:
            reference: Reference trail map
            rtl: RTL trail map

        Returns:
            Dictionary with comparison metrics:
                - total_pixels: Total pixels in map
                - matching_pixels: Number of exactly matching pixels
                - match_percentage: Percentage of matching pixels
                - max_diff: Maximum absolute difference
                - mean_diff: Mean absolute difference (over all pixels)
                - rms_diff: RMS difference
                - nonzero_ref: Number of non-zero pixels in reference
                - nonzero_rtl: Number of non-zero pixels in RTL
                - nonzero_match: Number of matching non-zero pixels
        """
        # Ensure same shape
        assert reference.shape == rtl.shape, "Trail maps have different shapes"

        # Compute differences
        diff = reference.astype(np.int16) - rtl.astype(np.int16)
        abs_diff = np.abs(diff)

        # Statistics
        total_pixels = reference.size
        matching_pixels = np.count_nonzero(abs_diff == 0)
        match_percentage = 100.0 * matching_pixels / total_pixels

        max_diff = np.max(abs_diff)
        mean_diff = np.mean(abs_diff)
        rms_diff = np.sqrt(np.mean(diff.astype(np.float32) ** 2))

        nonzero_ref = np.count_nonzero(reference)
        nonzero_rtl = np.count_nonzero(rtl)

        # Matching non-zero pixels
        nonzero_match = np.count_nonzero((reference > 0) & (reference == rtl))

        return {
            'total_pixels': total_pixels,
            'matching_pixels': matching_pixels,
            'match_percentage': match_percentage,
            'max_diff': float(max_diff),
            'mean_diff': float(mean_diff),
            'rms_diff': float(rms_diff),
            'nonzero_ref': nonzero_ref,
            'nonzero_rtl': nonzero_rtl,
            'nonzero_match': nonzero_match
        }

    def generate_diff_visualization(
        self,
        reference: np.ndarray,
        rtl: np.ndarray,
        output_file: str,
        scale: int = 4
    ):
        """
        Generate visual diff image (requires PIL/Pillow).

        Args:
            reference: Reference trail map
            rtl: RTL trail map
            output_file: Output PNG file path
            scale: Upscaling factor for visibility

        Raises:
            ImportError: If PIL not available
        """
        try:
            from PIL import Image
        except ImportError:
            print("Warning: PIL/Pillow not available, skipping visualization")
            return

        # Compute differences
        diff = reference.astype(np.int16) - rtl.astype(np.int16)
        abs_diff = np.abs(diff)

        # Create RGB image showing:
        # - Green: Matching pixels
        # - Red: Pixels only in reference
        # - Blue: Pixels only in RTL
        # - Yellow: Pixels in both but different values
        height, width = reference.shape
        img = np.zeros((height, width, 3), dtype=np.uint8)

        # Matching pixels (green)
        matching = (reference == rtl) & (reference > 0)
        img[matching, 1] = reference[matching]

        # Only in reference (red)
        ref_only = (reference > rtl)
        img[ref_only, 0] = abs_diff[ref_only]

        # Only in RTL (blue)
        rtl_only = (rtl > reference)
        img[rtl_only, 2] = abs_diff[rtl_only]

        # Scale up for visibility
        if scale > 1:
            img_pil = Image.fromarray(img)
            img_pil = img_pil.resize(
                (width * scale, height * scale),
                Image.NEAREST
            )
            img_pil.save(output_file)
        else:
            Image.fromarray(img).save(output_file)

    def compare_iterations(
        self,
        ref_dir: str,
        rtl_dir: str,
        iterations: List[int],
        threshold_percentage: float = 95.0
    ) -> Tuple[List[Dict], bool]:
        """
        Compare trail maps across multiple iterations.

        Args:
            ref_dir: Directory with reference trail maps
            rtl_dir: Directory with RTL trail maps
            iterations: List of iteration numbers to compare
            threshold_percentage: Pass threshold (% matching pixels)

        Returns:
            Tuple of (results list, overall pass/fail)
            results: List of dicts with comparison results for each iteration
            pass_fail: True if all iterations pass threshold
        """
        ref_path = Path(ref_dir)
        rtl_path = Path(rtl_dir)

        results = []
        all_pass = True

        for iter_num in sorted(iterations):
            ref_file = ref_path / f"trail_iter_{iter_num:03d}.bin"
            rtl_file = rtl_path / f"trail_iter_{iter_num:03d}.bin"

            # Check if files exist
            if not ref_file.exists():
                print(f"Warning: Reference file not found: {ref_file}")
                continue

            if not rtl_file.exists():
                print(f"Warning: RTL file not found: {rtl_file}")
                continue

            # Load maps
            try:
                ref_map = self.load_trail_map(str(ref_file))
                rtl_map = self.load_trail_map(str(rtl_file))
            except Exception as e:
                print(f"Error loading maps for iteration {iter_num}: {e}")
                continue

            # Compare
            stats = self.compare_maps(ref_map, rtl_map)
            stats['iteration'] = iter_num

            # Pass/fail
            passed = stats['match_percentage'] >= threshold_percentage
            stats['status'] = 'PASS' if passed else 'FAIL'

            if not passed:
                all_pass = False

            results.append(stats)

        return results, all_pass


def print_comparison_table(results: List[Dict]):
    """
    Print comparison results as formatted table.

    Args:
        results: List of comparison result dictionaries
    """
    print("\n" + "="*90)
    print("Trail Map Comparison Results")
    print("="*90)

    # Header
    print(f"{'Iter':>4} | {'Written':>8} | {'Match':>7} | "
          f"{'MaxDiff':>7} | {'MeanDiff':>8} | {'RMS':>7} | {'Status':>6}")
    print("-"*90)

    # Rows
    for r in results:
        print(f"{r['iteration']:4d} | "
              f"{r['nonzero_ref']:8d} | "
              f"{r['match_percentage']:6.2f}% | "
              f"{r['max_diff']:7.1f} | "
              f"{r['mean_diff']:8.3f} | "
              f"{r['rms_diff']:7.3f} | "
              f"{r['status']:>6}")

    print("="*90)


def save_comparison_csv(results: List[Dict], output_file: str):
    """
    Save comparison results to CSV file.

    Args:
        results: List of comparison result dictionaries
        output_file: Output CSV file path
    """
    if not results:
        print("No results to save")
        return

    # Define column order
    columns = [
        'iteration',
        'total_pixels',
        'nonzero_ref',
        'nonzero_rtl',
        'matching_pixels',
        'match_percentage',
        'max_diff',
        'mean_diff',
        'rms_diff',
        'nonzero_match',
        'status'
    ]

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()

        for r in results:
            # Filter to only include defined columns
            row = {k: r[k] for k in columns if k in r}
            writer.writerow(row)

    print(f"\nComparison results saved to: {output_path.absolute()}")


def generate_detailed_analysis(
    results: List[Dict],
    ref_dir: str,
    rtl_dir: str,
    output_file: str,
    comparator: TrailComparator
):
    """
    Generate detailed analysis text file.

    Args:
        results: Comparison results
        ref_dir: Reference directory
        rtl_dir: RTL directory
        output_file: Output text file path
        comparator: TrailComparator instance
    """
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("Detailed Trail Map Comparison Analysis\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"Reference Directory: {Path(ref_dir).absolute()}\n")
        f.write(f"RTL Directory:       {Path(rtl_dir).absolute()}\n")
        f.write(f"Resolution:          {comparator.width}x{comparator.height}\n")
        f.write(f"Total Pixels:        {comparator.size}\n\n")

        # Summary statistics
        if results:
            f.write("Summary Statistics:\n")
            f.write("-" * 80 + "\n")

            iterations = [r['iteration'] for r in results]
            match_pcts = [r['match_percentage'] for r in results]
            max_diffs = [r['max_diff'] for r in results]
            mean_diffs = [r['mean_diff'] for r in results]

            f.write(f"  Iterations tested:     {len(results)}\n")
            f.write(f"  Iteration range:       {min(iterations)} - {max(iterations)}\n")
            f.write(f"  Match % range:         {min(match_pcts):.2f}% - {max(match_pcts):.2f}%\n")
            f.write(f"  Average match %:       {np.mean(match_pcts):.2f}%\n")
            f.write(f"  Max diff range:        {min(max_diffs):.1f} - {max(max_diffs):.1f}\n")
            f.write(f"  Mean diff range:       {min(mean_diffs):.3f} - {max(mean_diffs):.3f}\n\n")

            # Pass/fail summary
            pass_count = sum(1 for r in results if r['status'] == 'PASS')
            fail_count = len(results) - pass_count
            f.write(f"  Tests passed:          {pass_count}/{len(results)}\n")
            f.write(f"  Tests failed:          {fail_count}/{len(results)}\n\n")

        # Per-iteration details
        f.write("Per-Iteration Analysis:\n")
        f.write("=" * 80 + "\n")

        for r in results:
            f.write(f"\nIteration {r['iteration']:3d}  [{r['status']}]\n")
            f.write("-" * 80 + "\n")
            f.write(f"  Reference pixels written:  {r['nonzero_ref']:8d}\n")
            f.write(f"  RTL pixels written:        {r['nonzero_rtl']:8d}\n")
            f.write(f"  Exactly matching pixels:   {r['matching_pixels']:8d}  ({r['match_percentage']:.2f}%)\n")
            f.write(f"  Matching non-zero pixels:  {r['nonzero_match']:8d}\n")
            f.write(f"  Maximum difference:        {r['max_diff']:8.1f}\n")
            f.write(f"  Mean difference:           {r['mean_diff']:8.3f}\n")
            f.write(f"  RMS difference:            {r['rms_diff']:8.3f}\n")

        # Trend analysis
        if len(results) > 1:
            f.write("\n" + "=" * 80 + "\n")
            f.write("Trend Analysis:\n")
            f.write("=" * 80 + "\n")

            # Check if divergence increases over time
            match_pcts = [r['match_percentage'] for r in results]
            if len(match_pcts) > 2:
                # Simple linear trend
                x = np.arange(len(match_pcts))
                coeffs = np.polyfit(x, match_pcts, 1)
                trend = "decreasing" if coeffs[0] < -0.1 else ("increasing" if coeffs[0] > 0.1 else "stable")

                f.write(f"\n  Match percentage trend:  {trend}\n")
                if trend == "decreasing":
                    f.write("  WARNING: RTL diverges more over time!\n")
                elif trend == "stable":
                    f.write("  GOOD: Divergence remains stable across iterations.\n")

    print(f"Detailed analysis saved to: {output_path.absolute()}")


def main():
    parser = argparse.ArgumentParser(
        description='Compare trail maps between Python reference and RTL',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic comparison
  python compare_trails.py \\
      --reference regression_test_results/reference \\
      --rtl regression_test_results/rtl_capture

  # Custom threshold and output
  python compare_trails.py \\
      --reference ref/ --rtl rtl/ \\
      --threshold 99.0 \\
      --output results/comparison.csv

  # Generate visualizations
  python compare_trails.py --reference ref/ --rtl rtl/ --visualize
        """
    )

    parser.add_argument('--reference', required=True,
                        help='Directory with reference trail maps')
    parser.add_argument('--rtl', required=True,
                        help='Directory with RTL trail maps')
    parser.add_argument('--iterations', type=str, default='1,5,10,20',
                        help='Comma-separated iterations to compare (default: 1,5,10,20)')
    parser.add_argument('--width', type=int, default=160,
                        help='Trail map width (default: 160)')
    parser.add_argument('--height', type=int, default=120,
                        help='Trail map height (default: 120)')
    parser.add_argument('--output', type=str,
                        default='regression_test_results/comparison_report.csv',
                        help='Output CSV file')
    parser.add_argument('--detailed-output', type=str,
                        default='regression_test_results/detailed_analysis.txt',
                        help='Detailed analysis text file')
    parser.add_argument('--threshold', type=float, default=95.0,
                        help='Pass threshold percentage (default: 95.0)')
    parser.add_argument('--visualize', action='store_true',
                        help='Generate diff visualization images (requires PIL)')

    args = parser.parse_args()

    # Parse iterations
    try:
        iterations = [int(x.strip()) for x in args.iterations.split(',')]
    except ValueError:
        print(f"Error: Invalid iterations format: {args.iterations}")
        sys.exit(1)

    # Create comparator
    comparator = TrailComparator(width=args.width, height=args.height)

    # Compare iterations
    print(f"Comparing trail maps...")
    print(f"  Reference: {args.reference}")
    print(f"  RTL:       {args.rtl}")
    print(f"  Iterations: {iterations}")

    try:
        results, all_pass = comparator.compare_iterations(
            ref_dir=args.reference,
            rtl_dir=args.rtl,
            iterations=iterations,
            threshold_percentage=args.threshold
        )

        if not results:
            print("Error: No results generated (check input directories)")
            sys.exit(1)

        # Print table
        print_comparison_table(results)

        # Save CSV
        save_comparison_csv(results, args.output)

        # Generate detailed analysis
        generate_detailed_analysis(
            results,
            args.reference,
            args.rtl,
            args.detailed_output,
            comparator
        )

        # Generate visualizations if requested
        if args.visualize:
            viz_dir = Path(args.output).parent / "visualizations"
            viz_dir.mkdir(parents=True, exist_ok=True)

            print(f"\nGenerating visualizations...")
            for iter_num in iterations:
                ref_file = Path(args.reference) / f"trail_iter_{iter_num:03d}.bin"
                rtl_file = Path(args.rtl) / f"trail_iter_{iter_num:03d}.bin"

                if ref_file.exists() and rtl_file.exists():
                    ref_map = comparator.load_trail_map(str(ref_file))
                    rtl_map = comparator.load_trail_map(str(rtl_file))

                    viz_file = viz_dir / f"diff_iter_{iter_num:03d}.png"
                    comparator.generate_diff_visualization(
                        ref_map, rtl_map, str(viz_file), scale=4
                    )
                    print(f"  {viz_file}")

        # Overall status
        print("\n" + "="*90)
        if all_pass:
            print("OVERALL STATUS: PASS")
            print(f"All iterations met {args.threshold}% match threshold")
        else:
            print("OVERALL STATUS: FAIL")
            print(f"Some iterations did not meet {args.threshold}% match threshold")
        print("="*90)

        sys.exit(0 if all_pass else 1)

    except Exception as e:
        print(f"\nError during comparison: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
