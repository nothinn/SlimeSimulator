#!/usr/bin/env python3
"""
FPGA Controller for RTL Regression Testing

This script provides an interface to control the Slime Simulator FPGA via JTAG.
It can program the bitstream, initialize the simulation, step through iterations,
and read trail memory for comparison with Python reference.

Key Features:
- Program FPGA with bitstream
- Initialize simulation with fixed seed
- Step through iterations (wait for frame_start)
- Read trail memory via JTAG2AXI
- Save trail maps at specified iteration points
- Monitor simulation state and signals

Usage:
    python fpga_controller.py --bitstream build/slime_top.bit \\
           --iterations 1,5,10,20 --output-dir regression_test_results/rtl_capture
"""

import sys
import time
import subprocess
import argparse
import numpy as np
from pathlib import Path
from typing import Optional, List


class FPGAController:
    """
    Interface to Slime Simulator FPGA via Vivado TCL commands.
    """

    def __init__(self, vivado_path: str = "vivado", verbose: bool = True):
        """
        Initialize FPGA controller.

        Args:
            vivado_path: Path to Vivado executable
            verbose: Print detailed messages
        """
        self.vivado_path = vivado_path
        self.verbose = verbose
        self.hw_target = None
        self.device = None

    def log(self, message: str):
        """Print log message if verbose."""
        if self.verbose:
            print(f"[FPGA] {message}")

    def run_tcl_command(self, tcl_script: str, timeout: int = 60) -> str:
        """
        Run a TCL command via Vivado in batch mode.

        Args:
            tcl_script: TCL script to execute
            timeout: Command timeout in seconds

        Returns:
            Command output

        Raises:
            RuntimeError: If command fails
        """
        # Create temporary TCL file
        tcl_file = Path("/tmp/fpga_command.tcl")
        with open(tcl_file, 'w') as f:
            f.write(tcl_script)

        # Run Vivado in batch mode
        cmd = [self.vivado_path, "-mode", "batch", "-source", str(tcl_file)]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            if result.returncode != 0:
                raise RuntimeError(
                    f"Vivado command failed:\n{result.stderr}"
                )

            return result.stdout

        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Vivado command timed out after {timeout}s")

    def connect_fpga(self):
        """
        Connect to FPGA hardware via JTAG.

        Raises:
            RuntimeError: If connection fails
        """
        self.log("Connecting to FPGA via JTAG...")

        tcl_script = """
        # Open hardware manager
        open_hw_manager
        connect_hw_server -url localhost:3121

        # Get available targets
        set targets [get_hw_targets]
        if {[llength $targets] == 0} {
            puts "ERROR: No hardware targets found"
            exit 1
        }

        # Open first target
        set target [lindex $targets 0]
        current_hw_target $target
        open_hw_target

        # Get device
        set devices [get_hw_devices]
        if {[llength $devices] == 0} {
            puts "ERROR: No devices found"
            exit 1
        }

        set device [lindex $devices 0]
        puts "Connected to device: $device"
        """

        try:
            output = self.run_tcl_command(tcl_script)
            self.log(f"Successfully connected to FPGA")
            if "Connected to device:" in output:
                device_line = [l for l in output.split('\n') if 'Connected to device:' in l][0]
                self.device = device_line.split(':')[-1].strip()
                self.log(f"Device: {self.device}")
        except RuntimeError as e:
            raise RuntimeError(f"Failed to connect to FPGA: {e}")

    def program_bitstream(self, bitstream_path: str):
        """
        Program FPGA with bitstream.

        Args:
            bitstream_path: Path to .bit file

        Raises:
            RuntimeError: If programming fails
        """
        bitstream = Path(bitstream_path)
        if not bitstream.exists():
            raise RuntimeError(f"Bitstream not found: {bitstream_path}")

        self.log(f"Programming bitstream: {bitstream.name}")

        tcl_script = f"""
        # Open hardware manager and connect
        open_hw_manager
        connect_hw_server -url localhost:3121
        set target [lindex [get_hw_targets] 0]
        current_hw_target $target
        open_hw_target

        # Get device
        set device [lindex [get_hw_devices] 0]
        current_hw_device $device

        # Program device
        set_property PROGRAM.FILE {{{bitstream.absolute()}}} $device
        program_hw_devices $device

        puts "Programming complete"
        """

        try:
            output = self.run_tcl_command(tcl_script, timeout=120)
            self.log("Bitstream programmed successfully")
        except RuntimeError as e:
            raise RuntimeError(f"Failed to program bitstream: {e}")

    def read_memory(self, address: int, length: int) -> bytes:
        """
        Read memory from FPGA via JTAG (placeholder - requires AXI interface).

        In a real implementation, this would use JTAG2AXI or Virtual I/O (VIO)
        to read BRAM memory. For now, this is a placeholder.

        Args:
            address: Memory start address
            length: Number of bytes to read

        Returns:
            Memory contents as bytes

        Raises:
            NotImplementedError: This requires JTAG2AXI IP in design
        """
        # NOTE: This requires JTAG2AXI or similar IP in the RTL design
        # For the initial implementation, we'll return zeros as placeholder
        self.log(f"Reading {length} bytes from address 0x{address:04X}")
        self.log("WARNING: Memory read not yet implemented - requires JTAG2AXI IP")
        self.log("         Returning zeros as placeholder")

        # In a real implementation with JTAG2AXI:
        # tcl_script = f"""
        # # Connect to AXI interface
        # create_hw_axi_txn read_txn [get_hw_axis hw_axi_1] -address {hex(address)} \\
        #     -len {length} -type read
        # run_hw_axi read_txn
        # set data [report_hw_axi_txn read_txn -w]
        # puts $data
        # """

        return bytes(length)

    def read_trail_memory(self, width: int = 160, height: int = 120) -> np.ndarray:
        """
        Read trail map memory from FPGA.

        Args:
            width: Trail map width
            height: Trail map height

        Returns:
            Trail map as numpy array (height, width)

        Raises:
            NotImplementedError: Requires JTAG2AXI IP
        """
        size = width * height
        data = self.read_memory(address=0x0000, length=size)

        # Convert to numpy array
        trail_map = np.frombuffer(data, dtype=np.uint8).reshape(height, width)
        return trail_map

    def wait_for_frame(self, timeout: int = 5) -> bool:
        """
        Wait for frame_start signal (indicates iteration complete).

        This is a placeholder - in a real implementation, would use VIO
        to monitor the frame_start signal.

        Args:
            timeout: Timeout in seconds

        Returns:
            True if frame_start detected, False if timeout

        Raises:
            NotImplementedError: Requires VIO IP in design
        """
        self.log("Waiting for frame_start signal...")
        self.log("WARNING: Signal monitoring not yet implemented - requires VIO IP")
        self.log("         Using fixed delay instead")

        # In a real implementation with VIO:
        # tcl_script = """
        # set vio [get_hw_vios]
        # set frame_start [get_hw_probes frame_start -of_objects $vio]
        # set prev_val [get_property INPUT_VALUE $frame_start]
        #
        # # Wait for rising edge
        # set timeout [clock seconds] + {timeout}
        # while {[clock seconds] < $timeout} {
        #     refresh_hw_vio $vio
        #     set curr_val [get_property INPUT_VALUE $frame_start]
        #     if {$curr_val == 1 && $prev_val == 0} {
        #         puts "Frame start detected"
        #         return
        #     }
        #     set prev_val $curr_val
        #     after 100
        # }
        # puts "Timeout waiting for frame"
        # """

        # For now, use a fixed delay (assuming ~60 FPS = ~16ms per frame)
        time.sleep(0.02)  # 20ms
        return True

    def initialize_simulation(self, seed: int = 0xDEADBEEF):
        """
        Initialize simulation with specified seed.

        This is a placeholder - would require control interface in RTL.

        Args:
            seed: LFSR seed
        """
        self.log(f"Initializing simulation with seed 0x{seed:08X}")
        self.log("WARNING: Initialization not yet implemented - requires control interface")
        self.log("         Assuming FPGA boots with correct seed")

    def capture_iterations(
        self,
        iterations: List[int],
        output_dir: str,
        width: int = 160,
        height: int = 120
    ) -> dict:
        """
        Step through iterations and capture trail maps.

        Args:
            iterations: List of iteration numbers to capture
            output_dir: Directory to save captured trail maps
            width: Trail map width
            height: Trail map height

        Returns:
            dict: Mapping from iteration to trail map array
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        iterations_sorted = sorted(iterations)
        max_iter = max(iterations_sorted)

        trail_maps = {}

        self.log(f"Capturing trail maps at iterations: {iterations_sorted}")

        for i in range(1, max_iter + 1):
            # Wait for iteration to complete
            if not self.wait_for_frame(timeout=5):
                raise RuntimeError(f"Timeout waiting for iteration {i}")

            if i in iterations_sorted:
                # Read trail memory
                try:
                    trail_map = self.read_trail_memory(width, height)
                    trail_maps[i] = trail_map

                    # Save to file
                    filename = output_path / f"trail_iter_{i:03d}.bin"
                    trail_map.tofile(str(filename))

                    # Statistics
                    nonzero = np.count_nonzero(trail_map)
                    mean_val = np.mean(trail_map[trail_map > 0]) if nonzero > 0 else 0
                    max_val = np.max(trail_map)

                    self.log(f"  Iter {i:3d}: {nonzero:6d} pixels written "
                            f"(mean={mean_val:.1f}, max={max_val})")
                    self.log(f"           -> {filename}")

                except Exception as e:
                    self.log(f"ERROR: Failed to capture iteration {i}: {e}")
                    raise

        self.log(f"Captured {len(trail_maps)} trail maps from RTL")
        return trail_maps


def main():
    parser = argparse.ArgumentParser(
        description='Control FPGA and capture RTL trail maps',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full workflow: program and capture
  python fpga_controller.py --bitstream build/slime_top.bit --iterations 1,5,10,20

  # Connect only (no programming)
  python fpga_controller.py --no-program --iterations 1,5,10,20

  # Custom output directory
  python fpga_controller.py --bitstream build/slime_top.bit \\
      --output-dir custom_test/rtl_capture

Notes:
  - Requires Vivado in PATH or use --vivado-path
  - FPGA must be connected via JTAG
  - Current implementation is a framework - full functionality requires:
    * JTAG2AXI IP for memory readout
    * VIO IP for signal monitoring
    * Control interface for initialization
        """
    )

    parser.add_argument('--bitstream', type=str,
                        help='Path to bitstream file (.bit)')
    parser.add_argument('--no-program', action='store_true',
                        help='Skip programming (FPGA already programmed)')
    parser.add_argument('--iterations', type=str, default='1,5,10,20',
                        help='Comma-separated iterations to capture (default: 1,5,10,20)')
    parser.add_argument('--output-dir', type=str,
                        default='regression_test_results/rtl_capture',
                        help='Output directory (default: regression_test_results/rtl_capture)')
    parser.add_argument('--width', type=int, default=160,
                        help='Trail map width (default: 160)')
    parser.add_argument('--height', type=int, default=120,
                        help='Trail map height (default: 120)')
    parser.add_argument('--seed', type=lambda x: int(x, 0), default=0xDEADBEEF,
                        help='LFSR seed (default: 0xDEADBEEF)')
    parser.add_argument('--vivado-path', type=str, default='vivado',
                        help='Path to Vivado executable')
    parser.add_argument('--quiet', action='store_true',
                        help='Suppress progress messages')

    args = parser.parse_args()

    # Validate arguments
    if not args.no_program and not args.bitstream:
        parser.error("--bitstream required unless --no-program specified")

    # Parse iterations
    try:
        iterations = [int(x.strip()) for x in args.iterations.split(',')]
    except ValueError:
        print(f"Error: Invalid iterations format: {args.iterations}")
        sys.exit(1)

    # Create controller
    controller = FPGAController(
        vivado_path=args.vivado_path,
        verbose=not args.quiet
    )

    try:
        # Connect to FPGA
        controller.connect_fpga()

        # Program bitstream if requested
        if not args.no_program:
            controller.program_bitstream(args.bitstream)

        # Initialize simulation
        controller.initialize_simulation(args.seed)

        # Capture iterations
        trail_maps = controller.capture_iterations(
            iterations=iterations,
            output_dir=args.output_dir,
            width=args.width,
            height=args.height
        )

        controller.log(f"\nCapture complete! {len(trail_maps)} trail maps saved.")
        controller.log(f"Output directory: {Path(args.output_dir).absolute()}")

    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
