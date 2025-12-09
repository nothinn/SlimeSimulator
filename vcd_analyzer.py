#!/usr/bin/env python3
"""
VCD Analyzer - Parse and analyze Verilator VCD waveform files
Useful for debugging RTL simulation issues without GUI
"""

import sys
import re
from collections import defaultdict
from pathlib import Path


class VCDAnalyzer:
    def __init__(self, vcd_file):
        self.vcd_file = Path(vcd_file)
        self.signals = {}  # id -> (scope, name, width)
        self.scopes = []
        self.timescale = None
        self.values = defaultdict(list)  # id -> [(time, value), ...]

    def parse(self):
        """Parse VCD file and extract signal definitions and value changes"""
        print(f"Parsing VCD file: {self.vcd_file}")

        in_definitions = True
        current_scope = []

        with open(self.vcd_file, 'r') as f:
            for line in f:
                line = line.strip()

                if not line or line.startswith('$comment'):
                    continue

                # Parse timescale
                if line.startswith('$timescale'):
                    self.timescale = line.split()[1]

                # Parse scope
                elif line.startswith('$scope'):
                    parts = line.split()
                    if len(parts) >= 3:
                        current_scope.append(parts[2])

                elif line.startswith('$upscope'):
                    if current_scope:
                        current_scope.pop()

                # Parse variable definitions
                elif line.startswith('$var'):
                    parts = line.split()
                    if len(parts) >= 5:
                        var_type = parts[1]
                        width = int(parts[2])
                        var_id = parts[3]
                        var_name = parts[4]
                        scope = '.'.join(current_scope) if current_scope else ''
                        self.signals[var_id] = (scope, var_name, width)

                # End of definitions
                elif line.startswith('$enddefinitions'):
                    in_definitions = False

                # Parse value changes
                elif not in_definitions:
                    if line.startswith('#'):
                        # Timestamp
                        current_time = int(line[1:])
                    else:
                        # Value change: format is either "bXXXX id" or "0id" or "1id"
                        if line.startswith('b'):
                            # Binary value
                            parts = line.split()
                            if len(parts) == 2:
                                value = parts[0][1:]  # Remove 'b' prefix
                                var_id = parts[1]
                                self.values[var_id].append((current_time, value))
                        elif len(line) >= 2:
                            # Single bit value
                            value = line[0]
                            var_id = line[1:]
                            self.values[var_id].append((current_time, value))

    def find_signals(self, pattern):
        """Find signals matching a pattern"""
        matches = []
        for var_id, (scope, name, width) in self.signals.items():
            full_name = f"{scope}.{name}" if scope else name
            if re.search(pattern, full_name, re.IGNORECASE):
                matches.append((var_id, scope, name, width))
        return matches

    def get_signal_value_at_time(self, var_id, time):
        """Get signal value at specific time"""
        if var_id not in self.values:
            return None

        # Find most recent value change before or at this time
        for t, v in reversed(self.values[var_id]):
            if t <= time:
                return v
        return None

    def print_signal_history(self, var_id, max_changes=50):
        """Print value change history for a signal"""
        if var_id not in self.signals:
            print(f"Signal {var_id} not found")
            return

        scope, name, width = self.signals[var_id]
        full_name = f"{scope}.{name}" if scope else name

        print(f"\nSignal: {full_name} (width={width})")
        print("-" * 80)

        if var_id not in self.values:
            print("  No value changes recorded")
            return

        changes = self.values[var_id][:max_changes]
        for time, value in changes:
            # Convert binary string to decimal if it's a multi-bit value
            if width > 1 and value not in ['x', 'z']:
                try:
                    dec_value = int(value, 2)
                    print(f"  @{time:8d}: {value:>20s} (0x{dec_value:X} = {dec_value})")
                except ValueError:
                    print(f"  @{time:8d}: {value:>20s}")
            else:
                print(f"  @{time:8d}: {value}")

        if len(self.values[var_id]) > max_changes:
            print(f"  ... ({len(self.values[var_id]) - max_changes} more changes)")

    def analyze_agent_movement(self):
        """Analyze agent processor and coordinator signals to debug movement issue"""
        print("\n" + "="*80)
        print("ANALYZING AGENT MOVEMENT SIGNALS")
        print("="*80)

        # Find key signals
        proc_done = self.find_signals(r'proc_done')
        proc_start = self.find_signals(r'proc_start')
        latched_valid = self.find_signals(r'latched_valid')
        step_complete = self.find_signals(r'step_complete_pulse')
        current_agent = self.find_signals(r'current_agent_idx')
        agent_x_out = self.find_signals(r'agent_x_out')
        agent_y_out = self.find_signals(r'agent_y_out')

        print(f"\nFound signals:")
        print(f"  proc_done: {len(proc_done)}")
        print(f"  proc_start: {len(proc_start)}")
        print(f"  latched_valid: {len(latched_valid)}")
        print(f"  step_complete_pulse: {len(step_complete)}")
        print(f"  current_agent_idx: {len(current_agent)}")
        print(f"  agent_x_out: {len(agent_x_out)}")

        # Print histories of key signals
        for signals, label in [
            (proc_done, "Processor Done Signal"),
            (proc_start, "Processor Start Signal"),
            (latched_valid, "Latched Valid Signal"),
            (step_complete, "Step Complete Pulse"),
            (current_agent, "Current Agent Index"),
        ]:
            if signals:
                var_id = signals[0][0]
                print(f"\n{label}:")
                self.print_signal_history(var_id, max_changes=30)

        # Analyze timing
        print("\n" + "="*80)
        print("TIMING ANALYSIS")
        print("="*80)

        if proc_done and latched_valid:
            proc_done_id = proc_done[0][0]
            latched_id = latched_valid[0][0]

            print("\nChecking proc_done and latched_valid correlation:")
            proc_done_times = [(t, v) for t, v in self.values[proc_done_id] if v == '1']

            if proc_done_times:
                print(f"\nproc_done rises {len(proc_done_times)} times:")
                for i, (t, v) in enumerate(proc_done_times[:10]):
                    latched_val = self.get_signal_value_at_time(latched_id, t + 10)
                    print(f"  proc_done @ {t:8d}, latched_valid @ {t+10:8d} = {latched_val}")
            else:
                print("\n  WARNING: proc_done NEVER goes high!")

        # Check if agents are being processed
        if current_agent:
            agent_id = current_agent[0][0]
            changes = self.values[agent_id]

            print(f"\nAgent processing sequence ({len(changes)} changes):")
            for t, v in changes[:20]:
                try:
                    agent_num = int(v, 2) if v not in ['x', 'z'] else v
                    print(f"  @{t:8d}: Agent {agent_num}")
                except ValueError:
                    print(f"  @{t:8d}: {v}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 vcd_analyzer.py <vcd_file>")
        print("\nExample: python3 vcd_analyzer.py rtl/sim/slime_verilator_full.vcd")
        sys.exit(1)

    vcd_file = sys.argv[1]

    if not Path(vcd_file).exists():
        print(f"Error: VCD file not found: {vcd_file}")
        sys.exit(1)

    analyzer = VCDAnalyzer(vcd_file)
    analyzer.parse()

    print(f"\nParsed {len(analyzer.signals)} signals")
    print(f"Timescale: {analyzer.timescale}")

    # Run analysis
    analyzer.analyze_agent_movement()

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)


if __name__ == '__main__':
    main()
