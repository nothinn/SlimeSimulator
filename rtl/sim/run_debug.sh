#!/bin/bash
set -e

cd /home/reson/SlimeSimulator/rtl/sim

echo "Compiling RTL with Verilator..."
verilator --cc --trace --build -j 4 -O3 -Wno-WIDTH -Wno-WIDTHTRUNC \
    --top-module slime_top \
    --Mdir obj_dir_debug \
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

echo ""
echo "Running simulation..."
mkdir -p rtl_trail_dumps
./obj_dir_debug/Vslime_top 2>&1 | tee debug_output.log
