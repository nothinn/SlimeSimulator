#!/usr/bin/env python3
"""
VIO Control Tool for Slime Simulator FPGA Debug
================================================

Tool for reading and writing Virtual I/O (VIO) registers in the FPGA.
VIO provides software-accessible registers for monitoring and controlling
the simulation without recompilation.

VIO Input Probes (Read from FPGA):
- IN0: lfsr_state[31:0] - Current LFSR value
- IN1: sim_state[3:0] - Current simulation state
- IN2: agent_idx[9:0] - Current agent index
- IN3: trail_data_b_out[7:0] - Trail map read data
- IN4: frame_count[31:0] - VGA frame counter (~60 Hz)
- IN5: sim_running - Running status flag
- IN6: led[15:0] - LED status display

VIO Output Probes (Write to FPGA):
- OUT0: vio_sim_freeze - Freeze simulation
- OUT1: vio_trail_read_en - Enable trail map read
- OUT2: vio_trail_addr[18:0] - Trail map address to read
- OUT3: vio_lfsr_seed[31:0] - Inject new LFSR seed

Features:
- Read all VIO input registers
- Write VIO output registers
- Inject custom LFSR seed for reproducibility
- Real-time monitoring dashboard
- Pretty-print register values with interpretations

Requirements:
- Vivado Hardware Manager
- FPGA programmed with VIO-enabled bitstream
- Python 3.6+

Usage:
    # Read all registers
    ./vio_control.py --read-all

    # Inject LFSR seed
    ./vio_control.py --set-lfsr-seed 0x12345678

    # Freeze simulation
    ./vio_control.py --freeze

    # Monitor live (updates every second)
    ./vio_control.py --monitor

Author: Claude (Anthropic)
Date: 2025-11-25
"""

import subprocess
import argparse
import sys
import time
from pathlib import Path
from typing import Optional, Dict
import logging

# ============================================================================
# Constants
# ============================================================================

# VIO probe definitions
VIO_INPUT_PROBES = [
    ('lfsr_state', 32, 'LFSR random number generator'),
    ('sim_state', 4, 'Simulation state machine'),
    ('agent_idx', 10, 'Current agent index'),
    ('trail_data_out', 8, 'Trail map read data'),
    ('frame_count', 32, 'VGA frame counter'),
    ('sim_running', 1, 'Simulation running flag'),
    ('led_status', 16, 'LED display status'),
]

VIO_OUTPUT_PROBES = [
    ('sim_freeze', 1, 'Freeze simulation control'),
    ('trail_read_en', 1, 'Trail map read enable'),
    ('trail_addr', 19, 'Trail map read address'),
    ('lfsr_seed', 32, 'LFSR seed injection'),
]

# Simulation states
SIM_STATES = {
    0: "RESET",
    1: "INIT_TRAIL",
    2: "PROCESS_AGENTS",
    3: "AGENT_WAIT",
    4: "DECAY_TRAIL",
    5: "WAIT_FRAME",
    6: "PAUSED"
}

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
# VIO Interface
# ============================================================================

class VIOControl:
    """Interface to VIO debug core via Vivado Hardware Manager"""

    def __init__(self, hw_server: str = "localhost:3121", dry_run: bool = False):
        """Initialize VIO interface"""
        self.hw_server = hw_server
        self.dry_run = dry_run
        self.connected = False
        self.logger = logging.getLogger(__name__)
        self.vio_name = None

    def connect(self) -> bool:
        """Connect to FPGA and find VIO core"""
        if self.dry_run:
            self.logger.info("[DRY RUN] Would connect to %s", self.hw_server)
            self.connected = True
            self.vio_name = "hw_vio_1"
            return True

        tcl_script = f"""
        open_hw_manager
        connect_hw_server -url {self.hw_server}

        set targets [get_hw_targets]
        current_hw_target [lindex $targets 0]
        open_hw_target

        set devices [get_hw_devices]
        current_hw_device [lindex $devices 0]

        refresh_hw_device [current_hw_device]

        set vios [get_hw_vios]
        if {{[llength $vios] == 0}} {{
            puts "ERROR: No VIO cores found"
            exit 1
        }}

        set vio [lindex $vios 0]
        puts "FOUND_VIO: $vio"
        """

        try:
            result = self._run_tcl(tcl_script)
            if result and "FOUND_VIO:" in result:
                self.vio_name = result.split("FOUND_VIO:")[1].strip()
                self.connected = True
                self.logger.info("Connected to VIO: %s", self.vio_name)
                return True
            else:
                self.logger.error("Failed to find VIO core")
                return False
        except Exception as e:
            self.logger.error("Connection error: %s", e)
            return False

    def disconnect(self):
        """Disconnect from FPGA"""
        if self.dry_run:
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
                self.logger.info("Disconnected")
            except Exception as e:
                self.logger.warning("Disconnect error: %s", e)

    def _run_tcl(self, tcl_script: str) -> Optional[str]:
        """Execute TCL script via Vivado"""
        tcl_file = Path("/tmp/vio_control_tmp.tcl")
        tcl_file.write_text(tcl_script)

        try:
            result = subprocess.run(
                ["vivado", "-mode", "batch", "-source", str(tcl_file), "-notrace"],
                capture_output=True,
                text=True,
                timeout=30
            )

            tcl_file.unlink()

            if result.returncode != 0:
                self.logger.error("Command failed: %s", result.stderr)
                return None

            return result.stdout

        except Exception as e:
            self.logger.error("Error: %s", e)
            if tcl_file.exists():
                tcl_file.unlink()
            return None

    def read_input_probe(self, probe_idx: int) -> Optional[int]:
        """Read VIO input probe value"""
        if not self.connected:
            return None

        if not (0 <= probe_idx < len(VIO_INPUT_PROBES)):
            self.logger.error("Invalid probe index: %d", probe_idx)
            return None

        probe_name, probe_width, _ = VIO_INPUT_PROBES[probe_idx]

        if self.dry_run:
            self.logger.info("[DRY RUN] Would read %s", probe_name)
            return 0

        tcl_script = f"""
        set vio [get_hw_vios {self.vio_name}]
        refresh_hw_vio [get_hw_vios $vio]
        set value [get_property INPUT_VALUE_RADIX [get_hw_probes $vio/probe_in{probe_idx}]]
        puts "VALUE: $value"
        """

        result = self._run_tcl(tcl_script)
        if result:
            for line in result.split('\n'):
                if line.startswith("VALUE:"):
                    val_str = line.split("VALUE:")[1].strip()
                    try:
                        return int(val_str, 0)
                    except:
                        self.logger.error("Failed to parse value: %s", val_str)
        return None

    def write_output_probe(self, probe_idx: int, value: int) -> bool:
        """Write VIO output probe value"""
        if not self.connected:
            return False

        if not (0 <= probe_idx < len(VIO_OUTPUT_PROBES)):
            self.logger.error("Invalid probe index: %d", probe_idx)
            return False

        probe_name, probe_width, _ = VIO_OUTPUT_PROBES[probe_idx]

        if self.dry_run:
            self.logger.info("[DRY RUN] Would write %s = 0x%X", probe_name, value)
            return True

        # Format value as binary string
        value_bin = format(value, f'0{probe_width}b')

        tcl_script = f"""
        set vio [get_hw_vios {self.vio_name}]
        set_property OUTPUT_VALUE {value_bin} [get_hw_probes $vio/probe_out{probe_idx}]
        commit_hw_vio [get_hw_probes $vio/probe_out{probe_idx}]
        puts "WRITE_OK"
        """

        result = self._run_tcl(tcl_script)
        if result and "WRITE_OK" in result:
            self.logger.info("Wrote %s = 0x%X", probe_name, value)
            return True
        else:
            self.logger.error("Failed to write %s", probe_name)
            return False

    def read_all_inputs(self) -> Dict[str, int]:
        """Read all VIO input probes"""
        values = {}
        for idx, (name, width, desc) in enumerate(VIO_INPUT_PROBES):
            val = self.read_input_probe(idx)
            if val is not None:
                values[name] = val
        return values

    def print_status(self):
        """Print formatted status of all registers"""
        print("\n" + "="*60)
        print("VIO Register Status")
        print("="*60)

        values = self.read_all_inputs()

        for name, value in values.items():
            # Format based on register type
            if name == 'lfsr_state':
                print(f"LFSR State:       0x{value:08X} ({value})")
            elif name == 'sim_state':
                state_name = SIM_STATES.get(value, "UNKNOWN")
                print(f"Sim State:        {value} ({state_name})")
            elif name == 'agent_idx':
                print(f"Agent Index:      {value}/999")
            elif name == 'trail_data_out':
                print(f"Trail Data:       0x{value:02X} ({value})")
            elif name == 'frame_count':
                print(f"Frame Count:      {value}")
            elif name == 'sim_running':
                status = "RUNNING" if value else "STOPPED"
                print(f"Sim Running:      {value} ({status})")
            elif name == 'led_status':
                print(f"LED Status:       0x{value:04X} ({format(value, '016b')})")

        print("="*60 + "\n")

    def freeze(self) -> bool:
        """Freeze simulation"""
        return self.write_output_probe(0, 1)

    def unfreeze(self) -> bool:
        """Unfreeze simulation"""
        return self.write_output_probe(0, 0)

    def set_lfsr_seed(self, seed: int) -> bool:
        """Inject new LFSR seed"""
        self.logger.info("Injecting LFSR seed: 0x%08X", seed)
        return self.write_output_probe(3, seed)

    def read_trail_pixel(self, x: int, y: int) -> Optional[int]:
        """Read trail map pixel via VIO"""
        if not (0 <= x < 160 and 0 <= y < 120):
            self.logger.error("Invalid coordinates")
            return None

        # Calculate address
        addr = y * 160 + x

        # Set address
        if not self.write_output_probe(2, addr):
            return None

        # Enable read
        if not self.write_output_probe(1, 1):
            return None

        # Wait for data
        time.sleep(0.01)

        # Read data
        value = self.read_input_probe(3)

        # Disable read
        self.write_output_probe(1, 0)

        return value

    def monitor_live(self, interval: float = 1.0):
        """Monitor VIO registers in real-time"""
        self.logger.info("Starting live monitor (Ctrl+C to stop)")

        try:
            while True:
                # Clear screen (ANSI escape)
                print("\033[2J\033[H", end='')

                # Print timestamp
                print(f"Live Monitor - {time.strftime('%Y-%m-%d %H:%M:%S')}")

                # Print status
                self.print_status()

                # Wait
                time.sleep(interval)

        except KeyboardInterrupt:
            print("\nMonitoring stopped")


# ============================================================================
# Main CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='VIO Control Tool for Slime Simulator FPGA'
    )

    parser.add_argument('--hw-server', default='localhost:3121',
                        help='Hardware server address')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show commands without executing')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Enable verbose logging')

    # Read operations
    parser.add_argument('--read-all', action='store_true',
                        help='Read all VIO input registers')
    parser.add_argument('--read-lfsr', action='store_true',
                        help='Read LFSR state')
    parser.add_argument('--read-state', action='store_true',
                        help='Read simulation state')
    parser.add_argument('--read-pixel', nargs=2, type=int, metavar=('X', 'Y'),
                        help='Read trail pixel via VIO')

    # Write operations
    parser.add_argument('--freeze', action='store_true',
                        help='Freeze simulation')
    parser.add_argument('--unfreeze', action='store_true',
                        help='Unfreeze simulation')
    parser.add_argument('--set-lfsr-seed', type=lambda x: int(x, 0),
                        help='Inject LFSR seed (hex or decimal)')

    # Monitoring
    parser.add_argument('--monitor', action='store_true',
                        help='Real-time monitor (1 Hz update)')
    parser.add_argument('--interval', type=float, default=1.0,
                        help='Monitor update interval in seconds')

    args = parser.parse_args()

    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    vio = VIOControl(hw_server=args.hw_server, dry_run=args.dry_run)

    if not vio.connect():
        logger.error("Failed to connect to FPGA")
        return 1

    try:
        if args.read_all:
            vio.print_status()

        if args.read_lfsr:
            val = vio.read_input_probe(0)
            if val is not None:
                print(f"LFSR State: 0x{val:08X} ({val})")

        if args.read_state:
            val = vio.read_input_probe(1)
            if val is not None:
                state_name = SIM_STATES.get(val, "UNKNOWN")
                print(f"Sim State: {val} ({state_name})")

        if args.read_pixel:
            x, y = args.read_pixel
            val = vio.read_trail_pixel(x, y)
            if val is not None:
                print(f"Trail[{x}, {y}] = {val}")

        if args.freeze:
            vio.freeze()

        if args.unfreeze:
            vio.unfreeze()

        if args.set_lfsr_seed is not None:
            vio.set_lfsr_seed(args.set_lfsr_seed)

        if args.monitor:
            vio.monitor_live(args.interval)

    finally:
        vio.disconnect()

    return 0


if __name__ == '__main__':
    sys.exit(main())
