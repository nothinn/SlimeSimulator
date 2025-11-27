#!/bin/bash
set -e

echo "========================================================================="
echo "  TESTING AGENT_COORDINATOR FIX"
echo "========================================================================="
echo ""

cd /home/reson/SlimeSimulator/rtl/sim

echo "Step 1: Compiling RTL with Verilator..."
verilator --cc --trace --build -j 4 -O3 -Wno-WIDTH -Wno-WIDTHTRUNC \
    --top-module slime_top \
    --Mdir obj_dir_fix \
    -CFLAGS "-std=c++17" \
    ../src/slime_top.sv \
    ../src/agent_coordinator.sv \
    ../src/agent_processor.sv \
    ../src/lfsr.sv \
    ../src/fixed_point_mult.sv \
    ../src/trig_lut.sv \
    ../src/debouncer.sv \
    ../src/vga_controller.sv \
    slime_verilator_full_tb.cpp

if [ $? -ne 0 ]; then
    echo "ERROR: Compilation failed"
    exit 1
fi

echo ""
echo "Step 2: Running simulation (100 agents, 1 step)..."
mkdir -p rtl_trail_dumps
./obj_dir_fix/Vslime_top 2>&1 | head -500

echo ""
echo "Step 3: Checking trail dump..."
if [ -f rtl_trail_dumps/trail_step_00000.bin ]; then
    echo "Trail dump exists!"
    # Check file size
    SIZE=$(stat -c%s rtl_trail_dumps/trail_step_00000.bin)
    echo "File size: $SIZE bytes (expected: $((320*240*3)) = 230400 bytes)"

    # Check for non-zero values using od
    NONZERO=$(od -An -tu1 rtl_trail_dumps/trail_step_00000.bin | tr ' ' '\n' | grep -v '^$' | grep -v '^0$' | head -10 | wc -l)
    echo "Non-zero bytes found: $NONZERO"

    if [ $NONZERO -gt 0 ]; then
        echo "SUCCESS: Trail map contains non-zero values!"
    else
        echo "FAILED: Trail map is all zeros"
        exit 1
    fi
else
    echo "ERROR: Trail dump not created"
    exit 1
fi

echo ""
echo "========================================================================="
echo "  FIX VERIFIED - TRAIL MAP HAS NON-ZERO VALUES"
echo "========================================================================="
