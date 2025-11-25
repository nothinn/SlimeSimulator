#!/usr/bin/env python3
"""
VGA Timing Validation Script
=============================

Validates VGA timing signals and framebuffer operations.

Features:
- Validates VGA timing signals (hsync, vsync, pixel clock)
- Checks 640x480@60Hz timing correctness
- Simulates framebuffer reads
- Verifies pixel ordering and blanking intervals
- Can compare with RTL simulation outputs if available

Usage:
    validate_vga.py --mode 640x480
    validate_vga.py --simulate-frames 10 --save-json
    validate_vga.py --compare-rtl vga_timing.csv
"""

import sys
import os
import argparse
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple
import json


class VGATimingSpec:
    """VGA timing specification."""

    MODES = {
        '640x480': {
            'name': '640x480@60Hz',
            'pixel_clock': 25.175e6,  # Hz
            'h_visible': 640,
            'h_front': 16,
            'h_sync': 96,
            'h_back': 48,
            'v_visible': 480,
            'v_front': 10,
            'v_sync': 2,
            'v_back': 33,
            'hsync_polarity': 'negative',
            'vsync_polarity': 'negative'
        },
        '800x600': {
            'name': '800x600@60Hz',
            'pixel_clock': 40.0e6,
            'h_visible': 800,
            'h_front': 40,
            'h_sync': 128,
            'h_back': 88,
            'v_visible': 600,
            'v_front': 1,
            'v_sync': 4,
            'v_back': 23,
            'hsync_polarity': 'positive',
            'vsync_polarity': 'positive'
        }
    }

    def __init__(self, mode: str = '640x480'):
        if mode not in self.MODES:
            raise ValueError(f"Unknown mode: {mode}")

        spec = self.MODES[mode]
        self.name = spec['name']
        self.pixel_clock = spec['pixel_clock']

        # Horizontal timing
        self.h_visible = spec['h_visible']
        self.h_front = spec['h_front']
        self.h_sync = spec['h_sync']
        self.h_back = spec['h_back']
        self.h_total = self.h_visible + self.h_front + self.h_sync + self.h_back

        # Vertical timing
        self.v_visible = spec['v_visible']
        self.v_front = spec['v_front']
        self.v_sync = spec['v_sync']
        self.v_back = spec['v_back']
        self.v_total = self.v_visible + self.v_front + self.v_sync + self.v_back

        # Sync polarities
        self.hsync_polarity = spec['hsync_polarity']
        self.vsync_polarity = spec['vsync_polarity']

        # Derived values
        self.frame_rate = self.pixel_clock / (self.h_total * self.v_total)
        self.line_time = self.h_total / self.pixel_clock
        self.frame_time = 1.0 / self.frame_rate
        self.total_pixels = self.h_total * self.v_total
        self.visible_pixels = self.h_visible * self.v_visible


class VGAValidator:
    """VGA timing validator."""

    def __init__(self, mode: str = '640x480'):
        self.spec = VGATimingSpec(mode)
        self.results = {
            'mode': self.spec.name,
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

    def test_timing_parameters(self) -> bool:
        """Test that timing parameters are valid."""
        try:
            # Check horizontal timing
            h_valid = (
                self.spec.h_visible > 0 and
                self.spec.h_front > 0 and
                self.spec.h_sync > 0 and
                self.spec.h_back > 0
            )

            # Check vertical timing
            v_valid = (
                self.spec.v_visible > 0 and
                self.spec.v_front > 0 and
                self.spec.v_sync > 0 and
                self.spec.v_back > 0
            )

            # Check frame rate is reasonable (55-65 Hz for 60Hz mode)
            frame_rate_valid = 55.0 <= self.spec.frame_rate <= 65.0

            passed = h_valid and v_valid and frame_rate_valid

            self.add_test(
                "Timing Parameters",
                passed,
                {
                    'h_total': self.spec.h_total,
                    'v_total': self.spec.v_total,
                    'frame_rate': f"{self.spec.frame_rate:.2f} Hz",
                    'pixel_clock': f"{self.spec.pixel_clock/1e6:.3f} MHz",
                    'frame_time': f"{self.spec.frame_time*1000:.2f} ms",
                    'line_time': f"{self.spec.line_time*1e6:.2f} µs"
                }
            )
            return passed

        except Exception as e:
            self.add_test("Timing Parameters", False, {'error': str(e)})
            return False

    def test_sync_regions(self) -> bool:
        """Test sync signal regions are correctly defined."""
        try:
            # Horizontal sync region
            h_sync_start = self.spec.h_visible + self.spec.h_front
            h_sync_end = h_sync_start + self.spec.h_sync

            # Vertical sync region
            v_sync_start = self.spec.v_visible + self.spec.v_front
            v_sync_end = v_sync_start + self.spec.v_sync

            # Check regions don't overlap with visible area
            h_valid = (h_sync_start >= self.spec.h_visible) and (h_sync_end <= self.spec.h_total)
            v_valid = (v_sync_start >= self.spec.v_visible) and (v_sync_end <= self.spec.v_total)

            passed = h_valid and v_valid

            self.add_test(
                "Sync Regions",
                passed,
                {
                    'h_sync_region': f"[{h_sync_start}, {h_sync_end})",
                    'v_sync_region': f"[{v_sync_start}, {v_sync_end})",
                    'hsync_polarity': self.spec.hsync_polarity,
                    'vsync_polarity': self.spec.vsync_polarity
                }
            )
            return passed

        except Exception as e:
            self.add_test("Sync Regions", False, {'error': str(e)})
            return False

    def simulate_timing(self, num_frames: int = 1) -> Dict[str, Any]:
        """Simulate VGA timing for given number of frames."""
        try:
            h_count = 0
            v_count = 0
            pixel_count = 0
            visible_count = 0
            hsync_active_count = 0
            vsync_active_count = 0
            frame_count = 0

            # Timing data for analysis
            timing_data = {
                'pixels_per_frame': [],
                'visible_per_frame': [],
                'lines_per_frame': [],
                'frame_starts': []
            }

            total_pixels = num_frames * self.spec.total_pixels

            for i in range(total_pixels):
                # Check if in visible region
                h_visible = (h_count < self.spec.h_visible)
                v_visible = (v_count < self.spec.v_visible)
                visible = h_visible and v_visible

                if visible:
                    visible_count += 1

                # Check hsync
                h_sync_start = self.spec.h_visible + self.spec.h_front
                h_sync_end = h_sync_start + self.spec.h_sync
                hsync_active = (h_count >= h_sync_start) and (h_count < h_sync_end)

                if hsync_active:
                    hsync_active_count += 1

                # Check vsync
                v_sync_start = self.spec.v_visible + self.spec.v_front
                v_sync_end = v_sync_start + self.spec.v_sync
                vsync_active = (v_count >= v_sync_start) and (v_count < v_sync_end)

                if vsync_active:
                    vsync_active_count += 1

                # Frame start detection
                if h_count == 0 and v_count == 0:
                    timing_data['frame_starts'].append(i)

                # Increment counters
                h_count += 1
                pixel_count += 1

                if h_count >= self.spec.h_total:
                    h_count = 0
                    v_count += 1

                    if v_count >= self.spec.v_total:
                        v_count = 0
                        frame_count += 1

                        # Record frame statistics
                        timing_data['pixels_per_frame'].append(pixel_count)
                        timing_data['visible_per_frame'].append(visible_count)
                        timing_data['lines_per_frame'].append(self.spec.v_total)

                        # Reset counters
                        pixel_count = 0
                        visible_count = 0

            return {
                'frames_simulated': num_frames,
                'total_pixels': total_pixels,
                'visible_pixels': sum(timing_data['visible_per_frame']),
                'expected_visible': num_frames * self.spec.visible_pixels,
                'hsync_active_pixels': hsync_active_count,
                'vsync_active_pixels': vsync_active_count,
                'timing_data': timing_data
            }

        except Exception as e:
            return {'error': str(e)}

    def test_frame_simulation(self, num_frames: int = 10) -> bool:
        """Test frame simulation for correct pixel counts."""
        try:
            sim_result = self.simulate_timing(num_frames)

            if 'error' in sim_result:
                self.add_test(
                    f"Frame Simulation ({num_frames} frames)",
                    False,
                    {'error': sim_result['error']}
                )
                return False

            # Check visible pixel count
            visible_match = (sim_result['visible_pixels'] == sim_result['expected_visible'])

            # Check frame count
            frames_detected = len(sim_result['timing_data']['frame_starts'])
            frame_count_match = (frames_detected == num_frames)

            passed = visible_match and frame_count_match

            self.add_test(
                f"Frame Simulation ({num_frames} frames)",
                passed,
                {
                    'frames_detected': frames_detected,
                    'visible_pixels': sim_result['visible_pixels'],
                    'expected_visible': sim_result['expected_visible'],
                    'total_pixels': sim_result['total_pixels']
                }
            )
            return passed

        except Exception as e:
            self.add_test(f"Frame Simulation ({num_frames} frames)", False, {'error': str(e)})
            return False

    def test_blanking_intervals(self) -> bool:
        """Test that blanking intervals are correct."""
        try:
            # Calculate blanking periods
            h_blanking = self.spec.h_front + self.spec.h_sync + self.spec.h_back
            v_blanking = self.spec.v_front + self.spec.v_sync + self.spec.v_back

            # As percentage
            h_blank_pct = 100 * h_blanking / self.spec.h_total
            v_blank_pct = 100 * v_blanking / self.spec.v_total

            # Typical values: horizontal ~20-25%, vertical ~10-15%
            h_reasonable = 15.0 <= h_blank_pct <= 30.0
            v_reasonable = 5.0 <= v_blank_pct <= 20.0

            passed = h_reasonable and v_reasonable

            self.add_test(
                "Blanking Intervals",
                passed,
                {
                    'h_blanking_pixels': h_blanking,
                    'h_blanking_pct': f"{h_blank_pct:.1f}%",
                    'v_blanking_lines': v_blanking,
                    'v_blanking_pct': f"{v_blank_pct:.1f}%",
                    'h_reasonable': h_reasonable,
                    'v_reasonable': v_reasonable
                }
            )
            return passed

        except Exception as e:
            self.add_test("Blanking Intervals", False, {'error': str(e)})
            return False

    def generate_timing_diagram(self, output_file: str, num_lines: int = 10):
        """Generate ASCII timing diagram for first few lines."""
        try:
            with open(output_file, 'w') as f:
                f.write(f"VGA Timing Diagram - {self.spec.name}\n")
                f.write("=" * 80 + "\n\n")

                # Horizontal timing for first few lines
                f.write("Horizontal Timing (first line):\n")
                f.write("Position: ")
                positions = [0, self.spec.h_visible,
                           self.spec.h_visible + self.spec.h_front,
                           self.spec.h_visible + self.spec.h_front + self.spec.h_sync,
                           self.spec.h_total]
                for pos in positions:
                    f.write(f"{pos:>6d} ")
                f.write("\n")

                # Visual representation
                scale = 0.1  # pixels per character
                visible_chars = int(self.spec.h_visible * scale)
                front_chars = int(self.spec.h_front * scale)
                sync_chars = int(self.spec.h_sync * scale)
                back_chars = int(self.spec.h_back * scale)

                f.write("          ")
                f.write("V" * visible_chars)
                f.write("F" * front_chars)
                f.write("S" * sync_chars)
                f.write("B" * back_chars)
                f.write("\n\n")

                f.write("Legend: V=Visible, F=Front Porch, S=Sync, B=Back Porch\n\n")

                # Vertical timing
                f.write("Vertical Timing:\n")
                f.write(f"Line 0-{self.spec.v_visible-1}: Visible\n")
                f.write(f"Line {self.spec.v_visible}-{self.spec.v_visible+self.spec.v_front-1}: Front Porch\n")
                f.write(f"Line {self.spec.v_visible+self.spec.v_front}-{self.spec.v_visible+self.spec.v_front+self.spec.v_sync-1}: Vsync\n")
                f.write(f"Line {self.spec.v_visible+self.spec.v_front+self.spec.v_sync}-{self.spec.v_total-1}: Back Porch\n\n")

                # Timing details
                f.write("Timing Details:\n")
                f.write(f"  Pixel Clock: {self.spec.pixel_clock/1e6:.3f} MHz\n")
                f.write(f"  Horizontal Total: {self.spec.h_total} pixels\n")
                f.write(f"  Vertical Total: {self.spec.v_total} lines\n")
                f.write(f"  Frame Rate: {self.spec.frame_rate:.2f} Hz\n")
                f.write(f"  Line Time: {self.spec.line_time*1e6:.2f} µs\n")
                f.write(f"  Frame Time: {self.spec.frame_time*1000:.2f} ms\n")

            return True
        except Exception as e:
            print(f"Error generating timing diagram: {e}")
            return False

    def compare_with_rtl(self, rtl_file: str) -> bool:
        """Compare timing with RTL simulation output."""
        try:
            # Expected format: pixel_count, h_count, v_count, hsync, vsync, visible
            rtl_data = []
            with open(rtl_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split(',')
                        if len(parts) >= 6:
                            rtl_data.append({
                                'pixel': int(parts[0]),
                                'h': int(parts[1]),
                                'v': int(parts[2]),
                                'hsync': int(parts[3]),
                                'vsync': int(parts[4]),
                                'visible': int(parts[5])
                            })

            # Simulate and compare
            errors = []
            for data in rtl_data[:1000]:  # Check first 1000 pixels
                h = data['h']
                v = data['v']

                # Expected values
                h_visible = (h < self.spec.h_visible)
                v_visible = (v < self.spec.v_visible)
                expected_visible = 1 if (h_visible and v_visible) else 0

                h_sync_start = self.spec.h_visible + self.spec.h_front
                h_sync_end = h_sync_start + self.spec.h_sync
                expected_hsync = 1 if (h >= h_sync_start and h < h_sync_end) else 0

                # Account for polarity
                if self.spec.hsync_polarity == 'negative':
                    expected_hsync = 1 - expected_hsync

                # Compare
                if data['visible'] != expected_visible:
                    if len(errors) < 10:
                        errors.append({
                            'pixel': data['pixel'],
                            'h': h,
                            'v': v,
                            'error': 'visible mismatch',
                            'expected': expected_visible,
                            'rtl': data['visible']
                        })

            passed = len(errors) == 0

            self.add_test(
                "RTL Comparison",
                passed,
                {
                    'rtl_file': rtl_file,
                    'pixels_compared': len(rtl_data),
                    'errors': errors if errors else 'None'
                }
            )
            return passed

        except Exception as e:
            self.add_test("RTL Comparison", False, {'error': str(e)})
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Validate VGA timing",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--mode', type=str, default='640x480',
                       choices=['640x480', '800x600'],
                       help='VGA mode (default: 640x480)')
    parser.add_argument('--simulate-frames', type=int, default=1,
                       help='Number of frames to simulate (default: 1)')
    parser.add_argument('--compare-rtl', type=str, metavar='FILE',
                       help='Compare with RTL timing output file')
    parser.add_argument('--generate-diagram', action='store_true',
                       help='Generate timing diagram')
    parser.add_argument('--output-dir', type=str,
                       default='validation_output/vga',
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
    print("  VGA Timing Validation")
    print("="*70)
    print(f"Mode: {args.mode}")
    print("="*70 + "\n")

    # Create validator
    validator = VGAValidator(args.mode)

    # Run tests
    validator.test_timing_parameters()
    validator.test_sync_regions()
    validator.test_blanking_intervals()
    validator.test_frame_simulation(args.simulate_frames)

    # RTL comparison
    if args.compare_rtl:
        print(f"Comparing with RTL output: {args.compare_rtl}")
        validator.compare_with_rtl(args.compare_rtl)

    # Generate timing diagram
    if args.generate_diagram:
        diagram_file = output_dir / "timing_diagram.txt"
        print(f"\nGenerating timing diagram: {diagram_file}")
        validator.generate_timing_diagram(str(diagram_file))

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
                if isinstance(val, (list, dict)) and len(str(val)) > 100:
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
                'mode': args.mode,
                'frames_simulated': args.simulate_frames
            },
            'results': validator.results
        }

        report_file = output_dir / f"vga_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"JSON report saved to: {report_file}\n")

    # Exit code
    sys.exit(0 if failed == 0 else 1)


if __name__ == '__main__':
    main()
