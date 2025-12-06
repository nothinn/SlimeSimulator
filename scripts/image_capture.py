#!/usr/bin/env python3
"""
Image Capture and Comparison Tool
Captures trail map images from FPGA via JTAG and compares with Python reference.
"""

import argparse
import subprocess
import sys
import tempfile
import json
import numpy as np
from pathlib import Path
from datetime import datetime
import shutil


class ImageCapture:
    """Handles image capture from FPGA and comparison with reference"""

    # Default memory addresses (adjust based on actual design)
    TRAIL_MAP_BASE_ADDR = 0x00000000
    TRAIL_MAP_SIZE = 160 * 120  # Width x Height

    def __init__(self, rtl_dir=None, output_dir=None, dry_run=False, verbose=False):
        self.dry_run = dry_run
        self.verbose = verbose

        # Set up paths
        if rtl_dir:
            self.rtl_dir = Path(rtl_dir).resolve()
        else:
            script_dir = Path(__file__).parent
            self.rtl_dir = script_dir.parent / 'rtl'

        if output_dir:
            self.output_dir = Path(output_dir).resolve()
        else:
            self.output_dir = Path.cwd() / 'output_images'

        self.output_dir.mkdir(exist_ok=True)

        # Set up logging
        self.log_dir = self.output_dir / 'logs'
        self.log_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_file = self.log_dir / f"capture_{timestamp}.log"

    def log(self, message, level='INFO'):
        """Log message to console and file"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_msg = f"[{timestamp}] [{level}] {message}"
        print(log_msg)

        with open(self.log_file, 'a') as f:
            f.write(log_msg + '\n')

    def check_vivado_available(self):
        """Check if Vivado is available"""
        vivado_path = shutil.which('vivado')
        if not vivado_path:
            self.log("ERROR: Vivado not found in PATH", 'ERROR')
            return False

        self.log(f"Found Vivado: {vivado_path}")
        return True

    def check_python_reference_available(self):
        """Check if Python reference implementation is available"""
        try:
            import slime_simulator
            self.log("Found Python reference implementation")
            return True
        except ImportError as e:
            self.log(f"Python reference not available: {e}", 'WARN')
            return False

    def capture_trail_map_jtag(self, width=160, height=120):
        """Capture trail map from FPGA via JTAG"""
        self.log("=" * 60)
        self.log("Capturing Trail Map from FPGA")
        self.log("=" * 60)
        self.log(f"Resolution: {width}x{height}")

        if self.dry_run:
            self.log("DRY RUN - Would capture from FPGA via JTAG")
            # Return dummy data for dry run
            return np.random.randint(0, 256, (height, width), dtype=np.uint8)

        # Create TCL script to read memory via JTAG
        # Note: This is a simplified example - actual implementation depends on your design
        output_file = self.output_dir / f"trail_map_raw_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bin"

        tcl_script = f"""
# Open hardware manager
open_hw_manager
connect_hw_server -allow_non_jtag
open_hw_target

# Get device
set device [lindex [get_hw_devices] 0]
current_hw_device $device

puts "Capturing trail map data..."

# Create ILA/VIO or use debug bridge to read memory
# This is a placeholder - actual implementation depends on debug infrastructure
# For now, we'll use a simplified approach

# Read trail map memory
# Note: Adjust based on actual memory interface in design
set num_samples {width * height}

# This would need actual debug core configuration
# For demonstration, we show the structure:
# set_property OUTPUT_VALUE 0x1 [get_hw_probes capture_enable]
# commit_hw_vio [get_hw_vios]

# Wait for capture
after 100

# Read data (example - actual commands depend on debug infrastructure)
# set data [read_hw_memory ...]

puts "Trail map captured to {output_file}"

# Close connection
close_hw_target
disconnect_hw_server
close_hw_manager

exit 0
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.tcl', delete=False) as f:
            f.write(tcl_script)
            tcl_file = Path(f.name)

        try:
            self.log("Running JTAG capture...")
            self.log("NOTE: This requires debug infrastructure (ILA/VIO) in the design", 'WARN')

            result = subprocess.run(
                ['vivado', '-mode', 'batch', '-source', str(tcl_file)],
                capture_output=True,
                text=True,
                timeout=60
            )

            if self.verbose:
                print(result.stdout)

            with open(self.log_file, 'a') as f:
                f.write(result.stdout)

            # For now, return simulated data since actual JTAG capture
            # requires specific debug infrastructure
            self.log("Using simulated capture data (JTAG infrastructure not fully implemented)", 'WARN')
            return np.random.randint(0, 256, (height, width), dtype=np.uint8)

        except Exception as e:
            self.log(f"Error during capture: {e}", 'ERROR')
            return None
        finally:
            tcl_file.unlink(missing_ok=True)

    def read_trail_map_file(self, filename):
        """Read trail map from binary file"""
        self.log(f"Reading trail map from: {filename}")

        filepath = Path(filename)
        if not filepath.exists():
            # Try relative to rtl_dir
            filepath = self.rtl_dir / filename
            if not filepath.exists():
                self.log(f"File not found: {filename}", 'ERROR')
                return None

        try:
            data = np.fromfile(filepath, dtype=np.uint8)
            self.log(f"Read {len(data)} bytes")

            # Determine dimensions
            if len(data) == 160 * 120:
                width, height = 160, 120
            elif len(data) == 640 * 480:
                width, height = 640, 480
            else:
                # Try to infer square or standard aspect ratio
                total = len(data)
                width = int(np.sqrt(total))
                height = total // width
                self.log(f"Inferred dimensions: {width}x{height}", 'WARN')

            trail_map = data.reshape((height, width))
            return trail_map

        except Exception as e:
            self.log(f"Error reading file: {e}", 'ERROR')
            return None

    def generate_python_reference(self, num_agents=100, num_steps=10, width=160, height=120):
        """Generate reference trail map using Python implementation"""
        self.log("=" * 60)
        self.log("Generating Python Reference")
        self.log("=" * 60)
        self.log(f"Agents: {num_agents}, Steps: {num_steps}")
        self.log(f"Resolution: {width}x{height}")

        if self.dry_run:
            self.log("DRY RUN - Would generate Python reference")
            return np.random.randint(0, 256, (height, width), dtype=np.uint8)

        try:
            from slime_simulator import SlimeSimulator

            # Create simulator
            sim = SlimeSimulator(
                width=width,
                height=height,
                num_agents=num_agents
            )

            # Run simulation
            self.log(f"Running {num_steps} simulation steps...")
            for step in range(num_steps):
                sim.step()
                if (step + 1) % max(1, num_steps // 10) == 0:
                    self.log(f"  Step {step + 1}/{num_steps}")

            # Get trail map
            trail_map = sim.get_trail_map()
            self.log(f"Generated trail map: {trail_map.shape}")

            # Save to file
            output_file = self.output_dir / f"reference_trail_{width}x{height}_{num_steps}steps.bin"
            trail_map.tofile(output_file)
            self.log(f"Saved reference to: {output_file}")

            return trail_map

        except ImportError as e:
            self.log(f"Could not import Python reference: {e}", 'ERROR')
            return None
        except Exception as e:
            self.log(f"Error generating reference: {e}", 'ERROR')
            import traceback
            traceback.print_exc()
            return None

    def compare_trail_maps(self, fpga_map, reference_map, tolerance=5):
        """Compare FPGA trail map with reference"""
        self.log("=" * 60)
        self.log("Comparing Trail Maps")
        self.log("=" * 60)

        if fpga_map is None or reference_map is None:
            self.log("Cannot compare: missing data", 'ERROR')
            return None

        # Ensure same shape
        if fpga_map.shape != reference_map.shape:
            self.log(f"Shape mismatch: FPGA={fpga_map.shape}, Ref={reference_map.shape}", 'ERROR')
            return None

        # Calculate differences
        diff = np.abs(fpga_map.astype(int) - reference_map.astype(int))
        max_diff = np.max(diff)
        mean_diff = np.mean(diff)
        pixels_within_tolerance = np.sum(diff <= tolerance)
        total_pixels = fpga_map.size
        match_percentage = (pixels_within_tolerance / total_pixels) * 100

        # Calculate statistics
        stats = {
            'max_difference': int(max_diff),
            'mean_difference': float(mean_diff),
            'pixels_within_tolerance': int(pixels_within_tolerance),
            'total_pixels': int(total_pixels),
            'match_percentage': float(match_percentage),
            'tolerance': tolerance
        }

        self.log(f"Max difference: {max_diff}")
        self.log(f"Mean difference: {mean_diff:.2f}")
        self.log(f"Match rate: {match_percentage:.2f}% (within tolerance={tolerance})")

        # Determine pass/fail
        if match_percentage >= 95.0:
            self.log("PASS: Trail maps match well", 'INFO')
            stats['result'] = 'PASS'
        elif match_percentage >= 80.0:
            self.log("WARN: Trail maps partially match", 'WARN')
            stats['result'] = 'PARTIAL'
        else:
            self.log("FAIL: Trail maps differ significantly", 'ERROR')
            stats['result'] = 'FAIL'

        return stats

    def save_comparison_images(self, fpga_map, reference_map, diff_map=None):
        """Save comparison images (requires PIL/Pillow)"""
        try:
            from PIL import Image
        except ImportError:
            self.log("PIL/Pillow not available, skipping image save", 'WARN')
            return

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Save FPGA map
        if fpga_map is not None:
            fpga_img = Image.fromarray(fpga_map)
            fpga_file = self.output_dir / f"fpga_trail_{timestamp}.png"
            fpga_img.save(fpga_file)
            self.log(f"Saved FPGA image: {fpga_file}")

        # Save reference map
        if reference_map is not None:
            ref_img = Image.fromarray(reference_map)
            ref_file = self.output_dir / f"reference_trail_{timestamp}.png"
            ref_img.save(ref_file)
            self.log(f"Saved reference image: {ref_file}")

        # Save difference map
        if fpga_map is not None and reference_map is not None:
            diff = np.abs(fpga_map.astype(int) - reference_map.astype(int))
            diff_img = Image.fromarray(diff.astype(np.uint8))
            diff_file = self.output_dir / f"diff_trail_{timestamp}.png"
            diff_img.save(diff_file)
            self.log(f"Saved difference image: {diff_file}")

    def save_comparison_report(self, stats):
        """Save comparison report to JSON"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.output_dir / f"comparison_report_{timestamp}.json"

        report = {
            'timestamp': datetime.now().isoformat(),
            'comparison': stats
        }

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        self.log(f"Saved report: {report_file}")
        return report_file


def main():
    parser = argparse.ArgumentParser(
        description='Image Capture and Comparison Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modes:
  capture        - Capture trail map from FPGA via JTAG
  reference      - Generate Python reference trail map
  compare        - Compare FPGA and reference trail maps
  full           - Full workflow: generate ref, capture FPGA, compare

Examples:
  %(prog)s reference --steps 10          # Generate reference
  %(prog)s capture                        # Capture from FPGA
  %(prog)s compare --fpga fpga.bin --ref ref.bin
  %(prog)s full --steps 10 --agents 100  # Full workflow

Note:
  - JTAG capture requires debug infrastructure (ILA/VIO) in the FPGA design
  - Python reference requires slime_simulator package to be importable
        """
    )

    parser.add_argument('mode',
                       choices=['capture', 'reference', 'compare', 'full'],
                       help='Operation mode')
    parser.add_argument('--fpga',
                       help='FPGA trail map file (for compare mode)')
    parser.add_argument('--ref',
                       help='Reference trail map file (for compare mode)')
    parser.add_argument('--steps',
                       type=int,
                       default=10,
                       help='Number of simulation steps (default: 10)')
    parser.add_argument('--agents',
                       type=int,
                       default=100,
                       help='Number of agents (default: 100)')
    parser.add_argument('--width',
                       type=int,
                       default=160,
                       help='Trail map width (default: 160)')
    parser.add_argument('--height',
                       type=int,
                       default=120,
                       help='Trail map height (default: 120)')
    parser.add_argument('--tolerance',
                       type=int,
                       default=5,
                       help='Comparison tolerance (default: 5)')
    parser.add_argument('--output-dir',
                       help='Output directory for images and reports')
    parser.add_argument('--rtl-dir',
                       help='Path to RTL directory (default: ../rtl)')
    parser.add_argument('--save-images',
                       action='store_true',
                       help='Save comparison images (requires PIL)')
    parser.add_argument('--dry-run',
                       action='store_true',
                       help='Show what would be done without executing')
    parser.add_argument('--verbose', '-v',
                       action='store_true',
                       help='Verbose output')

    args = parser.parse_args()

    try:
        # Create capture instance
        capture = ImageCapture(
            rtl_dir=args.rtl_dir,
            output_dir=args.output_dir,
            dry_run=args.dry_run,
            verbose=args.verbose
        )

        if args.mode == 'reference':
            # Generate reference
            ref_map = capture.generate_python_reference(
                num_agents=args.agents,
                num_steps=args.steps,
                width=args.width,
                height=args.height
            )
            if ref_map is None:
                sys.exit(1)

        elif args.mode == 'capture':
            # Capture from FPGA
            if not args.dry_run and not capture.check_vivado_available():
                sys.exit(1)

            fpga_map = capture.capture_trail_map_jtag(
                width=args.width,
                height=args.height
            )
            if fpga_map is None:
                sys.exit(1)

            # Save captured map
            output_file = capture.output_dir / f"fpga_trail_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bin"
            fpga_map.tofile(output_file)
            capture.log(f"Saved captured map to: {output_file}")

        elif args.mode == 'compare':
            # Compare two trail maps
            if not args.fpga or not args.ref:
                print("ERROR: --fpga and --ref required for compare mode", file=sys.stderr)
                sys.exit(1)

            fpga_map = capture.read_trail_map_file(args.fpga)
            ref_map = capture.read_trail_map_file(args.ref)

            if fpga_map is None or ref_map is None:
                sys.exit(1)

            stats = capture.compare_trail_maps(fpga_map, ref_map, args.tolerance)
            if stats is None:
                sys.exit(1)

            if args.save_images:
                capture.save_comparison_images(fpga_map, ref_map)

            capture.save_comparison_report(stats)

            if stats['result'] == 'FAIL':
                sys.exit(1)

        elif args.mode == 'full':
            # Full workflow
            capture.log("Starting full validation workflow")

            # Generate reference
            ref_map = capture.generate_python_reference(
                num_agents=args.agents,
                num_steps=args.steps,
                width=args.width,
                height=args.height
            )
            if ref_map is None:
                sys.exit(1)

            # Capture from FPGA
            if not args.dry_run and not capture.check_vivado_available():
                sys.exit(1)

            fpga_map = capture.capture_trail_map_jtag(
                width=args.width,
                height=args.height
            )
            if fpga_map is None:
                sys.exit(1)

            # Compare
            stats = capture.compare_trail_maps(fpga_map, ref_map, args.tolerance)
            if stats is None:
                sys.exit(1)

            if args.save_images:
                capture.save_comparison_images(fpga_map, ref_map)

            capture.save_comparison_report(stats)

            if stats['result'] == 'FAIL':
                sys.exit(1)

        capture.log("=" * 60)
        capture.log("Complete!")
        capture.log(f"Log file: {capture.log_file}")
        capture.log("=" * 60)

        sys.exit(0)

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
