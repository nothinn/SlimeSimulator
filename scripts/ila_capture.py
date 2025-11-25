#!/usr/bin/env python3
"""
ILA Capture Tool for Slime Simulator FPGA Debug
================================================

Tool for triggering and capturing waveforms from the Integrated Logic Analyzer (ILA)
embedded in the FPGA design. Provides trigger configuration, capture control, and
export functionality.

The ILA monitors critical signals in the Slime Simulator:
- Probe 0: lfsr_state[31:0] - LFSR random generator
- Probe 1: sim_state[3:0] - State machine
- Probe 2: agent_idx[9:0] - Current agent
- Probe 3: trail_addr_b[18:0] - Trail map write address
- Probe 4: trail_data_b_in[7:0] - Trail map write data
- Probe 5: trail_we_b - Trail map write enable
- Probe 6: vga_hs - VGA horizontal sync
- Probe 7: vga_vs - VGA vertical sync
- Probe 8: pixel_x[9:0] - VGA X coordinate
- Probe 9: pixel_y[8:0] - VGA Y coordinate
- Probe 10: frame_start - Frame start pulse
- Probe 11: sim_running - Simulation running
- Probe 12: sim_pause - Simulation paused
- Probe 13: speed_level[3:0] - Speed control
- Probe 14: btn_debounced[4:0] - Button inputs

Features:
- Arm ILA for capture
- Configure trigger conditions (value, edge, pattern)
- Capture waveform data (8192 samples)
- Export to CSV for analysis
- Export to VCD for waveform viewers
- Real-time trigger status monitoring

Requirements:
- Vivado Hardware Manager
- FPGA programmed with ILA-enabled bitstream
- Python 3.6+

Usage:
    # Arm ILA and wait for trigger
    ./ila_capture.py --arm --wait

    # Trigger on specific LFSR value
    ./ila_capture.py --trigger-lfsr 0x12345678 --capture output.csv

    # Trigger on agent index = 0
    ./ila_capture.py --trigger-agent 0 --capture output.csv

    # Export capture to VCD
    ./ila_capture.py --load capture.csv --export-vcd output.vcd

Author: Claude (Anthropic)
Date: 2025-11-25
"""

import subprocess
import argparse
import sys
import csv
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging

# ============================================================================
# Constants
# ============================================================================

# ILA configuration
ILA_DEPTH = 8192  # Sample depth
ILA_PROBES = 15   # Number of probes

# Probe definitions (name, width, description)
PROBE_DEFS = [
    ('lfsr_state', 32, 'LFSR random number generator'),
    ('sim_state', 4, 'Simulation state machine'),
    ('agent_idx', 10, 'Current agent index (0-999)'),
    ('trail_addr_b', 19, 'Trail map write address'),
    ('trail_data_b_in', 8, 'Trail map write data'),
    ('trail_we_b', 1, 'Trail map write enable'),
    ('vga_hs', 1, 'VGA horizontal sync'),
    ('vga_vs', 1, 'VGA vertical sync'),
    ('pixel_x', 10, 'VGA pixel X coordinate'),
    ('pixel_y', 9, 'VGA pixel Y coordinate'),
    ('frame_start', 1, 'VGA frame start pulse'),
    ('sim_running', 1, 'Simulation running flag'),
    ('sim_pause', 1, 'Simulation pause flag'),
    ('speed_level', 4, 'Speed control level'),
    ('btn_debounced', 5, 'Debounced button inputs'),
]

# Trigger modes
TRIGGER_VALUE = 'value'
TRIGGER_EDGE_RISING = 'rising'
TRIGGER_EDGE_FALLING = 'falling'
TRIGGER_EDGE_BOTH = 'both'

# ============================================================================
# Logging Setup
# ============================================================================

def setup_logging(verbose: bool = False):
    """Configure logging output"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


# ============================================================================
# ILA Interface
# ============================================================================

class ILACapture:
    """Interface to ILA debug core via Vivado Hardware Manager"""

    def __init__(self, hw_server: str = "localhost:3121", dry_run: bool = False):
        """
        Initialize ILA interface

        Args:
            hw_server: Hardware server address
            dry_run: If True, show commands without executing
        """
        self.hw_server = hw_server
        self.dry_run = dry_run
        self.connected = False
        self.logger = logging.getLogger(__name__)
        self.ila_name = None

    def connect(self) -> bool:
        """Connect to FPGA and find ILA core"""
        if self.dry_run:
            self.logger.info("[DRY RUN] Would connect to %s", self.hw_server)
            self.connected = True
            self.ila_name = "hw_ila_1"
            return True

        tcl_script = f"""
        # Connect to hardware server
        open_hw_manager
        connect_hw_server -url {self.hw_server}

        # Open target and device
        set targets [get_hw_targets]
        if {{[llength $targets] == 0}} {{
            puts "ERROR: No hardware targets found"
            exit 1
        }}
        current_hw_target [lindex $targets 0]
        open_hw_target

        set devices [get_hw_devices]
        if {{[llength $devices] == 0}} {{
            puts "ERROR: No hardware devices found"
            exit 1
        }}
        current_hw_device [lindex $devices 0]

        # Refresh device and find ILA
        refresh_hw_device [current_hw_device]

        set ilas [get_hw_ilas]
        if {{[llength $ilas] == 0}} {{
            puts "ERROR: No ILA cores found in design"
            exit 1
        }}

        set ila [lindex $ilas 0]
        puts "FOUND_ILA: $ila"
        """

        try:
            result = self._run_tcl(tcl_script)
            if result and "FOUND_ILA:" in result:
                self.ila_name = result.split("FOUND_ILA:")[1].strip()
                self.connected = True
                self.logger.info("Connected to ILA: %s", self.ila_name)
                return True
            else:
                self.logger.error("Failed to find ILA core")
                return False
        except Exception as e:
            self.logger.error("Connection error: %s", e)
            return False

    def disconnect(self):
        """Disconnect from FPGA"""
        if self.dry_run:
            self.logger.info("[DRY RUN] Would disconnect")
            return

        if self.connected:
            tcl_script = """
            close_hw_target
            disconnect_hw_server
            close_hw_manager
            """
            try:
                self._run_tcl(tcl_script)
                self.connected = False
                self.logger.info("Disconnected from FPGA")
            except Exception as e:
                self.logger.warning("Error during disconnect: %s", e)

    def _run_tcl(self, tcl_script: str) -> Optional[str]:
        """Execute TCL script via Vivado batch mode"""
        tcl_file = Path("/tmp/ila_capture_tmp.tcl")
        tcl_file.write_text(tcl_script)

        try:
            cmd = [
                "vivado",
                "-mode", "batch",
                "-source", str(tcl_file),
                "-notrace"
            ]

            self.logger.debug("Running Vivado command: %s", " ".join(cmd))

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            tcl_file.unlink()

            if result.returncode != 0:
                self.logger.error("Vivado command failed: %s", result.stderr)
                return None

            return result.stdout

        except subprocess.TimeoutExpired:
            self.logger.error("Vivado command timed out")
            tcl_file.unlink()
            return None
        except Exception as e:
            self.logger.error("Error running Vivado: %s", e)
            if tcl_file.exists():
                tcl_file.unlink()
            return None

    def arm_ila(self) -> bool:
        """Arm ILA for capture (sets up trigger but doesn't wait)"""
        if not self.connected:
            self.logger.error("Not connected to FPGA")
            return False

        if self.dry_run:
            self.logger.info("[DRY RUN] Would arm ILA")
            return True

        self.logger.info("Arming ILA...")

        tcl_script = f"""
        # Arm the ILA
        set ila [get_hw_ilas {self.ila_name}]
        run_hw_ila $ila
        puts "ILA_ARMED"
        """

        result = self._run_tcl(tcl_script)
        if result and "ILA_ARMED" in result:
            self.logger.info("ILA armed and ready")
            return True
        else:
            self.logger.error("Failed to arm ILA")
            return False

    def set_trigger_value(self, probe_idx: int, value: int) -> bool:
        """
        Configure ILA to trigger on specific probe value

        Args:
            probe_idx: Probe index (0-14)
            value: Trigger value

        Returns:
            True on success
        """
        if not self.connected:
            self.logger.error("Not connected to FPGA")
            return False

        if not (0 <= probe_idx < ILA_PROBES):
            self.logger.error("Invalid probe index: %d", probe_idx)
            return False

        probe_name, probe_width, probe_desc = PROBE_DEFS[probe_idx]

        if self.dry_run:
            self.logger.info("[DRY RUN] Would set trigger: %s = 0x%X", probe_name, value)
            return True

        self.logger.info("Setting trigger: %s (probe%d) = 0x%X", probe_name, probe_idx, value)

        # Format value with correct width
        value_str = format(value, f'0{probe_width}b')

        tcl_script = f"""
        # Configure trigger
        set ila [get_hw_ilas {self.ila_name}]

        # Set trigger condition on probe
        set_property CONTROL.TRIGGER_CONDITION TRIG_IN [get_hw_ilas $ila]
        set_property CONTROL.TRIGGER_MODE BASIC [get_hw_ilas $ila]

        # Set probe trigger value
        set_property TRIGGER_COMPARE_VALUE == [get_hw_probes {{$ila/probe{probe_idx}}}]
        set_property TRIGGER_VALUE {value_str} [get_hw_probes {{$ila/probe{probe_idx}}}]

        puts "TRIGGER_SET"
        """

        result = self._run_tcl(tcl_script)
        if result and "TRIGGER_SET" in result:
            self.logger.info("Trigger configured")
            return True
        else:
            self.logger.error("Failed to configure trigger")
            return False

    def wait_for_trigger(self, timeout: int = 30) -> bool:
        """
        Wait for ILA to trigger

        Args:
            timeout: Maximum wait time in seconds

        Returns:
            True if triggered, False if timeout
        """
        if not self.connected:
            self.logger.error("Not connected to FPGA")
            return False

        if self.dry_run:
            self.logger.info("[DRY RUN] Would wait for trigger (max %d sec)", timeout)
            return True

        self.logger.info("Waiting for trigger (max %d seconds)...", timeout)

        tcl_script = f"""
        # Wait for trigger
        set ila [get_hw_ilas {self.ila_name}]
        wait_on_hw_ila $ila -timeout {timeout}

        # Check if triggered
        set status [get_property STATUS $ila]
        if {{$status == "TRIGGERED"}} {{
            puts "TRIGGERED"
        }} else {{
            puts "TIMEOUT"
        }}
        """

        result = self._run_tcl(tcl_script)
        if result and "TRIGGERED" in result:
            self.logger.info("ILA triggered!")
            return True
        else:
            self.logger.warning("ILA trigger timeout")
            return False

    def capture_and_save(self, output_file: str) -> bool:
        """
        Capture waveform data and save to CSV

        Args:
            output_file: Output CSV filename

        Returns:
            True on success
        """
        if not self.connected:
            self.logger.error("Not connected to FPGA")
            return False

        if self.dry_run:
            self.logger.info("[DRY RUN] Would capture to %s", output_file)
            return True

        self.logger.info("Capturing waveform data...")

        # Use Vivado's built-in CSV export
        csv_temp = Path("/tmp/ila_capture_data.csv")

        tcl_script = f"""
        # Upload and display waveform
        set ila [get_hw_ilas {self.ila_name}]
        display_hw_ila_data [upload_hw_ila_data $ila]

        # Export to CSV
        write_hw_ila_data -csv_file {csv_temp} hw_ila_data_1

        puts "CAPTURE_DONE"
        """

        result = self._run_tcl(tcl_script)
        if result and "CAPTURE_DONE" in result:
            # Move CSV to desired location
            if csv_temp.exists():
                import shutil
                shutil.move(str(csv_temp), output_file)
                self.logger.info("Waveform saved to %s", output_file)
                return True
            else:
                self.logger.error("CSV file not created")
                return False
        else:
            self.logger.error("Failed to capture waveform")
            return False

    def analyze_capture(self, csv_file: str) -> Dict[str, Any]:
        """
        Analyze captured waveform data

        Args:
            csv_file: CSV file from capture

        Returns:
            Dictionary with analysis results
        """
        self.logger.info("Analyzing capture: %s", csv_file)

        try:
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            if not rows:
                self.logger.error("No data in CSV file")
                return {}

            # Extract statistics
            num_samples = len(rows)

            # Count signal transitions
            transitions = {}
            for probe_name, _, _ in PROBE_DEFS:
                if probe_name in rows[0]:
                    prev_val = None
                    count = 0
                    for row in rows:
                        val = row[probe_name]
                        if prev_val is not None and val != prev_val:
                            count += 1
                        prev_val = val
                    transitions[probe_name] = count

            stats = {
                'num_samples': num_samples,
                'transitions': transitions,
                'probes': list(rows[0].keys())
            }

            self.logger.info("Analysis complete:")
            self.logger.info("  Samples: %d", num_samples)
            for probe, count in transitions.items():
                self.logger.info("  %s: %d transitions", probe, count)

            return stats

        except Exception as e:
            self.logger.error("Failed to analyze capture: %s", e)
            return {}

    def export_vcd(self, csv_file: str, vcd_file: str) -> bool:
        """
        Convert CSV capture to VCD format for waveform viewers

        Args:
            csv_file: Input CSV file
            vcd_file: Output VCD file

        Returns:
            True on success
        """
        self.logger.info("Converting %s to VCD format...", csv_file)

        try:
            # Read CSV data
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            if not rows:
                self.logger.error("No data in CSV")
                return False

            # Write VCD header
            with open(vcd_file, 'w') as f:
                # Header
                f.write("$version SlimeSimulator ILA Capture $end\n")
                f.write("$timescale 1ns $end\n")
                f.write("$scope module ila $end\n")

                # Variable declarations
                var_map = {}
                for idx, (probe_name, probe_width, probe_desc) in enumerate(PROBE_DEFS):
                    if probe_name in rows[0]:
                        var_id = chr(33 + idx)  # ASCII starting from '!'
                        var_map[probe_name] = var_id
                        f.write(f"$var wire {probe_width} {var_id} {probe_name} $end\n")

                f.write("$upscope $end\n")
                f.write("$enddefinitions $end\n")

                # Initial values
                f.write("$dumpvars\n")
                for probe_name, var_id in var_map.items():
                    val = rows[0][probe_name]
                    if 'x' in val.lower():
                        f.write(f"bx {var_id}\n")
                    else:
                        # Convert hex to binary
                        try:
                            int_val = int(val, 16) if val.startswith('0x') else int(val)
                            f.write(f"b{bin(int_val)[2:]} {var_id}\n")
                        except:
                            f.write(f"b0 {var_id}\n")
                f.write("$end\n")

                # Value changes (assume 10ns per sample at 100 MHz)
                for idx, row in enumerate(rows[1:], 1):
                    time_ns = idx * 10
                    f.write(f"#{time_ns}\n")

                    # Check for changes
                    for probe_name, var_id in var_map.items():
                        if row[probe_name] != rows[idx-1][probe_name]:
                            val = row[probe_name]
                            try:
                                int_val = int(val, 16) if val.startswith('0x') else int(val)
                                f.write(f"b{bin(int_val)[2:]} {var_id}\n")
                            except:
                                f.write(f"bx {var_id}\n")

            self.logger.info("VCD file created: %s", vcd_file)
            return True

        except Exception as e:
            self.logger.error("Failed to create VCD: %s", e)
            return False


# ============================================================================
# Main CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='ILA Capture Tool for Slime Simulator FPGA',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Arm ILA and wait for trigger
  %(prog)s --arm --wait --capture output.csv

  # Trigger on LFSR value
  %(prog)s --trigger-lfsr 0x12345678 --capture output.csv

  # Trigger on agent index 0
  %(prog)s --trigger-agent 0 --capture output.csv

  # Trigger on frame start pulse
  %(prog)s --trigger-frame-start --capture output.csv

  # Analyze existing capture
  %(prog)s --analyze capture.csv

  # Export to VCD
  %(prog)s --load capture.csv --export-vcd output.vcd
        """
    )

    parser.add_argument('--hw-server', default='localhost:3121',
                        help='Hardware server address')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show commands without executing')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Enable verbose logging')

    # ILA control
    parser.add_argument('--arm', action='store_true',
                        help='Arm ILA for capture')
    parser.add_argument('--wait', action='store_true',
                        help='Wait for trigger')
    parser.add_argument('--timeout', type=int, default=30,
                        help='Trigger wait timeout in seconds (default: 30)')

    # Trigger configuration
    parser.add_argument('--trigger-lfsr', type=lambda x: int(x, 0),
                        help='Trigger on LFSR value (hex or decimal)')
    parser.add_argument('--trigger-state', type=int,
                        help='Trigger on simulation state (0-6)')
    parser.add_argument('--trigger-agent', type=int,
                        help='Trigger on agent index (0-999)')
    parser.add_argument('--trigger-frame-start', action='store_true',
                        help='Trigger on frame start pulse')

    # Capture and export
    parser.add_argument('--capture', metavar='FILE',
                        help='Capture waveform to CSV file')
    parser.add_argument('--analyze', metavar='FILE',
                        help='Analyze existing CSV capture')
    parser.add_argument('--load', metavar='FILE',
                        help='Load CSV for export')
    parser.add_argument('--export-vcd', metavar='FILE',
                        help='Export to VCD format')

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    # Analysis mode (no FPGA connection needed)
    if args.analyze:
        ila = ILACapture(dry_run=True)
        ila.analyze_capture(args.analyze)
        return 0

    # Export mode (no FPGA connection needed)
    if args.load and args.export_vcd:
        ila = ILACapture(dry_run=True)
        ila.export_vcd(args.load, args.export_vcd)
        return 0

    # Create ILA interface
    ila = ILACapture(hw_server=args.hw_server, dry_run=args.dry_run)

    # Connect to FPGA
    if not ila.connect():
        logger.error("Failed to connect to FPGA")
        return 1

    try:
        # Configure trigger
        trigger_set = False

        if args.trigger_lfsr is not None:
            trigger_set = ila.set_trigger_value(0, args.trigger_lfsr)

        if args.trigger_state is not None:
            trigger_set = ila.set_trigger_value(1, args.trigger_state)

        if args.trigger_agent is not None:
            trigger_set = ila.set_trigger_value(2, args.trigger_agent)

        if args.trigger_frame_start:
            trigger_set = ila.set_trigger_value(10, 1)  # frame_start = 1

        # Arm ILA
        if args.arm or trigger_set:
            if not ila.arm_ila():
                logger.error("Failed to arm ILA")
                return 1

        # Wait for trigger
        if args.wait or trigger_set:
            if not ila.wait_for_trigger(args.timeout):
                logger.error("Trigger timeout")
                return 1

        # Capture data
        if args.capture:
            if not ila.capture_and_save(args.capture):
                logger.error("Failed to capture waveform")
                return 1

            # Analyze it
            ila.analyze_capture(args.capture)

    finally:
        ila.disconnect()

    return 0


if __name__ == '__main__':
    sys.exit(main())
