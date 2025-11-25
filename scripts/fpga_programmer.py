#!/usr/bin/env python3
"""
FPGA Programmer
Programs Xilinx FPGA devices via Vivado Hardware Manager.
"""

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path
from datetime import datetime
import shutil


class FPGAProgrammer:
    """Handles FPGA programming via Vivado Hardware Manager"""

    def __init__(self, bitstream=None, rtl_dir=None, dry_run=False, verbose=False):
        self.bitstream = Path(bitstream).resolve() if bitstream else None
        self.dry_run = dry_run
        self.verbose = verbose

        # Set up paths
        if rtl_dir:
            self.rtl_dir = Path(rtl_dir).resolve()
        else:
            script_dir = Path(__file__).parent
            self.rtl_dir = script_dir.parent / 'rtl'

        if not self.rtl_dir.exists():
            raise FileNotFoundError(f"RTL directory not found: {self.rtl_dir}")

        # Set up logging
        self.log_dir = self.rtl_dir / 'programming_logs'
        self.log_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_file = self.log_dir / f"program_{timestamp}.log"

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
            self.log("Please source Vivado settings64.sh first", 'ERROR')
            return False

        self.log(f"Found Vivado: {vivado_path}")
        return True

    def find_latest_bitstream(self):
        """Find the most recently generated bitstream"""
        self.log("Searching for bitstream files...")

        # Search patterns for different build types
        search_patterns = [
            'vivado_project/slime_simulator.runs/impl_1/*.bit',
            'vivado_project_simple/slime_simple.runs/impl_1/*.bit',
            'vivado_project_solid/vga_solid.runs/impl_1/*.bit',
            'vivado_project_test/slime_debug.runs/impl_1/*.bit',
        ]

        bitstreams = []
        for pattern in search_patterns:
            bitstreams.extend(self.rtl_dir.glob(pattern))

        if not bitstreams:
            self.log("No bitstream files found", 'ERROR')
            return None

        # Sort by modification time
        bitstreams.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        latest = bitstreams[0]
        mod_time = datetime.fromtimestamp(latest.stat().st_mtime)
        size_kb = latest.stat().st_size / 1024

        self.log(f"Found {len(bitstreams)} bitstream(s)")
        self.log(f"Latest: {latest.name}")
        self.log(f"  Path: {latest}")
        self.log(f"  Modified: {mod_time}")
        self.log(f"  Size: {size_kb:.1f} KB")

        return latest

    def verify_bitstream(self, bitstream):
        """Verify bitstream file exists and is valid"""
        if not bitstream.exists():
            self.log(f"Bitstream not found: {bitstream}", 'ERROR')
            return False

        if bitstream.suffix != '.bit':
            self.log(f"Invalid file type: {bitstream.suffix} (expected .bit)", 'ERROR')
            return False

        size = bitstream.stat().st_size
        if size == 0:
            self.log("Bitstream file is empty", 'ERROR')
            return False

        self.log(f"Bitstream verified: {bitstream.name} ({size / 1024:.1f} KB)")
        return True

    def check_fpga_connected(self):
        """Check if FPGA is connected and accessible"""
        self.log("Checking for connected FPGA...")

        if self.dry_run:
            self.log("DRY RUN - Skipping FPGA detection")
            return True

        # Create a simple TCL script to detect hardware
        tcl_script = """
open_hw_manager
connect_hw_server -allow_non_jtag
set targets [get_hw_targets]
if {[llength $targets] == 0} {
    puts "ERROR: No hardware targets found"
    exit 1
}
puts "Hardware targets found: $targets"
open_hw_target
set devices [get_hw_devices]
if {[llength $devices] == 0} {
    puts "ERROR: No devices found"
    exit 1
}
puts "Devices found: $devices"
close_hw_target
disconnect_hw_server
close_hw_manager
exit 0
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.tcl', delete=False) as f:
            f.write(tcl_script)
            tcl_file = Path(f.name)

        try:
            result = subprocess.run(
                ['vivado', '-mode', 'batch', '-source', str(tcl_file)],
                capture_output=True,
                text=True,
                timeout=30
            )

            if self.verbose:
                print(result.stdout)

            with open(self.log_file, 'a') as f:
                f.write(result.stdout)
                f.write(result.stderr)

            if result.returncode == 0:
                self.log("FPGA detected successfully")
                return True
            else:
                self.log("FPGA not detected or not accessible", 'ERROR')
                if 'No hardware targets found' in result.stdout:
                    self.log("Make sure FPGA is connected via USB", 'ERROR')
                    self.log("Check that cable drivers are installed", 'ERROR')
                return False

        except subprocess.TimeoutExpired:
            self.log("Timeout while checking for FPGA", 'ERROR')
            return False
        except Exception as e:
            self.log(f"Error checking FPGA: {e}", 'ERROR')
            return False
        finally:
            tcl_file.unlink(missing_ok=True)

    def program_fpga(self, bitstream):
        """Program the FPGA with the given bitstream"""
        self.log("=" * 60)
        self.log("Programming FPGA")
        self.log("=" * 60)
        self.log(f"Bitstream: {bitstream}")

        if self.dry_run:
            self.log("DRY RUN - Would program FPGA")
            return True

        # Create TCL script for programming
        tcl_script = f"""
# Open hardware manager
open_hw_manager

# Connect to hardware server
connect_hw_server -allow_non_jtag

# Open target (auto-detect)
open_hw_target

# Get first device
set device [lindex [get_hw_devices] 0]
if {{$device eq ""}} {{
    puts "ERROR: No device found"
    exit 1
}}

puts "Device: $device"
current_hw_device $device

# Set programming file
set_property PROGRAM.FILE {{{bitstream}}} $device

# Program the device
puts "Programming device..."
program_hw_devices $device

# Verify
refresh_hw_device $device

puts "============================================"
puts "FPGA programmed successfully!"
puts "============================================"

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
            self.log("Running Vivado Hardware Manager...")

            result = subprocess.run(
                ['vivado', '-mode', 'batch', '-source', str(tcl_file)],
                capture_output=True,
                text=True,
                timeout=120
            )

            # Log output
            with open(self.log_file, 'a') as f:
                f.write("=== Vivado Output ===\n")
                f.write(result.stdout)
                f.write("\n=== Stderr ===\n")
                f.write(result.stderr)

            if self.verbose:
                print(result.stdout)

            # Check for success
            if result.returncode == 0 and 'successfully' in result.stdout.lower():
                self.log("FPGA programmed successfully!")
                return True
            else:
                self.log("Programming failed", 'ERROR')
                if 'ERROR' in result.stdout:
                    # Extract error messages
                    for line in result.stdout.split('\n'):
                        if 'ERROR' in line:
                            self.log(f"  {line}", 'ERROR')
                return False

        except subprocess.TimeoutExpired:
            self.log("Timeout while programming FPGA", 'ERROR')
            return False
        except Exception as e:
            self.log(f"Error programming FPGA: {e}", 'ERROR')
            return False
        finally:
            tcl_file.unlink(missing_ok=True)

    def read_device_info(self):
        """Read information from the programmed device"""
        self.log("Reading device information...")

        if self.dry_run:
            self.log("DRY RUN - Would read device info")
            return {}

        tcl_script = """
open_hw_manager
connect_hw_server -allow_non_jtag
open_hw_target
set device [lindex [get_hw_devices] 0]
current_hw_device $device

puts "Device: [get_property NAME $device]"
puts "Part: [get_property PART $device]"
puts "Program Time: [get_property PROGRAM.PROGRAM_TIME $device]"

close_hw_target
disconnect_hw_server
close_hw_manager
exit 0
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.tcl', delete=False) as f:
            f.write(tcl_script)
            tcl_file = Path(f.name)

        try:
            result = subprocess.run(
                ['vivado', '-mode', 'batch', '-source', str(tcl_file)],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.startswith('Device:') or line.startswith('Part:') or line.startswith('Program Time:'):
                        self.log(line)

            return result.returncode == 0

        except Exception as e:
            self.log(f"Could not read device info: {e}", 'WARN')
            return False
        finally:
            tcl_file.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(
        description='FPGA Programmer - Program Xilinx FPGAs via Vivado',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Auto-detect latest bitstream
  %(prog)s --bitstream design.bit             # Program specific bitstream
  %(prog)s --check-only                       # Only check if FPGA is connected
  %(prog)s --bitstream design.bit --dry-run   # Show what would be done
  %(prog)s --info                             # Read device information

Notes:
  - Requires Vivado to be in PATH (source settings64.sh)
  - FPGA must be connected via USB
  - Cable drivers must be installed
        """
    )

    parser.add_argument('--bitstream', '-b',
                       help='Path to bitstream file (.bit)')
    parser.add_argument('--rtl-dir',
                       help='Path to RTL directory (default: ../rtl)')
    parser.add_argument('--check-only',
                       action='store_true',
                       help='Only check if FPGA is connected')
    parser.add_argument('--info',
                       action='store_true',
                       help='Read device information after programming')
    parser.add_argument('--dry-run',
                       action='store_true',
                       help='Show what would be done without executing')
    parser.add_argument('--verbose', '-v',
                       action='store_true',
                       help='Show all Vivado output')

    args = parser.parse_args()

    try:
        # Create programmer instance
        programmer = FPGAProgrammer(
            bitstream=args.bitstream,
            rtl_dir=args.rtl_dir,
            dry_run=args.dry_run,
            verbose=args.verbose
        )

        # Check Vivado availability
        if not args.dry_run and not programmer.check_vivado_available():
            sys.exit(1)

        # Check FPGA connection
        if not programmer.check_fpga_connected():
            sys.exit(1)

        if args.check_only:
            programmer.log("FPGA check complete")
            sys.exit(0)

        # Find or verify bitstream
        if programmer.bitstream:
            bitstream = programmer.bitstream
            if not programmer.verify_bitstream(bitstream):
                sys.exit(1)
        else:
            programmer.log("No bitstream specified, auto-detecting...")
            bitstream = programmer.find_latest_bitstream()
            if not bitstream:
                programmer.log("ERROR: Could not find bitstream", 'ERROR')
                programmer.log("Specify bitstream with --bitstream", 'ERROR')
                sys.exit(1)

            if not programmer.verify_bitstream(bitstream):
                sys.exit(1)

        # Program FPGA
        success = programmer.program_fpga(bitstream)

        if not success:
            sys.exit(1)

        # Read device info if requested
        if args.info:
            programmer.read_device_info()

        programmer.log("=" * 60)
        programmer.log("Programming complete!")
        programmer.log(f"Log file: {programmer.log_file}")
        programmer.log("=" * 60)

        sys.exit(0)

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
