#!/usr/bin/env python3
"""
Generate C++ Agent Initialization Code from Python Reference

This script uses the Python reference implementation to compute the exact
circle spawn pattern for agents, then outputs C++ code to initialize the
RTL testbench with these pre-computed values.

Usage:
    python generate_cpp_agent_init.py [--num-agents N] [--width W] [--height H]
"""

import numpy as np
import math
import argparse
import sys
from pathlib import Path

# Add parent directory to path to import slime_simulator
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from slime_simulator import FixedPoint, TrigLUT


def generate_circle_spawn_agents(num_agents, width, height, int_bits=12, frac_bits=12):
    """
    Generate agent initialization using exact circle spawn pattern.

    This matches the Python reference implementation (slime_simulator.py)
    spawn_pattern='circle' logic.

    Returns:
        List of (x_fp, y_fp, angle_fp) tuples in fixed-point representation
    """
    # Initialize fixed-point system
    fp = FixedPoint(int_bits, frac_bits)

    # Initialize trig lookup table (1024 entries)
    trig = TrigLUT(fp, table_bits=10)

    # Calculate center coordinates (fixed-point)
    cx_fp = fp.to_fixed(width / 2.0)
    cy_fp = fp.to_fixed(height / 2.0)

    # Calculate spawn radius: 40% of min(width, height)
    radius_px = min(width, height) * 0.4
    radius_fp = fp.to_fixed(radius_px)

    print(f"Circle spawn parameters:")
    print(f"  Center: ({width/2.0:.2f}, {height/2.0:.2f}) px")
    print(f"  Radius: {radius_px:.2f} px")
    print(f"  Fixed-point scale: {fp.scale} (2^{frac_bits})")
    print()

    # Generate agents
    agents = []

    for i in range(num_agents):
        # Spawn angle: 2π * i / num_agents (evenly distributed around circle)
        spawn_angle_rad = 2.0 * math.pi * i / num_agents
        spawn_angle_fp = fp.to_fixed(spawn_angle_rad)

        # Calculate position on circle: (cx + cos(θ)*r, cy + sin(θ)*r)
        cos_val = trig.cos_array(np.array([spawn_angle_fp], dtype=np.int64))[0]
        sin_val = trig.sin_array(np.array([spawn_angle_fp], dtype=np.int64))[0]

        # x = cx + cos(angle) * radius
        x_fp = cx_fp + fp.multiply(cos_val, radius_fp)

        # y = cy + sin(angle) * radius
        y_fp = cy_fp + fp.multiply(sin_val, radius_fp)

        # Agent angle: point toward center (spawn_angle + π)
        # This makes agents point inward toward the center
        pi_fp = fp.to_fixed(math.pi)
        two_pi_fp = fp.to_fixed(2.0 * math.pi)

        angle_fp = spawn_angle_fp + pi_fp

        # Normalize angle to [0, 2π)
        if angle_fp >= two_pi_fp:
            angle_fp -= two_pi_fp

        agents.append((x_fp, y_fp, angle_fp))

    return agents, fp


def format_cpp_array(agents, fp):
    """
    Format agent data as C++ initialization code.

    Returns:
        String containing C++ array initialization code
    """
    lines = []
    lines.append("// Agent initialization data (circle spawn, 40% radius, pointing inward)")
    lines.append("// Format: {x_fp, y_fp, angle_fp} for each agent")
    lines.append("// Fixed-point: Q12.12 (scale = 4096)")
    lines.append("")
    lines.append("const int32_t AGENT_INIT_DATA[][3] = {")

    for i, (x_fp, y_fp, angle_fp) in enumerate(agents):
        # Convert to signed 32-bit for C++
        x_signed = x_fp if x_fp < (1 << 24) else x_fp - (1 << 25)
        y_signed = y_fp if y_fp < (1 << 24) else y_fp - (1 << 25)
        angle_signed = angle_fp if angle_fp < (1 << 24) else angle_fp - (1 << 25)

        # Format as hex for clarity
        line = f"    {{0x{x_signed & 0xFFFFFFFF:08X}, 0x{y_signed & 0xFFFFFFFF:08X}, 0x{angle_signed & 0xFFFFFFFF:08X}}}"

        if i < len(agents) - 1:
            line += ","

        # Add comment with pixel values for first 10 agents
        if i < 10:
            x_px = fp.from_fixed(x_fp)
            y_px = fp.from_fixed(y_fp)
            angle_rad = fp.from_fixed(angle_fp)
            angle_deg = angle_rad * 180.0 / math.pi
            line += f"  // Agent {i}: ({x_px:.2f}, {y_px:.2f}) px, {angle_deg:.1f}°"
        elif i == 10:
            line += "  // ... (remaining agents)"

        lines.append(line)

    lines.append("};")
    lines.append("")
    lines.append(f"const int NUM_INIT_AGENTS = {len(agents)};")

    return "\n".join(lines)


def format_cpp_memcpy_initialization(agents, fp):
    """
    Format initialization code using memcpy approach.

    Returns:
        String containing C++ initialization code using memcpy
    """
    lines = []
    lines.append("// Function to initialize agents from pre-computed data")
    lines.append("// Usage: initialize_agents_from_precomputed(dut, num_agents);")
    lines.append("template<typename DUT_TYPE>")
    lines.append("void initialize_agents_from_precomputed(DUT_TYPE* dut, int num_agents) {")
    lines.append("    for (int i = 0; i < NUM_INIT_AGENTS && i < num_agents; i++) {")
    lines.append("        // Write x coordinate")
    lines.append("        dut->debug_agent_idx = i;")
    lines.append("        dut->debug_agent_sel = 0;  // 0 = x")
    lines.append("        dut->debug_agent_data_write = AGENT_INIT_DATA[i][0];")
    lines.append("        dut->debug_agent_write_en = 1;")
    lines.append("        dut->eval();")
    lines.append("        dut->debug_agent_write_en = 0;")
    lines.append("")
    lines.append("        // Write y coordinate")
    lines.append("        dut->debug_agent_sel = 1;  // 1 = y")
    lines.append("        dut->debug_agent_data_write = AGENT_INIT_DATA[i][1];")
    lines.append("        dut->debug_agent_write_en = 1;")
    lines.append("        dut->eval();")
    lines.append("        dut->debug_agent_write_en = 0;")
    lines.append("")
    lines.append("        // Write angle")
    lines.append("        dut->debug_agent_sel = 2;  // 2 = angle")
    lines.append("        dut->debug_agent_data_write = AGENT_INIT_DATA[i][2];")
    lines.append("        dut->debug_agent_write_en = 1;")
    lines.append("        dut->eval();")
    lines.append("        dut->debug_agent_write_en = 0;")
    lines.append("    }")
    lines.append("    std::cout << \"Initialized \" << NUM_INIT_AGENTS << \" agents from pre-computed data\" << std::endl;")
    lines.append("}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Generate C++ initialization code from Python reference circle spawn'
    )
    parser.add_argument('--num-agents', type=int, default=100,
                        help='Number of agents to generate (default: 100)')
    parser.add_argument('--width', type=int, default=320,
                        help='Simulation width in pixels (default: 320)')
    parser.add_argument('--height', type=int, default=240,
                        help='Simulation height in pixels (default: 240)')
    parser.add_argument('--output', type=str, default='agent_init_data.h',
                        help='Output C++ header file (default: agent_init_data.h)')
    parser.add_argument('--verify-first', type=int, default=5,
                        help='Number of first agents to print for verification (default: 5)')

    args = parser.parse_args()

    print("=" * 80)
    print("C++ Agent Initialization Code Generator")
    print("=" * 80)
    print(f"Configuration:")
    print(f"  Agents: {args.num_agents}")
    print(f"  Resolution: {args.width}x{args.height}")
    print(f"  Output: {args.output}")
    print()

    # Generate agents using Python reference
    agents, fp = generate_circle_spawn_agents(args.num_agents, args.width, args.height)

    # Print first N agents for verification
    print(f"First {args.verify_first} agents (for verification):")
    print("-" * 80)
    print(f"{'Agent':<8} {'X (px)':<12} {'Y (px)':<12} {'Angle (rad)':<14} {'Angle (deg)':<12} {'X (hex)':<12} {'Y (hex)':<12} {'Angle (hex)':<12}")
    print("-" * 80)

    for i in range(min(args.verify_first, len(agents))):
        x_fp, y_fp, angle_fp = agents[i]
        x_px = fp.from_fixed(x_fp)
        y_px = fp.from_fixed(y_fp)
        angle_rad = fp.from_fixed(angle_fp)
        angle_deg = angle_rad * 180.0 / math.pi

        # Sign-extend for display
        x_signed = x_fp if x_fp < (1 << 24) else x_fp - (1 << 25)
        y_signed = y_fp if y_fp < (1 << 24) else y_fp - (1 << 25)
        angle_signed = angle_fp if angle_fp < (1 << 24) else angle_fp - (1 << 25)

        print(f"{i:<8} {x_px:<12.2f} {y_px:<12.2f} {angle_rad:<14.6f} {angle_deg:<12.2f} "
              f"0x{x_signed & 0xFFFFFFFF:08X} 0x{y_signed & 0xFFFFFFFF:08X} 0x{angle_signed & 0xFFFFFFFF:08X}")

    print("-" * 80)
    print()

    # Generate C++ code
    cpp_array = format_cpp_array(agents, fp)
    cpp_init = format_cpp_memcpy_initialization(agents, fp)

    # Write to file
    output_path = Path(args.output)
    with open(output_path, 'w') as f:
        f.write("// Auto-generated agent initialization data\n")
        f.write("// Generated by generate_cpp_agent_init.py\n")
        f.write("//\n")
        f.write(f"// Configuration:\n")
        f.write(f"//   Agents: {args.num_agents}\n")
        f.write(f"//   Resolution: {args.width}x{args.height}\n")
        f.write(f"//   Spawn pattern: circle (40% radius, pointing inward)\n")
        f.write("//\n")
        f.write("// Fixed-point format: Q12.12 (12 integer bits, 12 fractional bits)\n")
        f.write("//   Scale: 4096 (1.0 = 0x1000)\n")
        f.write("//   Range: -2048.0 to +2047.9998\n")
        f.write("//\n\n")
        f.write("#ifndef AGENT_INIT_DATA_H\n")
        f.write("#define AGENT_INIT_DATA_H\n\n")
        f.write("#include <cstdint>\n\n")
        f.write(cpp_array)
        f.write("\n\n")
        f.write(cpp_init)
        f.write("\n\n#endif // AGENT_INIT_DATA_H\n")

    print(f"✓ Generated C++ header file: {output_path}")
    print()

    # Show usage example
    print("Usage in C++ testbench:")
    print("-" * 80)
    print('#include "agent_init_data.h"')
    print()
    print("// In your testbench initialization:")
    print("initialize_agents_from_precomputed(dut, NUM_AGENTS);")
    print("-" * 80)
    print()

    print("✓ Generation complete!")
    print("=" * 80)


if __name__ == '__main__':
    main()
