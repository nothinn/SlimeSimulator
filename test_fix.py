#!/usr/bin/env python3
import subprocess
import sys
import os

print("=" * 73)
print("  TESTING AGENT_COORDINATOR FIX")
print("=" * 73)
print()

os.chdir("/home/reson/SlimeSimulator/rtl/sim")

print("Step 1: Compiling RTL with Verilator...")
cmd = [
    "verilator", "--cc", "--trace", "--build", "-j", "4", "-O3",
    "-Wno-WIDTH", "-Wno-WIDTHTRUNC",
    "--top-module", "slime_top",
    "--Mdir", "obj_dir_fix",
    "-CFLAGS", "-std=c++17",
    "../src/slime_top.sv",
    "../src/agent_coordinator.sv",
    "../src/agent_processor.sv",
    "../src/lfsr.sv",
    "../src/fixed_point_mult.sv",
    "../src/trig_lut.sv",
    "../src/debouncer.sv",
    "../src/vga_controller.sv",
    "slime_verilator_full_tb.cpp"
]

try:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        print("ERROR: Compilation failed")
        print(result.stderr)
        sys.exit(1)
    print("Compilation successful!")
except Exception as e:
    print(f"ERROR during compilation: {e}")
    sys.exit(1)

print()
print("Step 2: Running simulation (100 agents, 1 step)...")
os.makedirs("rtl_trail_dumps", exist_ok=True)

try:
    result = subprocess.run(
        ["./obj_dir_fix/Vslime_top"],
        capture_output=True,
        text=True,
        timeout=60
    )
    # Print first 500 lines of output
    lines = result.stdout.split('\n')
    for line in lines[:500]:
        print(line)
except Exception as e:
    print(f"ERROR during simulation: {e}")
    sys.exit(1)

print()
print("Step 3: Checking trail dump...")
trail_file = "rtl_trail_dumps/trail_step_00000.bin"
if os.path.exists(trail_file):
    print("Trail dump exists!")
    size = os.path.getsize(trail_file)
    expected_size = 320 * 240 * 3
    print(f"File size: {size} bytes (expected: {expected_size} bytes)")

    # Check for non-zero values
    with open(trail_file, 'rb') as f:
        data = f.read()
        nonzero_count = sum(1 for b in data if b != 0)
        print(f"Non-zero bytes found: {nonzero_count}")

        if nonzero_count > 0:
            print("SUCCESS: Trail map contains non-zero values!")
            # Show first few non-zero values
            nonzero_vals = [b for b in data[:1000] if b != 0][:10]
            print(f"First non-zero values: {nonzero_vals}")
        else:
            print("FAILED: Trail map is all zeros")
            sys.exit(1)
else:
    print(f"ERROR: Trail dump not created at {trail_file}")
    sys.exit(1)

print()
print("=" * 73)
print("  FIX VERIFIED - TRAIL MAP HAS NON-ZERO VALUES")
print("=" * 73)
