#!/usr/bin/env python3
"""
Vivado Build Automation Script
Runs Vivado builds in batch mode with progress tracking and result parsing.
"""

import argparse
import subprocess
import sys
import re
import json
from pathlib import Path
from datetime import datetime
import shutil


class VivadoBuild:
    """Handles Vivado build automation"""

    BUILD_CONFIGS = {
        'main': {
            'tcl_script': 'build_vivado.tcl',
            'project_dir': 'vivado_project',
            'project_name': 'slime_simulator',
            'top_module': 'slime_top',
            'description': 'Full slime simulator with agent processor'
        },
        'simple': {
            'tcl_script': 'build_simple.tcl',
            'project_dir': 'vivado_project_simple',
            'project_name': 'slime_simple',
            'top_module': 'slime_top_simple',
            'description': 'Simplified version with trail animation'
        },
        'vga': {
            'tcl_script': 'build_solid_color.tcl',
            'project_dir': 'vivado_project_solid',
            'project_name': 'vga_solid',
            'top_module': 'vga_test_pattern',
            'description': 'VGA test pattern (diagnostic)'
        },
        'debug': {
            'tcl_script': 'build_simple.tcl',
            'project_dir': 'vivado_project_test',
            'project_name': 'slime_debug',
            'top_module': 'slime_top_debug',
            'description': 'Debug build with extra instrumentation'
        }
    }

    def __init__(self, build_type='main', rtl_dir=None, dry_run=False, verbose=False):
        self.build_type = build_type
        self.dry_run = dry_run
        self.verbose = verbose

        # Set up paths
        if rtl_dir:
            self.rtl_dir = Path(rtl_dir).resolve()
        else:
            # Default to rtl/ directory relative to script location
            script_dir = Path(__file__).parent
            self.rtl_dir = script_dir.parent / 'rtl'

        if not self.rtl_dir.exists():
            raise FileNotFoundError(f"RTL directory not found: {self.rtl_dir}")

        # Get build configuration
        if build_type not in self.BUILD_CONFIGS:
            raise ValueError(f"Unknown build type: {build_type}. "
                           f"Valid types: {', '.join(self.BUILD_CONFIGS.keys())}")

        self.config = self.BUILD_CONFIGS[build_type]
        self.tcl_script = self.rtl_dir / self.config['tcl_script']
        self.project_dir = self.rtl_dir / self.config['project_dir']

        # Set up logging
        self.log_dir = self.rtl_dir / 'build_logs'
        self.log_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_file = self.log_dir / f"build_{build_type}_{timestamp}.log"

    def log(self, message, level='INFO'):
        """Log message to console and file"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_msg = f"[{timestamp}] [{level}] {message}"
        print(log_msg)

        with open(self.log_file, 'a') as f:
            f.write(log_msg + '\n')

    def check_vivado_available(self):
        """Check if Vivado is available in PATH"""
        vivado_path = shutil.which('vivado')
        if not vivado_path:
            self.log("ERROR: Vivado not found in PATH", 'ERROR')
            self.log("Please source Vivado settings64.sh first", 'ERROR')
            return False

        self.log(f"Found Vivado: {vivado_path}")
        return True

    def clean_previous_build(self):
        """Clean previous build artifacts"""
        if self.project_dir.exists():
            self.log(f"Cleaning previous build: {self.project_dir}")
            if not self.dry_run:
                shutil.rmtree(self.project_dir)

        # Clean vivado logs
        for log_file in self.rtl_dir.glob('vivado*.log'):
            if not self.dry_run:
                log_file.unlink()
        for jou_file in self.rtl_dir.glob('vivado*.jou'):
            if not self.dry_run:
                jou_file.unlink()

    def run_build(self):
        """Run Vivado build"""
        if not self.tcl_script.exists():
            raise FileNotFoundError(f"TCL script not found: {self.tcl_script}")

        self.log("=" * 60)
        self.log(f"Starting Vivado Build: {self.build_type}")
        self.log(f"Description: {self.config['description']}")
        self.log(f"TCL Script: {self.tcl_script}")
        self.log("=" * 60)

        if self.dry_run:
            self.log("DRY RUN - Would execute:", 'INFO')
            self.log(f"  cd {self.rtl_dir}")
            self.log(f"  vivado -mode batch -source {self.tcl_script.name}")
            return True

        # Build command
        cmd = ['vivado', '-mode', 'batch', '-source', self.tcl_script.name]

        self.log(f"Running: {' '.join(cmd)}")
        self.log(f"Working directory: {self.rtl_dir}")

        # Run Vivado
        try:
            process = subprocess.Popen(
                cmd,
                cwd=self.rtl_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )

            # Stream output
            for line in process.stdout:
                line = line.rstrip()
                if self.verbose or any(keyword in line.lower() for keyword in
                                      ['error', 'critical', 'failed', 'success', 'complete']):
                    print(line)

                with open(self.log_file, 'a') as f:
                    f.write(line + '\n')

            process.wait()

            if process.returncode != 0:
                self.log(f"Build failed with return code: {process.returncode}", 'ERROR')
                return False

            self.log("Build completed successfully!")
            return True

        except FileNotFoundError:
            self.log("ERROR: Vivado executable not found", 'ERROR')
            return False
        except Exception as e:
            self.log(f"ERROR during build: {e}", 'ERROR')
            return False

    def parse_results(self):
        """Parse build results from reports"""
        results = {
            'build_type': self.build_type,
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'bitstream': None,
            'timing': {},
            'utilization': {}
        }

        if self.dry_run:
            return results

        # Find bitstream
        bitstream_pattern = f"{self.config['project_name']}.runs/impl_1/*.bit"
        bitstream_files = list(self.project_dir.glob(bitstream_pattern))

        if bitstream_files:
            results['bitstream'] = str(bitstream_files[0])
            results['bitstream_size_kb'] = bitstream_files[0].stat().st_size / 1024
            results['success'] = True
            self.log(f"Bitstream: {bitstream_files[0]}")
            self.log(f"Size: {results['bitstream_size_kb']:.1f} KB")
        else:
            self.log("WARNING: Bitstream not found", 'WARN')

        # Parse timing report
        timing_report = self.project_dir / f"{self.config['project_name']}.runs/impl_1/timing.rpt"
        if not timing_report.exists():
            timing_report = self.project_dir / 'timing.txt'

        if timing_report.exists():
            timing_data = self._parse_timing_report(timing_report)
            results['timing'] = timing_data

        # Parse utilization report
        util_report = self.project_dir / f"{self.config['project_name']}.runs/impl_1/utilization.rpt"
        if not util_report.exists():
            util_report = self.project_dir / 'utilization.txt'

        if util_report.exists():
            util_data = self._parse_utilization_report(util_report)
            results['utilization'] = util_data

        return results

    def _parse_timing_report(self, report_file):
        """Parse timing information from report"""
        timing = {}

        try:
            with open(report_file, 'r') as f:
                content = f.read()

            # Look for WNS (Worst Negative Slack)
            wns_match = re.search(r'WNS\(ns\)\s*:\s*([-\d.]+)', content)
            if wns_match:
                timing['wns_ns'] = float(wns_match.group(1))
                timing['timing_met'] = timing['wns_ns'] >= 0

            # Look for TNS (Total Negative Slack)
            tns_match = re.search(r'TNS\(ns\)\s*:\s*([-\d.]+)', content)
            if tns_match:
                timing['tns_ns'] = float(tns_match.group(1))

            # Look for clock period
            clock_match = re.search(r'create_clock.*period\s+([\d.]+)', content)
            if clock_match:
                timing['target_period_ns'] = float(clock_match.group(1))

            if timing.get('timing_met'):
                self.log("Timing: MET", 'INFO')
            else:
                self.log(f"Timing: VIOLATED (WNS={timing.get('wns_ns', 'N/A')} ns)", 'WARN')

        except Exception as e:
            self.log(f"Could not parse timing report: {e}", 'WARN')

        return timing

    def _parse_utilization_report(self, report_file):
        """Parse utilization information from report"""
        util = {}

        try:
            with open(report_file, 'r') as f:
                content = f.read()

            # Parse resource utilization
            resources = {
                'LUT': r'LUT.*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*([\d.]+)',
                'FF': r'Register.*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*([\d.]+)',
                'BRAM': r'Block RAM.*\|\s*([\d.]+)\s*\|\s*(\d+)\s*\|\s*([\d.]+)',
                'DSP': r'DSPs.*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*([\d.]+)'
            }

            for resource, pattern in resources.items():
                match = re.search(pattern, content)
                if match:
                    util[resource] = {
                        'used': int(float(match.group(1))),
                        'available': int(match.group(2)),
                        'percent': float(match.group(3))
                    }

            # Log utilization summary
            self.log("Resource Utilization:")
            for resource, data in util.items():
                self.log(f"  {resource}: {data['used']}/{data['available']} ({data['percent']:.1f}%)")

        except Exception as e:
            self.log(f"Could not parse utilization report: {e}", 'WARN')

        return util

    def save_results_json(self, results):
        """Save results to JSON file"""
        results_file = self.log_dir / f"build_results_{self.build_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)

        self.log(f"Results saved to: {results_file}")
        return results_file


def main():
    parser = argparse.ArgumentParser(
        description='Vivado Build Automation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Build Types:
  main    - Full slime simulator with agent processor
  simple  - Simplified version with trail animation
  vga     - VGA test pattern (diagnostic)
  debug   - Debug build with instrumentation

Examples:
  %(prog)s main                    # Build main design
  %(prog)s vga --verbose           # Build VGA test with verbose output
  %(prog)s simple --clean          # Clean and build simple design
  %(prog)s main --dry-run          # Show what would be done
        """
    )

    parser.add_argument('build_type',
                       choices=['main', 'simple', 'vga', 'debug'],
                       help='Type of build to perform')
    parser.add_argument('--rtl-dir',
                       help='Path to RTL directory (default: ../rtl)')
    parser.add_argument('--clean',
                       action='store_true',
                       help='Clean previous build before starting')
    parser.add_argument('--dry-run',
                       action='store_true',
                       help='Show what would be done without executing')
    parser.add_argument('--verbose', '-v',
                       action='store_true',
                       help='Show all Vivado output')
    parser.add_argument('--save-json',
                       action='store_true',
                       help='Save results to JSON file')

    args = parser.parse_args()

    try:
        # Create build instance
        builder = VivadoBuild(
            build_type=args.build_type,
            rtl_dir=args.rtl_dir,
            dry_run=args.dry_run,
            verbose=args.verbose
        )

        # Check Vivado availability
        if not args.dry_run and not builder.check_vivado_available():
            sys.exit(1)

        # Clean if requested
        if args.clean:
            builder.clean_previous_build()

        # Run build
        success = builder.run_build()

        if not success:
            sys.exit(1)

        # Parse and display results
        results = builder.parse_results()

        if args.save_json:
            builder.save_results_json(results)

        # Summary
        builder.log("=" * 60)
        builder.log("BUILD SUMMARY")
        builder.log("=" * 60)
        builder.log(f"Build Type: {args.build_type}")
        builder.log(f"Status: {'SUCCESS' if results['success'] else 'FAILED'}")
        builder.log(f"Log file: {builder.log_file}")

        if results['success']:
            builder.log(f"Bitstream: {results['bitstream']}")
            if results['timing'].get('timing_met') is not None:
                builder.log(f"Timing: {'MET' if results['timing']['timing_met'] else 'VIOLATED'}")

        sys.exit(0 if results['success'] else 1)

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
