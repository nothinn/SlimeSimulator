#!/usr/bin/env python3
"""
JTAG Inspector for Slime Simulator FPGA Debug
==============================================

Comprehensive JTAG interface tool for accessing FPGA debug features.
Provides read/write access to FPGA internal state via Vivado Hardware Manager.

Features:
- Read LFSR state (32-bit random number generator)
- Read simulation state machine value
- Read current agent index being processed
- Read frame counter (~60 Hz display refresh)
- Freeze/unfreeze simulation
- Read entire 160x120 trail map to binary/PNG
- Read single trail map pixels
- Compare FPGA output with Python reference

Requirements:
- Vivado Hardware Manager running (hw_server)
- FPGA programmed with debug-enabled bitstream
- Python packages: subprocess, struct, numpy, PIL

Usage:
    # Read current LFSR state
    ./jtag_inspect.py --read-lfsr

    # Read simulation state
    ./jtag_inspect.py --read-state

    # Freeze simulation for inspection
    ./jtag_inspect.py --freeze

    # Dump entire trail map to file
    ./jtag_inspect.py --dump-trail-map output.bin

    # Read single pixel
    ./jtag_inspect.py --read-pixel 80 60

    # Compare with Python reference
    ./jtag_inspect.py --compare fpga_trail.bin python_trail.bin

Author: Claude (Anthropic)
Date: 2025-11-25
"""

import subprocess
import argparse
import sys
import os
import struct
import time
from pathlib import Path
from typing import Optional, Tuple, List
import logging

# Optional imports for advanced features
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("Warning: numpy not available, some features disabled")

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: PIL not available, PNG export disabled")


# ============================================================================
# Constants
# ============================================================================

TRAIL_MAP_WIDTH = 160
TRAIL_MAP_HEIGHT = 120
TRAIL_MAP_SIZE = TRAIL_MAP_WIDTH * TRAIL_MAP_HEIGHT  # 19200 bytes

# AXI address map (configured in debug build)
# Base address for trail map access via JTAG-to-AXI
AXI_TRAIL_MAP_BASE = 0x44A00000

# VIO register offsets (for simulation control)
VIO_FREEZE_ADDR = 0x44A10000
VIO_READ_EN_ADDR = 0x44A10004
VIO_READ_ADDR = 0x44A10008

# VIO input probe addresses (read-only status)
VIO_LFSR_STATE_ADDR = 0x44A10100
VIO_SIM_STATE_ADDR = 0x44A10104
VIO_AGENT_IDX_ADDR = 0x44A10108
VIO_TRAIL_DATA_ADDR = 0x44A1010C
VIO_FRAME_COUNT_ADDR = 0x44A10110
VIO_SIM_RUNNING_ADDR = 0x44A10114
VIO_LED_STATUS_ADDR = 0x44A10118

# Simulation state machine values
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
# JTAG Communication via Vivado TCL
# ============================================================================

class JTAGInterface:
    """Interface to FPGA via Vivado Hardware Manager and JTAG-to-AXI"""

    def __init__(self, hw_server: str = "localhost:3121", dry_run: bool = False):
        """
        Initialize JTAG interface

        Args:
            hw_server: Hardware server address (localhost:3121 by default)
            dry_run: If True, show commands without executing
        """
        self.hw_server = hw_server
        self.dry_run = dry_run
        self.hw_target = None
        self.hw_device = None
        self.connected = False
        self.logger = logging.getLogger(__name__)

        # Track connection for resource cleanup
        self._tcl_commands = []

    def connect(self) -> bool:
        """
        Connect to FPGA via Vivado Hardware Manager

        Returns:
            True if connection successful, False otherwise
        """
        if self.dry_run:
            self.logger.info("[DRY RUN] Would connect to %s", self.hw_server)
            self.connected = True
            return True

        tcl_script = f"""
        # Connect to hardware server
        open_hw_manager
        connect_hw_server -url {self.hw_server}

        # Get target
        set targets [get_hw_targets]
        if {{[llength $targets] == 0}} {{
            puts "ERROR: No hardware targets found"
            exit 1
        }}

        current_hw_target [lindex $targets 0]
        open_hw_target

        # Get device
        set devices [get_hw_devices]
        if {{[llength $devices] == 0}} {{
            puts "ERROR: No hardware devices found"
            exit 1
        }}

        current_hw_device [lindex $devices 0]
        puts "Connected to [get_property PART [current_hw_device]]"
        """

        try:
            result = self._run_tcl(tcl_script)
            if result and "Connected to" in result:
                self.connected = True
                self.logger.info("Connected to FPGA: %s", result.split("Connected to")[1].strip())
                return True
            else:
                self.logger.error("Failed to connect to FPGA")
                return False
        except Exception as e:
            self.logger.error("Connection error: %s", e)
            return False

    def disconnect(self):
        """Disconnect from FPGA and close hardware manager"""
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
        """
        Execute TCL script via Vivado batch mode

        Args:
            tcl_script: TCL commands to execute

        Returns:
            Command output as string, or None on error
        """
        # Write TCL script to temporary file
        tcl_file = Path("/tmp/jtag_inspect_tmp.tcl")
        tcl_file.write_text(tcl_script)

        try:
            # Run Vivado in batch mode
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
                timeout=30
            )

            # Clean up temp file
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

    def read_axi(self, address: int, num_bytes: int = 4) -> Optional[bytes]:
        """
        Read data from FPGA via JTAG-to-AXI

        Args:
            address: AXI address to read from
            num_bytes: Number of bytes to read (must be multiple of 4)

        Returns:
            Bytes read, or None on error
        """
        if not self.connected:
            self.logger.error("Not connected to FPGA")
            return None

        if num_bytes % 4 != 0:
            self.logger.error("num_bytes must be multiple of 4")
            return None

        if self.dry_run:
            self.logger.info("[DRY RUN] Would read %d bytes from 0x%08X", num_bytes, address)
            return b'\x00' * num_bytes

        # Read in 4-byte chunks (AXI word size)
        num_words = num_bytes // 4
        data = bytearray()

        for i in range(num_words):
            addr = address + (i * 4)

            tcl_script = f"""
            # Read single AXI word
            set axi_masters [get_hw_axis]
            if {{[llength $axi_masters] == 0}} {{
                puts "ERROR: No AXI masters found (JTAG-to-AXI missing?)"
                exit 1
            }}

            set axi_master [lindex $axi_masters 0]
            set value [read_hw_axi -address 0x{addr:08X} $axi_master]
            puts "READ: $value"
            """

            result = self._run_tcl(tcl_script)
            if not result:
                self.logger.error("Failed to read from 0x%08X", addr)
                return None

            # Parse result
            for line in result.split('\n'):
                if line.startswith("READ:"):
                    hex_value = line.split("READ:")[1].strip()
                    # Convert hex string to bytes (little-endian)
                    word_value = int(hex_value, 16)
                    data.extend(struct.pack('<I', word_value))
                    break

        return bytes(data)

    def write_axi(self, address: int, data: bytes) -> bool:
        """
        Write data to FPGA via JTAG-to-AXI

        Args:
            address: AXI address to write to
            data: Bytes to write (must be multiple of 4)

        Returns:
            True on success, False on error
        """
        if not self.connected:
            self.logger.error("Not connected to FPGA")
            return False

        if len(data) % 4 != 0:
            self.logger.error("Data length must be multiple of 4")
            return False

        if self.dry_run:
            self.logger.info("[DRY RUN] Would write %d bytes to 0x%08X", len(data), address)
            return True

        # Write in 4-byte chunks
        num_words = len(data) // 4

        for i in range(num_words):
            addr = address + (i * 4)
            word_bytes = data[i*4:(i+1)*4]
            word_value = struct.unpack('<I', word_bytes)[0]

            tcl_script = f"""
            # Write single AXI word
            set axi_masters [get_hw_axis]
            if {{[llength $axi_masters] == 0}} {{
                puts "ERROR: No AXI masters found"
                exit 1
            }}

            set axi_master [lindex $axi_masters 0]
            write_hw_axi -address 0x{addr:08X} -data 0x{word_value:08X} $axi_master
            puts "WRITE OK"
            """

            result = self._run_tcl(tcl_script)
            if not result or "WRITE OK" not in result:
                self.logger.error("Failed to write to 0x%08X", addr)
                return False

        return True


# ============================================================================
# High-Level FPGA Inspection Functions
# ============================================================================

class FPGAInspector:
    """High-level interface for inspecting FPGA state"""

    def __init__(self, jtag: JTAGInterface):
        """Initialize inspector with JTAG interface"""
        self.jtag = jtag
        self.logger = logging.getLogger(__name__)

    def read_lfsr_state(self) -> Optional[int]:
        """
        Read current 32-bit LFSR random number generator state

        Returns:
            32-bit LFSR value, or None on error
        """
        data = self.jtag.read_axi(VIO_LFSR_STATE_ADDR, 4)
        if data:
            value = struct.unpack('<I', data)[0]
            self.logger.info("LFSR State: 0x%08X (%u)", value, value)
            return value
        return None

    def read_sim_state(self) -> Optional[Tuple[int, str]]:
        """
        Read current simulation state machine value

        Returns:
            Tuple of (state_value, state_name), or None on error
        """
        data = self.jtag.read_axi(VIO_SIM_STATE_ADDR, 4)
        if data:
            value = struct.unpack('<I', data)[0] & 0xF  # 4-bit state
            name = SIM_STATES.get(value, "UNKNOWN")
            self.logger.info("Simulation State: %d (%s)", value, name)
            return (value, name)
        return None

    def read_agent_index(self) -> Optional[int]:
        """
        Read current agent index being processed (0-999)

        Returns:
            Agent index, or None on error
        """
        data = self.jtag.read_axi(VIO_AGENT_IDX_ADDR, 4)
        if data:
            value = struct.unpack('<I', data)[0] & 0x3FF  # 10-bit index
            self.logger.info("Agent Index: %d", value)
            return value
        return None

    def read_frame_count(self) -> Optional[int]:
        """
        Read VGA frame counter (~60 Hz)

        Returns:
            Frame count, or None on error
        """
        data = self.jtag.read_axi(VIO_FRAME_COUNT_ADDR, 4)
        if data:
            value = struct.unpack('<I', data)[0]
            self.logger.info("Frame Count: %u", value)
            return value
        return None

    def read_sim_running(self) -> Optional[bool]:
        """
        Check if simulation is currently running

        Returns:
            True if running, False if paused, None on error
        """
        data = self.jtag.read_axi(VIO_SIM_RUNNING_ADDR, 4)
        if data:
            value = struct.unpack('<I', data)[0] & 0x1
            running = bool(value)
            self.logger.info("Simulation Running: %s", running)
            return running
        return None

    def read_led_status(self) -> Optional[int]:
        """
        Read current LED status (16 bits)

        Returns:
            16-bit LED value, or None on error
        """
        data = self.jtag.read_axi(VIO_LED_STATUS_ADDR, 4)
        if data:
            value = struct.unpack('<I', data)[0] & 0xFFFF
            self.logger.info("LED Status: 0x%04X (binary: %s)", value, format(value, '016b'))
            return value
        return None

    def freeze_simulation(self) -> bool:
        """
        Freeze simulation for inspection (stops agent processing)

        Returns:
            True on success, False on error
        """
        self.logger.info("Freezing simulation...")
        data = struct.pack('<I', 1)
        return self.jtag.write_axi(VIO_FREEZE_ADDR, data)

    def unfreeze_simulation(self) -> bool:
        """
        Unfreeze simulation (resume agent processing)

        Returns:
            True on success, False on error
        """
        self.logger.info("Unfreezing simulation...")
        data = struct.pack('<I', 0)
        return self.jtag.write_axi(VIO_FREEZE_ADDR, data)

    def read_trail_at_xy(self, x: int, y: int) -> Optional[int]:
        """
        Read single trail map pixel value at (x, y)

        Args:
            x: X coordinate (0-159)
            y: Y coordinate (0-119)

        Returns:
            8-bit trail intensity value, or None on error
        """
        if not (0 <= x < TRAIL_MAP_WIDTH and 0 <= y < TRAIL_MAP_HEIGHT):
            self.logger.error("Coordinates out of range: (%d, %d)", x, y)
            return None

        # Calculate linear address
        addr = y * TRAIL_MAP_WIDTH + x
        byte_addr = AXI_TRAIL_MAP_BASE + addr

        # Read 4 bytes (AXI word), extract our byte
        data = self.jtag.read_axi(byte_addr & ~0x3, 4)
        if data:
            # Extract correct byte from word
            byte_offset = byte_addr & 0x3
            value = data[byte_offset]
            self.logger.info("Trail[%d, %d] = %d", x, y, value)
            return value
        return None

    def read_trail_map(self) -> Optional[bytes]:
        """
        Read entire 160x120 trail map from FPGA

        Returns:
            19200 bytes of trail map data, or None on error
        """
        self.logger.info("Reading entire trail map (%d bytes)...", TRAIL_MAP_SIZE)

        # Read in chunks for better performance
        chunk_size = 1024  # 256 words
        data = bytearray()

        for offset in range(0, TRAIL_MAP_SIZE, chunk_size):
            remaining = min(chunk_size, TRAIL_MAP_SIZE - offset)

            # Round up to nearest word
            read_size = ((remaining + 3) // 4) * 4

            chunk_data = self.jtag.read_axi(AXI_TRAIL_MAP_BASE + offset, read_size)
            if not chunk_data:
                self.logger.error("Failed to read chunk at offset %d", offset)
                return None

            # Only append the bytes we need
            data.extend(chunk_data[:remaining])

            # Progress indicator
            progress = (offset + remaining) * 100 // TRAIL_MAP_SIZE
            self.logger.debug("Progress: %d%%", progress)

        self.logger.info("Trail map read complete")
        return bytes(data)

    def save_trail_map(self, filename: str, data: Optional[bytes] = None) -> bool:
        """
        Save trail map to binary file

        Args:
            filename: Output filename (.bin)
            data: Trail map data (if None, will read from FPGA)

        Returns:
            True on success, False on error
        """
        if data is None:
            data = self.read_trail_map()
            if not data:
                return False

        try:
            with open(filename, 'wb') as f:
                f.write(data)
            self.logger.info("Saved trail map to %s", filename)
            return True
        except Exception as e:
            self.logger.error("Failed to save trail map: %s", e)
            return False

    def save_trail_map_png(self, filename: str, data: Optional[bytes] = None) -> bool:
        """
        Save trail map as PNG image

        Args:
            filename: Output filename (.png)
            data: Trail map data (if None, will read from FPGA)

        Returns:
            True on success, False on error
        """
        if not PIL_AVAILABLE:
            self.logger.error("PIL not available, cannot save PNG")
            return False

        if not NUMPY_AVAILABLE:
            self.logger.error("numpy not available, cannot save PNG")
            return False

        if data is None:
            data = self.read_trail_map()
            if not data:
                return False

        try:
            # Convert to numpy array
            arr = np.frombuffer(data, dtype=np.uint8)
            arr = arr.reshape((TRAIL_MAP_HEIGHT, TRAIL_MAP_WIDTH))

            # Create image
            img = Image.fromarray(arr, mode='L')
            img.save(filename)

            self.logger.info("Saved trail map PNG to %s", filename)
            return True
        except Exception as e:
            self.logger.error("Failed to save PNG: %s", e)
            return False


# ============================================================================
# Comparison Functions
# ============================================================================

def compare_trail_maps(fpga_data: bytes, python_data: bytes) -> dict:
    """
    Compare FPGA trail map with Python reference

    Args:
        fpga_data: Trail map from FPGA (19200 bytes)
        python_data: Trail map from Python reference (19200 bytes)

    Returns:
        Dictionary with comparison statistics
    """
    if len(fpga_data) != TRAIL_MAP_SIZE or len(python_data) != TRAIL_MAP_SIZE:
        raise ValueError("Invalid trail map size")

    # Convert to numpy if available
    if NUMPY_AVAILABLE:
        fpga_arr = np.frombuffer(fpga_data, dtype=np.uint8)
        python_arr = np.frombuffer(python_data, dtype=np.uint8)

        # Calculate statistics
        diff = fpga_arr.astype(np.int16) - python_arr.astype(np.int16)

        stats = {
            'total_pixels': TRAIL_MAP_SIZE,
            'matching_pixels': np.sum(fpga_arr == python_arr),
            'match_percentage': float(np.sum(fpga_arr == python_arr)) * 100.0 / TRAIL_MAP_SIZE,
            'max_error': int(np.max(np.abs(diff))),
            'mean_error': float(np.mean(np.abs(diff))),
            'std_error': float(np.std(diff)),
            'different_pixels': int(np.sum(fpga_arr != python_arr))
        }
    else:
        # Fallback to pure Python
        matching = sum(1 for a, b in zip(fpga_data, python_data) if a == b)
        errors = [abs(a - b) for a, b in zip(fpga_data, python_data)]

        stats = {
            'total_pixels': TRAIL_MAP_SIZE,
            'matching_pixels': matching,
            'match_percentage': matching * 100.0 / TRAIL_MAP_SIZE,
            'max_error': max(errors),
            'mean_error': sum(errors) / len(errors),
            'different_pixels': TRAIL_MAP_SIZE - matching
        }

    return stats


# ============================================================================
# Main CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='JTAG Inspector for Slime Simulator FPGA',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --read-lfsr
  %(prog)s --read-state
  %(prog)s --read-all
  %(prog)s --freeze
  %(prog)s --unfreeze
  %(prog)s --dump-trail-map fpga_trail.bin
  %(prog)s --dump-trail-png fpga_trail.png
  %(prog)s --read-pixel 80 60
  %(prog)s --compare fpga_trail.bin python_trail.bin
        """
    )

    parser.add_argument('--hw-server', default='localhost:3121',
                        help='Hardware server address (default: localhost:3121)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show commands without executing')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Enable verbose logging')

    # Read operations
    parser.add_argument('--read-lfsr', action='store_true',
                        help='Read LFSR state')
    parser.add_argument('--read-state', action='store_true',
                        help='Read simulation state')
    parser.add_argument('--read-agent', action='store_true',
                        help='Read current agent index')
    parser.add_argument('--read-frame', action='store_true',
                        help='Read frame counter')
    parser.add_argument('--read-leds', action='store_true',
                        help='Read LED status')
    parser.add_argument('--read-all', action='store_true',
                        help='Read all status registers')

    # Control operations
    parser.add_argument('--freeze', action='store_true',
                        help='Freeze simulation')
    parser.add_argument('--unfreeze', action='store_true',
                        help='Unfreeze simulation')

    # Trail map operations
    parser.add_argument('--dump-trail-map', metavar='FILE',
                        help='Dump trail map to binary file')
    parser.add_argument('--dump-trail-png', metavar='FILE',
                        help='Dump trail map to PNG image')
    parser.add_argument('--read-pixel', nargs=2, type=int, metavar=('X', 'Y'),
                        help='Read single pixel at (X, Y)')

    # Comparison
    parser.add_argument('--compare', nargs=2, metavar=('FPGA_FILE', 'PYTHON_FILE'),
                        help='Compare FPGA trail map with Python reference')

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    # Create JTAG interface
    jtag = JTAGInterface(hw_server=args.hw_server, dry_run=args.dry_run)
    inspector = FPGAInspector(jtag)

    # Connect to FPGA (unless doing comparison only)
    if not args.compare:
        if not jtag.connect():
            logger.error("Failed to connect to FPGA")
            return 1

    try:
        # Execute requested operations
        if args.read_lfsr or args.read_all:
            inspector.read_lfsr_state()

        if args.read_state or args.read_all:
            inspector.read_sim_state()

        if args.read_agent or args.read_all:
            inspector.read_agent_index()

        if args.read_frame or args.read_all:
            inspector.read_frame_count()

        if args.read_leds or args.read_all:
            inspector.read_led_status()

        if args.freeze:
            inspector.freeze_simulation()

        if args.unfreeze:
            inspector.unfreeze_simulation()

        if args.dump_trail_map:
            inspector.save_trail_map(args.dump_trail_map)

        if args.dump_trail_png:
            inspector.save_trail_map_png(args.dump_trail_png)

        if args.read_pixel:
            x, y = args.read_pixel
            inspector.read_trail_at_xy(x, y)

        if args.compare:
            fpga_file, python_file = args.compare

            # Load both files
            with open(fpga_file, 'rb') as f:
                fpga_data = f.read()
            with open(python_file, 'rb') as f:
                python_data = f.read()

            # Compare
            stats = compare_trail_maps(fpga_data, python_data)

            print("\n=== Trail Map Comparison ===")
            print(f"Total pixels:      {stats['total_pixels']}")
            print(f"Matching pixels:   {stats['matching_pixels']}")
            print(f"Different pixels:  {stats['different_pixels']}")
            print(f"Match percentage:  {stats['match_percentage']:.2f}%")
            print(f"Max error:         {stats['max_error']}")
            print(f"Mean error:        {stats['mean_error']:.2f}")
            if 'std_error' in stats:
                print(f"Std error:         {stats['std_error']:.2f}")

            if stats['match_percentage'] == 100.0:
                print("\nRESULT: PERFECT MATCH!")
            elif stats['match_percentage'] > 95.0:
                print("\nRESULT: VERY GOOD MATCH")
            elif stats['match_percentage'] > 90.0:
                print("\nRESULT: GOOD MATCH")
            else:
                print("\nRESULT: POOR MATCH - investigate differences")

    finally:
        # Always disconnect
        if not args.compare:
            jtag.disconnect()

    return 0


if __name__ == '__main__':
    sys.exit(main())
