#!/usr/bin/env python3
"""Analyze trail map files for debugging."""

import numpy as np
import sys
from pathlib import Path

def load_trail_map(filename, width=160, height=120):
    """Load trail map from binary file."""
    try:
        data = np.fromfile(filename, dtype=np.uint8)
        if len(data) != width * height:
            print(f"Warning: Expected {width*height} bytes, got {len(data)}")
            # Pad or truncate
            if len(data) < width * height:
                data = np.pad(data, (0, width*height - len(data)))
            else:
                data = data[:width*height]
        return data.reshape((height, width))
    except FileNotFoundError:
        print(f"Error: File {filename} not found")
        return None

def analyze_trail_map(trail_map, filename=""):
    """Print statistics about a trail map."""
    if trail_map is None:
        return
    
    total_pixels = trail_map.size
    non_zero = np.count_nonzero(trail_map)
    trail_sum = np.sum(trail_map.astype(np.int32))
    trail_mean = np.mean(trail_map.astype(np.float32))
    trail_max = np.max(trail_map)
    trail_min = np.min(trail_map)
    
    print(f"\n{'='*60}")
    print(f"Trail Map Analysis: {Path(filename).name}")
    print(f"{'='*60}")
    print(f"  Resolution: {trail_map.shape[1]}x{trail_map.shape[0]}")
    print(f"  Total pixels: {total_pixels}")
    print(f"  Non-zero pixels: {non_zero} ({100*non_zero/total_pixels:.1f}%)")
    print(f"  Trail sum: {trail_sum}")
    print(f"  Trail mean: {trail_mean:.2f}")
    print(f"  Trail min: {trail_min}")
    print(f"  Trail max: {trail_max}")
    
    # Histogram
    hist, _ = np.histogram(trail_map, bins=16, range=(0, 256))
    print(f"\n  Intensity distribution (16 bins):")
    for i, count in enumerate(hist):
        level = i * 16
        percent = 100 * count / total_pixels
        bar = '█' * int(percent / 2)
        print(f"    [{level:3d}-{level+15:3d}]: {count:6d} ({percent:5.1f}%) {bar}")

def compare_trail_maps(trail1, trail2, label1="Trail1", label2="Trail2"):
    """Compare two trail maps."""
    if trail1 is None or trail2 is None:
        return
    
    if trail1.shape != trail2.shape:
        print(f"Error: Trail maps have different shapes: {trail1.shape} vs {trail2.shape}")
        return
    
    diff = np.abs(trail1.astype(np.int16) - trail2.astype(np.int16))
    max_diff = np.max(diff)
    mean_diff = np.mean(diff)
    match = np.sum(trail1 == trail2) / trail1.size * 100
    
    print(f"\n{'='*60}")
    print(f"Trail Map Comparison: {label1} vs {label2}")
    print(f"{'='*60}")
    print(f"  Matching pixels: {match:.2f}%")
    print(f"  Max difference: {max_diff}")
    print(f"  Mean difference: {mean_diff:.2f}")
    print(f"  RMS difference: {np.sqrt(np.mean(diff**2)):.2f}")
    
    # Difference distribution
    hist, _ = np.histogram(diff, bins=16, range=(0, 256))
    print(f"\n  Difference distribution:")
    for i, count in enumerate(hist):
        level = i * 16
        percent = 100 * count / diff.size
        bar = '█' * int(percent / 2)
        print(f"    [{level:3d}-{level+15:3d}]: {count:6d} ({percent:5.1f}%) {bar}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: analyze_trails.py <trail_file> [trail_file2]")
        print("\nExample: analyze_trails.py reference_trail_160x120_1step.bin")
        print("         analyze_trails.py reference_trail_160x120_1step.bin rtl_trail.bin")
        sys.exit(1)
    
    file1 = sys.argv[1]
    trail1 = load_trail_map(file1)
    analyze_trail_map(trail1, file1)
    
    if len(sys.argv) > 2:
        file2 = sys.argv[2]
        trail2 = load_trail_map(file2)
        compare_trail_maps(trail1, trail2, Path(file1).stem, Path(file2).stem)
