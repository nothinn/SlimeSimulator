#!/usr/bin/env python3
"""
Generate Python Reference Trail Maps

This script runs the SlimeSimulatorReference model and generates trail map
snapshots at specified iteration points. These serve as golden reference data
for RTL comparison.

Usage:
    python generate_python_ref.py --width 160 --height 120 --agents 1000 \\
           --iterations 1,5,10,20 --output-dir regression_test_results/reference
"""

import sys
import argparse
import numpy as np
from pathlib import Path

# Import from slime_simulator
sys.path.insert(0, str(Path(__file__).parent.parent))
from slime_simulator import SlimeSimulatorReference


def generate_reference_trails(
    width: int = 160,
    height: int = 120,
    num_agents: int = 1000,
    iterations: list = [1, 5, 10, 20],
    output_dir: str = "regression_test_results/reference",
    seed: int = 0xDEADBEEF,
    verbose: bool = True
):
    """
    Generate reference trail maps at specified iteration points.

    Args:
        width: Simulation width in pixels
        height: Simulation height in pixels
        num_agents: Number of agents
        iterations: List of iteration numbers to capture (e.g., [1, 5, 10, 20])
        output_dir: Directory to save trail map files
        seed: LFSR seed for deterministic results
        verbose: Print progress messages

    Returns:
        dict: Mapping from iteration number to trail map array
    """
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Initialize simulator
    if verbose:
        print(f"Initializing SlimeSimulatorReference:")
        print(f"  Resolution: {width}x{height}")
        print(f"  Agents: {num_agents}")
        print(f"  Seed: 0x{seed:08X}")

    sim = SlimeSimulatorReference(
        width=width,
        height=height,
        num_agents=num_agents,
        int_bits=12,
        frac_bits=12,
        lfsr_seed=seed
    )

    # Initialize agents at center (matching RTL behavior)
    sim.init_agents_center()

    # Sort iterations to capture in order
    iterations_sorted = sorted(iterations)
    max_iter = max(iterations_sorted)

    # Storage for trail maps
    trail_maps = {}

    if verbose:
        print(f"\nRunning simulation for {max_iter} iterations...")
        print(f"Capturing at iterations: {iterations_sorted}")

    # Run simulation and capture at specified points
    for i in range(1, max_iter + 1):
        sim.step()

        if i in iterations_sorted:
            # Capture trail map
            trail_map = sim.get_trail_map()
            trail_maps[i] = trail_map

            # Save to file
            filename = output_path / f"trail_iter_{i:03d}.bin"
            trail_map.tofile(str(filename))

            # Calculate statistics
            nonzero = np.count_nonzero(trail_map)
            mean_val = np.mean(trail_map[trail_map > 0]) if nonzero > 0 else 0
            max_val = np.max(trail_map)

            if verbose:
                print(f"  Iter {i:3d}: {nonzero:6d} pixels written "
                      f"(mean={mean_val:.1f}, max={max_val})")
                print(f"           -> {filename}")

    if verbose:
        print(f"\nGenerated {len(trail_maps)} reference trail maps")
        print(f"Output directory: {output_path.absolute()}")

        # Also dump final state for debugging
        state_file = output_path / "final_state.txt"
        sim.dump_state(str(state_file))
        print(f"Final state: {state_file}")

    return trail_maps


def main():
    parser = argparse.ArgumentParser(
        description='Generate Python reference trail maps for RTL comparison',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate reference for standard test points
  python generate_python_ref.py

  # Custom iterations and resolution
  python generate_python_ref.py --width 320 --height 240 --iterations 1,2,5,10,15,20

  # Different seed
  python generate_python_ref.py --seed 0x12345678
        """
    )

    parser.add_argument('--width', type=int, default=160,
                        help='Simulation width (default: 160)')
    parser.add_argument('--height', type=int, default=120,
                        help='Simulation height (default: 120)')
    parser.add_argument('--agents', type=int, default=1000,
                        help='Number of agents (default: 1000)')
    parser.add_argument('--iterations', type=str, default='1,5,10,20',
                        help='Comma-separated list of iterations to capture (default: 1,5,10,20)')
    parser.add_argument('--output-dir', type=str,
                        default='regression_test_results/reference',
                        help='Output directory (default: regression_test_results/reference)')
    parser.add_argument('--seed', type=lambda x: int(x, 0), default=0xDEADBEEF,
                        help='LFSR seed in hex (default: 0xDEADBEEF)')
    parser.add_argument('--quiet', action='store_true',
                        help='Suppress progress messages')

    args = parser.parse_args()

    # Parse iterations
    try:
        iterations = [int(x.strip()) for x in args.iterations.split(',')]
    except ValueError:
        print(f"Error: Invalid iterations format: {args.iterations}")
        print("Expected comma-separated integers, e.g., '1,5,10,20'")
        sys.exit(1)

    if not iterations:
        print("Error: No iterations specified")
        sys.exit(1)

    if any(i < 1 for i in iterations):
        print("Error: Iterations must be >= 1")
        sys.exit(1)

    # Generate reference trails
    try:
        generate_reference_trails(
            width=args.width,
            height=args.height,
            num_agents=args.agents,
            iterations=iterations,
            output_dir=args.output_dir,
            seed=args.seed,
            verbose=not args.quiet
        )
    except Exception as e:
        print(f"\nError generating reference trails: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
