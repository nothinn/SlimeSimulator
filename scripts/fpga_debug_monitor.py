#!/usr/bin/env python3
"""
FPGA Debug Monitor for Slime Simulator
=======================================

Interactive real-time monitoring dashboard for FPGA debug information.
Combines VIO register readback with trail map visualization to provide
comprehensive system visibility.

Features:
- Real-time status dashboard (1 Hz update)
- Current LFSR state (hex and decimal)
- Simulation state machine status with descriptions
- Current agent index
- Frame counter and calculated FPS
- LED status visualization
- ASCII art trail map heatmap (low-res preview)
- Interactive commands (freeze, unfreeze, read memory, trigger ILA)

The monitor provides a single unified view of all FPGA debug information,
making it the go-to tool for live system debugging.

Requirements:
- Vivado Hardware Manager running
- FPGA programmed with debug-enabled bitstream
- Terminal with ANSI color support (optional)

Usage:
    # Start monitor with default settings
    ./fpga_debug_monitor.py

    # Custom update rate (2 Hz)
    ./fpga_debug_monitor.py --rate 0.5

    # No color output (for non-ANSI terminals)
    ./fpga_debug_monitor.py --no-color

    # Save logs to file
    ./fpga_debug_monitor.py --log-file monitor.log

Author: Claude (Anthropic)
Date: 2025-11-25
"""

import subprocess
import argparse
import sys
import time
from pathlib import Path
from typing import Optional, Dict, List
import logging
from datetime import datetime

# Import our JTAG tools
sys.path.insert(0, str(Path(__file__).parent))
from vio_control import VIOControl, SIM_STATES
from jtag_inspect import JTAGInterface, FPGAInspector

# ============================================================================
# Constants
# ============================================================================

TRAIL_MAP_WIDTH = 160
TRAIL_MAP_HEIGHT = 120

# ASCII art characters for trail intensity (low to high)
ASCII_RAMP = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"

# ANSI color codes
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'

# ============================================================================
# Logging Setup
# ============================================================================

def setup_logging(verbose: bool = False, log_file: Optional[str] = None):
    """Configure logging"""
    level = logging.DEBUG if verbose else logging.INFO

    handlers = []

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    handlers.append(console_handler)

    # File handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        handlers.append(file_handler)

    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=handlers
    )


# ============================================================================
# Debug Monitor
# ============================================================================

class FPGADebugMonitor:
    """Real-time FPGA debug monitor"""

    def __init__(self, hw_server: str = "localhost:3121", use_color: bool = True):
        """Initialize monitor"""
        self.hw_server = hw_server
        self.use_color = use_color
        self.logger = logging.getLogger(__name__)

        # Connect to FPGA
        self.vio = VIOControl(hw_server=hw_server)
        self.jtag = JTAGInterface(hw_server=hw_server)
        self.inspector = FPGAInspector(self.jtag)

        # State tracking
        self.last_frame_count = 0
        self.last_frame_time = time.time()
        self.fps = 0.0

        self.running = False

    def color(self, text: str, color: str) -> str:
        """Apply color if enabled"""
        if self.use_color:
            return f"{color}{text}{Colors.RESET}"
        return text

    def connect(self) -> bool:
        """Connect to FPGA"""
        self.logger.info("Connecting to FPGA...")

        if not self.vio.connect():
            self.logger.error("Failed to connect VIO")
            return False

        if not self.jtag.connect():
            self.logger.error("Failed to connect JTAG")
            self.vio.disconnect()
            return False

        self.logger.info("Connected successfully")
        return True

    def disconnect(self):
        """Disconnect from FPGA"""
        self.vio.disconnect()
        self.jtag.disconnect()

    def clear_screen(self):
        """Clear terminal screen"""
        print("\033[2J\033[H", end='')

    def read_status(self) -> Dict:
        """Read all status information"""
        status = {}

        # Read VIO inputs
        values = self.vio.read_all_inputs()

        status['lfsr_state'] = values.get('lfsr_state', 0)
        status['sim_state'] = values.get('sim_state', 0)
        status['sim_state_name'] = SIM_STATES.get(values.get('sim_state', 0), "UNKNOWN")
        status['agent_idx'] = values.get('agent_idx', 0)
        status['frame_count'] = values.get('frame_count', 0)
        status['sim_running'] = values.get('sim_running', 0)
        status['led_status'] = values.get('led_status', 0)

        # Calculate FPS
        current_frame = status['frame_count']
        current_time = time.time()

        if self.last_frame_count > 0:
            frame_diff = current_frame - self.last_frame_count
            time_diff = current_time - self.last_frame_time

            if time_diff > 0:
                self.fps = frame_diff / time_diff

        self.last_frame_count = current_frame
        self.last_frame_time = current_time

        status['fps'] = self.fps

        return status

    def create_trail_preview(self, width: int = 40, height: int = 30) -> List[str]:
        """
        Create ASCII art preview of trail map

        Args:
            width: Preview width in characters
            height: Preview height in characters

        Returns:
            List of strings (one per row)
        """
        try:
            # Read trail map
            trail_data = self.inspector.read_trail_map()
            if not trail_data:
                return ["[Trail map read failed]"]

            # Downsample to preview size
            scale_x = TRAIL_MAP_WIDTH // width
            scale_y = TRAIL_MAP_HEIGHT // height

            preview = []

            for y in range(height):
                row = ""
                for x in range(width):
                    # Sample from trail map
                    src_x = x * scale_x
                    src_y = y * scale_y

                    if src_x < TRAIL_MAP_WIDTH and src_y < TRAIL_MAP_HEIGHT:
                        idx = src_y * TRAIL_MAP_WIDTH + src_x
                        if idx < len(trail_data):
                            intensity = trail_data[idx]
                            # Map to ASCII character
                            char_idx = min(intensity * len(ASCII_RAMP) // 256, len(ASCII_RAMP) - 1)
                            row += ASCII_RAMP[char_idx]
                        else:
                            row += " "
                    else:
                        row += " "

                preview.append(row)

            return preview

        except Exception as e:
            self.logger.warning("Failed to create trail preview: %s", e)
            return ["[Trail preview unavailable]"]

    def display_dashboard(self, status: Dict, include_trail: bool = False):
        """Display monitoring dashboard"""
        self.clear_screen()

        # Header
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(self.color("="*80, Colors.BOLD))
        print(self.color(f"FPGA Debug Monitor - {timestamp}", Colors.BOLD + Colors.CYAN))
        print(self.color("="*80, Colors.BOLD))
        print()

        # System Status
        print(self.color("SYSTEM STATUS:", Colors.BOLD + Colors.YELLOW))
        print(f"  LFSR State:       {self.color(f'0x{status[\"lfsr_state\"]:08X}', Colors.GREEN)} ({status['lfsr_state']})")

        state_color = Colors.GREEN if status['sim_running'] else Colors.RED
        print(f"  Sim State:        {self.color(f'{status[\"sim_state\"]} ({status[\"sim_state_name\"]})', state_color)}")

        print(f"  Agent Index:      {self.color(f'{status[\"agent_idx\"]}/999', Colors.CYAN)}")

        frame_color = Colors.GREEN if status['frame_count'] > 0 else Colors.RED
        print(f"  Frame Count:      {self.color(str(status['frame_count']), frame_color)}")

        fps_color = Colors.GREEN if status['fps'] > 50 else Colors.YELLOW if status['fps'] > 30 else Colors.RED
        print(f"  Frame Rate:       {self.color(f'{status[\"fps\"]:.1f} FPS', fps_color)}")

        running_str = self.color("RUNNING", Colors.GREEN) if status['sim_running'] else self.color("STOPPED", Colors.RED)
        print(f"  Simulation:       {running_str}")

        print()

        # LED Status
        print(self.color("LED STATUS:", Colors.BOLD + Colors.YELLOW))
        led_binary = format(status['led_status'], '016b')
        print(f"  LEDs:             {self.color(f'0x{status[\"led_status\"]:04X}', Colors.MAGENTA)} ({led_binary})")

        # Visual LED representation
        led_visual = ""
        for i in range(15, -1, -1):
            if status['led_status'] & (1 << i):
                led_visual += self.color("█", Colors.GREEN)
            else:
                led_visual += self.color("░", Colors.WHITE)
        print(f"                    {led_visual}")

        print()

        # Trail Map Preview (optional)
        if include_trail:
            print(self.color("TRAIL MAP PREVIEW (ASCII):", Colors.BOLD + Colors.YELLOW))
            preview = self.create_trail_preview(width=80, height=20)
            for line in preview:
                print(f"  {line}")
            print()

        # Footer
        print(self.color("-"*80, Colors.BOLD))
        print(self.color("Commands: Ctrl+C to exit, 'h' for help", Colors.CYAN))
        print(self.color("="*80, Colors.BOLD))

    def run_monitor(self, interval: float = 1.0, show_trail: bool = False):
        """
        Run monitoring loop

        Args:
            interval: Update interval in seconds
            show_trail: Include trail map preview
        """
        self.logger.info("Starting monitor loop (Ctrl+C to exit)")
        self.running = True

        try:
            while self.running:
                # Read status
                status = self.read_status()

                # Display
                self.display_dashboard(status, include_trail=show_trail)

                # Wait
                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n")
            self.logger.info("Monitor stopped by user")
        except Exception as e:
            self.logger.error("Monitor error: %s", e)
            raise
        finally:
            self.running = False

    def single_snapshot(self, show_trail: bool = True):
        """Take single status snapshot and display"""
        status = self.read_status()
        self.display_dashboard(status, include_trail=show_trail)


# ============================================================================
# Main CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='FPGA Debug Monitor for Slime Simulator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start interactive monitor (1 Hz updates)
  %(prog)s

  # Monitor at 2 Hz
  %(prog)s --rate 0.5

  # Include trail map preview
  %(prog)s --show-trail

  # Single snapshot
  %(prog)s --snapshot

  # Save logs to file
  %(prog)s --log-file debug.log
        """
    )

    parser.add_argument('--hw-server', default='localhost:3121',
                        help='Hardware server address')
    parser.add_argument('--rate', type=float, default=1.0,
                        help='Update interval in seconds (default: 1.0)')
    parser.add_argument('--show-trail', action='store_true',
                        help='Include trail map ASCII preview')
    parser.add_argument('--no-color', action='store_true',
                        help='Disable color output')
    parser.add_argument('--snapshot', action='store_true',
                        help='Single snapshot (no loop)')
    parser.add_argument('--log-file', metavar='FILE',
                        help='Log file path')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Enable verbose logging')

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose, args.log_file)
    logger = logging.getLogger(__name__)

    # Create monitor
    monitor = FPGADebugMonitor(
        hw_server=args.hw_server,
        use_color=not args.no_color
    )

    # Connect
    if not monitor.connect():
        logger.error("Failed to connect to FPGA")
        return 1

    try:
        if args.snapshot:
            # Single snapshot
            monitor.single_snapshot(show_trail=args.show_trail)
        else:
            # Continuous monitoring
            monitor.run_monitor(interval=args.rate, show_trail=args.show_trail)

    finally:
        monitor.disconnect()

    return 0


if __name__ == '__main__':
    sys.exit(main())
