#!/usr/bin/env python3
"""
RTL vs Python Reference Comparison
Compare 100k agent slime simulator RTL with Python reference implementation.
"""

import sys
import os
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json

sys.path.insert(0, str(Path(__file__).parent))
from slime_simulator import SlimeSimulator, SimulationConfig


class RTLPythonComparison:
    """Generate side-by-side comparison of RTL and Python trail maps."""

    def __init__(self, output_dir="rtl_final_comparison_100k", width=800, height=600, num_agents=100000, num_steps=10000):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        # RTL dumps are in rtl/sim/rtl_trail_dumps
        self.rtl_dumps_dir = Path(__file__).parent / "rtl" / "sim" / "rtl_trail_dumps"
        self.width = width
        self.height = height
        self.num_agents = num_agents
        self.num_steps = num_steps

    def trail_to_image(self, trail_map):
        """Convert trail map to heat-mapped RGB image."""
        if trail_map.max() > 0:
            normalized = (trail_map / trail_map.max() * 255).astype(np.uint8)
        else:
            normalized = trail_map.astype(np.uint8)

        img_array = np.zeros((trail_map.shape[0], trail_map.shape[1], 3), dtype=np.uint8)

        # Heat map: black -> blue -> cyan -> green -> yellow -> red
        for i in range(256):
            mask = normalized == i
            if i < 64:
                # Black to blue
                img_array[mask] = [0, 0, min(255, int(i * 4))]
            elif i < 128:
                # Blue to cyan
                img_array[mask] = [0, min(255, int((i - 64) * 4)), 255]
            elif i < 192:
                # Cyan to green
                img_array[mask] = [0, 255, min(255, int(255 - (i - 128) * 4))]
            else:
                # Green to red
                img_array[mask] = [min(255, int((i - 192) * 6.4)), min(255, int(255 - (i - 192) * 4)), 0]

        return Image.fromarray(img_array, 'RGB')

    def load_rtl_trail(self, step):
        """Load RTL trail map from binary dump (18-bit values stored as 3 bytes)."""
        filename = self.rtl_dumps_dir / f"trail_step_{step:05d}.bin"
        if not filename.exists():
            return None

        with open(filename, 'rb') as f:
            raw_data = f.read()

        data = np.frombuffer(raw_data, dtype=np.uint8)
        # 18-bit values: each cell is 3 bytes (24-bit storage, 18 bits used)
        expected_bytes = self.width * self.height * 3
        if len(data) == expected_bytes:
            # Unpack 3-byte values to 18-bit integers
            trail_map = np.zeros((self.height, self.width), dtype=np.uint32)
            idx = 0
            for y in range(self.height):
                for x in range(self.width):
                    # Read 3 bytes and reconstruct 18-bit value
                    b0 = int(data[idx])
                    b1 = int(data[idx + 1])
                    b2 = int(data[idx + 2])
                    val = b0 | (b1 << 8) | ((b2 & 0x03) << 16)
                    trail_map[y, x] = val
                    idx += 3
            return trail_map
        return None

    def create_comparison_frame(self, python_trail, rtl_trail, step):
        """Create side-by-side comparison frame."""
        python_img = self.trail_to_image(python_trail)
        rtl_img = self.trail_to_image(rtl_trail)

        # Create canvas
        canvas_width = python_img.width + rtl_img.width + 40
        canvas_height = python_img.height + 120

        canvas = Image.new('RGB', (canvas_width, canvas_height), color='black')

        # Paste images
        canvas.paste(python_img, (10, 60))
        canvas.paste(rtl_img, (python_img.width + 20, 60))

        # Draw labels
        draw = ImageDraw.Draw(canvas)

        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
            label_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
        except:
            title_font = ImageFont.load_default()
            label_font = ImageFont.load_default()

        # Title
        draw.text((10, 10), f"RTL Simulation vs Python Reference ({self.width}x{self.height}, {self.num_agents} agents, {self.num_steps} steps)",
                 fill='lime', font=title_font)

        # Column headers
        draw.text((30, 40), "PYTHON REFERENCE", fill='cyan', font=label_font)
        draw.text((python_img.width + 40, 40), "RTL SIMULATION (Verilator)", fill='magenta', font=label_font)

        # Statistics
        py_min, py_max, py_mean = python_trail.min(), python_trail.max(), python_trail.mean()
        rtl_min, rtl_max, rtl_mean = rtl_trail.min(), rtl_trail.max(), rtl_trail.mean()

        stats_text = f"Step {step}/10000 | Python: min={py_min} max={py_max} mean={py_mean:.0f} | RTL: min={rtl_min} max={rtl_max} mean={rtl_mean:.0f}"
        draw.text((10, canvas_height - 30), stats_text, fill='yellow', font=label_font)

        # Compute pixel-level difference
        if rtl_trail.shape == python_trail.shape:
            diff = np.abs(rtl_trail.astype(int) - python_trail.astype(int))
            max_diff = diff.max()
            mean_diff = diff.mean()
            match_pct = 100 * (1 - mean_diff / max(py_max, 1))
            diff_text = f"Diff: max={max_diff} mean={mean_diff:.1f} match={match_pct:.1f}%"
            draw.text((10, canvas_height - 50), diff_text, fill='orange', font=label_font)

        # Save
        filename = self.output_dir / f"comparison_{step:05d}.png"
        canvas.save(filename)
        return filename, py_min, py_max, py_mean, rtl_min, rtl_max, rtl_mean, max_diff if rtl_trail.shape == python_trail.shape else 0

    def run_comparison(self):
        """Run Python reference and compare with RTL."""
        print("\n" + "="*80)
        print(f"  RTL vs PYTHON COMPARISON: {self.num_agents} agents @ {self.width}x{self.height}, {self.num_steps} steps")
        print("="*80)
        print()

        # Create Python reference configuration
        config = SimulationConfig(
            width=self.width,
            height=self.height,
            num_agents=self.num_agents,
            num_steps=self.num_steps,
            move_speed=1.0,
            turn_speed=0.3,
            sensor_angle=0.5,
            sensor_distance=9.0,
            deposit_amount=5,
            decay_rate=0.95,
            lfsr_width=32,
            seed=0xDEADBEEF
        )

        print(f"Configuration:")
        print(f"  Resolution: {self.width}×{self.height}")
        print(f"  Agents: {self.num_agents:,}")
        print(f"  Steps: {self.num_steps:,}")
        print(f"  Seed: 0xDEADBEEF")
        print()

        # Run Python simulation
        print("Running Python reference simulation...")
        sim = SlimeSimulator(config)

        comparison_stats = []
        current_sim_step = 0

        # Steps to compare (match RTL dump intervals which start at 0)
        comparison_steps = range(0, config.num_steps, max(1, config.num_steps // 100))  # Generate ~100 frames
        

        for step in comparison_steps:
            # Get Python trail at this step
            target_step = step

            # Run to the target step
            while current_sim_step < target_step:
                sim.step()
                current_sim_step += 1

            python_trail = sim.trail_map.copy()

            # Load RTL trail
            rtl_trail = self.load_rtl_trail(step)

            if rtl_trail is None:
                print(f"[SKIP] Step {step}: RTL trail not found")
                continue

            print(f"[{step:5d}/{self.num_steps}] Generating comparison frame...", end=" ")

            # Create comparison frame
            filename, py_min, py_max, py_mean, rtl_min, rtl_max, rtl_mean, max_diff = \
                self.create_comparison_frame(python_trail, rtl_trail, step)

            stats = {
                "step": step,
                "python": {"min": int(py_min), "max": int(py_max), "mean": float(py_mean)},
                "rtl": {"min": int(rtl_min), "max": int(rtl_max), "mean": float(rtl_mean)},
                "max_diff": int(max_diff),
                "filename": str(filename.name)
            }
            comparison_stats.append(stats)

            print(f"✓ {filename.name}")

        # Save statistics
        stats_file = self.output_dir / "comparison_stats.json"
        with open(stats_file, 'w') as f:
            json.dump(comparison_stats, f, indent=2)

        print()
        print("="*80)
        print("  COMPARISON COMPLETE")
        print("="*80)
        print()
        print("Output files:")
        print(f"  📁 Directory: {self.output_dir}")
        print(f"  🖼️  Frames: {len(comparison_stats)} comparison images")
        print(f"  📊 Statistics: {stats_file}")
        print()

        # Summary statistics
        print("Summary Statistics:")
        print("-" * 80)
        for stat in comparison_stats:
            step = stat["step"]
            py = stat["python"]
            rtl = stat["rtl"]
            diff = stat["max_diff"]
            print(f"Step {step:4d}: Python(min={py['min']:7d}, max={py['max']:7d}, mean={py['mean']:8.1f}) | " +
                  f"RTL(min={rtl['min']:7d}, max={rtl['max']:7d}, mean={rtl['mean']:8.1f}) | " +
                  f"MaxDiff={diff:5d}")


def main():
    """Run RTL vs Python comparison."""
    import sys

    # Parse command-line arguments
    output_dir = "rtl_final_comparison_100k"
    width = 800
    height = 600
    num_agents = 100000
    num_steps = 10000

    for i, arg in enumerate(sys.argv[1:]):
        if arg == "--output" and i + 1 < len(sys.argv) - 1:
            output_dir = sys.argv[i + 2]
        elif arg == "--width" and i + 1 < len(sys.argv) - 1:
            width = int(sys.argv[i + 2])
        elif arg == "--height" and i + 1 < len(sys.argv) - 1:
            height = int(sys.argv[i + 2])
        elif arg == "--agents" and i + 1 < len(sys.argv) - 1:
            num_agents = int(sys.argv[i + 2])
        elif arg == "--steps" and i + 1 < len(sys.argv) - 1:
            num_steps = int(sys.argv[i + 2])

    comp = RTLPythonComparison(output_dir, width, height, num_agents, num_steps)
    comp.run_comparison()


if __name__ == "__main__":
    main()
