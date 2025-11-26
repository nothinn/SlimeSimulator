#!/usr/bin/env python3
"""
Generate Python reference simulations at RTL-compatible scales
and create side-by-side comparison visualizations.

This creates frames showing what the Python simulator produces,
which can then be compared with RTL simulation outputs when available.
"""

import sys
import os
import time
from pathlib import Path
from datetime import datetime
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))

from slime_simulator import SlimeSimulator, SimulationConfig


class ComparisonFrameGenerator:
    """Generate side-by-side Python vs RTL-scale comparison frames."""

    def __init__(self, output_dir="comparison_frames"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.frame_count = 0

    def create_comparison_frame(self, python_frame, label_text, step_num):
        """
        Create a comparison frame with Python output and metadata.

        Args:
            python_frame: 3-channel PIL Image of Python simulation
            label_text: Text to display (resolution, agents, etc)
            step_num: Step number for filename
        """
        # Create canvas with space for labels
        canvas_width = python_frame.width + 20
        canvas_height = python_frame.height + 120

        canvas = Image.new('RGB', (canvas_width, canvas_height), color='black')

        # Paste Python frame
        canvas.paste(python_frame, (10, 60))

        # Add title and metadata
        draw = ImageDraw.Draw(canvas)

        # Try to use a decent font, fall back to default if not available
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
            label_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
        except:
            title_font = ImageFont.load_default()
            label_font = ImageFont.load_default()

        # Draw title
        draw.text((10, 10), "Python Reference Simulation", fill='lime', font=title_font)

        # Draw labels
        label_lines = label_text.split('\n')
        y_pos = canvas_height - 40
        for line in label_lines:
            draw.text((10, y_pos), line, fill='cyan', font=label_font)
            y_pos -= 15

        # Save frame
        filename = self.output_dir / f"python_comparison_{step_num:05d}.png"
        canvas.save(filename)
        return filename

    def trail_to_image(self, trail_map):
        """Convert trail map to 3-channel PIL Image with heat coloring."""
        # Normalize to 0-255
        if trail_map.max() > 0:
            normalized = (trail_map / trail_map.max() * 255).astype(np.uint8)
        else:
            normalized = trail_map.astype(np.uint8)

        # Create 3-channel RGB image with heat coloring
        img_array = np.zeros((trail_map.shape[0], trail_map.shape[1], 3), dtype=np.uint8)

        # Heat map: black -> blue -> cyan -> green -> yellow -> red
        for i in range(256):
            mask = normalized == i
            if i < 64:  # Black to blue
                img_array[mask] = [0, 0, min(255, int(i * 4))]
            elif i < 128:  # Blue to cyan
                img_array[mask] = [0, min(255, int((i - 64) * 4)), 255]
            elif i < 192:  # Cyan to green
                img_array[mask] = [0, 255, min(255, int(255 - (i - 128) * 4))]
            else:  # Green to red
                img_array[mask] = [min(255, int((i - 192) * 6.4)), min(255, int(255 - (i - 192) * 4)), 0]

        return Image.fromarray(img_array, 'RGB')


def generate_rtl_scale_comparison():
    """Generate Python simulation at RTL-compatible scale (320x240, fewer agents)."""

    print("\n" + "="*70)
    print("  PYTHON REFERENCE: RTL-COMPATIBLE SCALE (320x240, 5000 agents)")
    print("="*70)

    comparison_gen = ComparisonFrameGenerator("comparison_frames_rtl_scale")

    # RTL-compatible configuration
    config = SimulationConfig(
        width=320,
        height=240,
        num_agents=5000,  # RTL-feasible count
        num_steps=100,    # Fewer steps for quick generation
        move_speed=1.0,
        turn_speed=0.3,
        sensor_angle=0.5,
        sensor_distance=9.0,
        deposit_amount=5,
        decay_rate=0.95,
        lfsr_width=32,
        seed=0xDEADBEEF
    )

    sim = SlimeSimulator(config)

    print(f"Configuration:")
    print(f"  Resolution: {config.width}x{config.height}")
    print(f"  Agents: {config.num_agents:,}")
    print(f"  Steps: {config.num_steps:,}")
    print(f"  Seed: 0x{config.seed:08X}")

    start_time = time.time()

    # Generate frames at regular intervals
    for step in range(config.num_steps):
        sim.step()

        # Save comparison frame every 10 steps
        if step % 10 == 0 or step == config.num_steps - 1:
            trail_img = comparison_gen.trail_to_image(sim.trail_map)
            label = f"Python Ref | {config.width}x{config.height} | {config.num_agents:,} agents\nStep {step+1}/{config.num_steps} ({100*(step+1)//config.num_steps}%)"
            filename = comparison_gen.create_comparison_frame(trail_img, label, step)
            print(f"  Step {step+1:3d}/{config.num_steps}: {filename.name}")

    elapsed = time.time() - start_time
    print(f"\nRTL-scale simulation complete!")
    print(f"  Runtime: {elapsed:.2f}s")
    print(f"  Frames saved to: comparison_frames_rtl_scale/")

    return sim


def generate_full_scale_comparison():
    """Generate Python simulation at full scale (800x600, 100k agents) for reference."""

    print("\n" + "="*70)
    print("  PYTHON REFERENCE: FULL SCALE (800x600, 100k agents)")
    print("="*70)

    comparison_gen = ComparisonFrameGenerator("comparison_frames_full_scale")

    # Full-scale configuration (as validated earlier)
    config = SimulationConfig(
        width=800,
        height=600,
        num_agents=100000,
        num_steps=50,  # Reduced for quicker generation
        move_speed=1.0,
        turn_speed=0.3,
        sensor_angle=0.5,
        sensor_distance=9.0,
        deposit_amount=5,
        decay_rate=0.95,
        lfsr_width=32,
        seed=0xDEADBEEF
    )

    sim = SlimeSimulator(config)

    print(f"Configuration:")
    print(f"  Resolution: {config.width}x{config.height}")
    print(f"  Agents: {config.num_agents:,}")
    print(f"  Steps: {config.num_steps:,}")
    print(f"  Seed: 0x{config.seed:08X}")

    start_time = time.time()

    # Generate frames at regular intervals
    for step in range(config.num_steps):
        sim.step()

        # Save comparison frame every 5 steps
        if step % 5 == 0 or step == config.num_steps - 1:
            trail_img = comparison_gen.trail_to_image(sim.trail_map)
            label = f"Python Ref | {config.width}x{config.height} | {config.num_agents:,} agents\nStep {step+1}/{config.num_steps} ({100*(step+1)//config.num_steps}%)"
            filename = comparison_gen.create_comparison_frame(trail_img, label, step)
            print(f"  Step {step+1:3d}/{config.num_steps}: {filename.name}")

    elapsed = time.time() - start_time
    print(f"\nFull-scale simulation complete!")
    print(f"  Runtime: {elapsed:.2f}s")
    print(f"  Frames saved to: comparison_frames_full_scale/")

    return sim


def main():
    """Generate all comparison frames."""

    print("\n" + "="*70)
    print("  PYTHON REFERENCE vs RTL SCALE COMPARISON")
    print("="*70)
    print("\nThis script generates Python reference simulations at:")
    print("1. RTL-compatible scale (320x240, 5000 agents)")
    print("2. Full scale (800x600, 100k agents)")
    print("\nThese reference outputs can be compared with RTL simulations")
    print("when they are run through Vivado or Verilator.")

    # Generate RTL-scale comparison
    rtl_scale_sim = generate_rtl_scale_comparison()

    # Generate full-scale comparison
    full_scale_sim = generate_full_scale_comparison()

    # Summary
    print("\n" + "="*70)
    print("  COMPARISON GENERATION COMPLETE")
    print("="*70)
    print("\nGenerated Frames:")
    print("  ✓ comparison_frames_rtl_scale/ - 320x240, 5000 agents")
    print("  ✓ comparison_frames_full_scale/ - 800x600, 100k agents")
    print("\nNext Steps:")
    print("1. Run RTL simulations (cocotb or Vivado)")
    print("2. Extract trail maps from RTL simulations")
    print("3. Compare against these Python reference frames")
    print("4. Analyze differences in agent behavior and trail patterns")
    print("\nKey Files:")
    print(f"  - RTL-scale trail map: {Path('validation_output')/Path('reference_trail_320x240_5000agents.npy')}")
    print(f"  - Full-scale trail map: {Path('validation_output')/Path('reference_trail_800x600_100000agents.npy')}")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
