#!/usr/bin/env python3
"""Analyze RTL trail dump files to check if they contain non-zero values."""

import numpy as np
import struct
import os

def analyze_trail_dump(filename, width=320, height=240):
    """Read and analyze a trail dump file."""
    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        return None

    # Read the binary file as 32-bit unsigned integers (18-bit values)
    with open(filename, 'rb') as f:
        data = f.read()

    # Unpack as 32-bit unsigned integers
    num_pixels = len(data) // 4
    values = struct.unpack(f'<{num_pixels}I', data)

    # Convert to numpy array
    trail = np.array(values, dtype=np.uint32)

    # Calculate statistics
    stats = {
        'filename': os.path.basename(filename),
        'min': int(trail.min()),
        'max': int(trail.max()),
        'mean': float(trail.mean()),
        'non_zero_count': int(np.count_nonzero(trail)),
        'total_pixels': len(trail)
    }

    return stats

def main():
    print("="*70)
    print("RTL Trail Dump Analysis")
    print("="*70)
    print()

    dump_dir = "/home/reson/SlimeSimulator/rtl/sim/rtl_trail_dumps"

    # Analyze each step
    for step in [0, 1, 2]:
        filename = os.path.join(dump_dir, f"trail_step_{step:05d}.bin")
        stats = analyze_trail_dump(filename)

        if stats:
            print(f"Step {step}:")
            print(f"  File: {stats['filename']}")
            print(f"  Min:  {stats['min']}")
            print(f"  Max:  {stats['max']}")
            print(f"  Mean: {stats['mean']:.2f}")
            print(f"  Non-zero pixels: {stats['non_zero_count']} / {stats['total_pixels']}")

            # SUCCESS METRIC: Check if max > 0
            if stats['max'] > 0:
                print(f"  ✓ SUCCESS: Trail contains non-zero values!")
            else:
                print(f"  ✗ FAIL: Trail is all zeros")
            print()

if __name__ == '__main__':
    main()
