#!/usr/bin/env python3
"""
Emergency build and test script when bash is broken.
Builds Verilator testbench and runs comparison test.
"""

import subprocess
import os
import sys

def run_command(cmd, cwd=None):
    """Run a command and return success status."""
    print(f"\n{'='*70}")
    print(f"Running: {cmd}")
    print(f"{'='*70}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=600
        )
        print(result.stdout)
        print(f"Exit code: {result.returncode}")
        return result.returncode == 0
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    project_root = "/home/reson/SlimeSimulator"
    sim_dir = f"{project_root}/rtl/sim"

    # Configuration
    width = 320
    height = 240
    agents = 100
    steps = 3

    print(f"\n{'#'*70}")
    print(f"# RTL vs Python Comparison Test")
    print(f"# Resolution: {width}x{height}, Agents: {agents}, Steps: {steps}")
    print(f"# WITH --public-flat-rw FIX")
    print(f"{'#'*70}\n")

    # Step 1: Build with Verilator
    print("\n[1/4] Building Verilator testbench...")
    build_cmd = f"""
verilator -cc --trace -Wno-fatal --public-flat-rw --exe \\
    -CFLAGS "-std=c++17 -DWIDTH={width} -DHEIGHT={height} -DNUM_AGENTS={agents} -DNUM_STEPS={steps}" \\
    -LDFLAGS "-lm" \\
    --top-module slime_top \\
    --Mdir obj_dir \\
    -I../src \\
    ../src/slime_top.sv \\
    ../src/agent_orchestrator.sv \\
    ../src/agent_processor.sv \\
    ../src/lfsr.sv \\
    ../src/fixed_point_mult.sv \\
    ../src/trig_lut.sv \\
    ../src/debouncer.sv \\
    ../src/vga_controller.sv \\
    slime_verilator_full_tb.cpp
"""

    if not run_command(build_cmd, cwd=sim_dir):
        print("\nERROR: Verilator compilation failed")
        return 1

    # Step 2: Make the C++ simulation
    print("\n[2/4] Compiling C++ simulation...")
    make_cmd = "make -C obj_dir -f Vslime_top.mk"
    if not run_command(make_cmd, cwd=sim_dir):
        print("\nERROR: Make failed")
        return 1

    # Step 3: Run RTL simulation
    print("\n[3/4] Running RTL simulation...")
    rtl_cmd = "./obj_dir/Vslime_top"
    if not run_command(rtl_cmd, cwd=sim_dir):
        print("\nERROR: RTL simulation failed")
        return 1

    # Step 4: Run Python comparison
    print("\n[4/4] Running Python comparison and generating images...")
    python_cmd = f"""
python3 rtl_final_comparison.py \\
    --resolution {width} {height} \\
    --agents {agents} \\
    --steps {steps}
"""
    if not run_command(python_cmd, cwd=project_root):
        print("\nERROR: Python comparison failed")
        return 1

    # Success - show results
    print(f"\n{'='*70}")
    print("SUCCESS! Test completed.")
    print(f"{'='*70}")
    print(f"\nResults directory: rtl_comparison_{width}x{height}_{agents}agents_{steps}steps/")
    print("Check comparison_stats.json for RTL trail values")

    return 0

if __name__ == "__main__":
    sys.exit(main())
