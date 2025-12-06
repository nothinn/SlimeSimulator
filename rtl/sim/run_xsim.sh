#!/bin/bash
# Run xsim simulation with Vivado

cd "$(dirname "$0")"

# Check if Vivado is available
if ! command -v vivado &> /dev/null; then
    echo "ERROR: Vivado not found. Please source Vivado environment."
    echo "Run: source ~/2025.2/Vivado/.settings64-Vivado.sh"
    exit 1
fi

echo "========================================="
echo "Running xsim SystemVerilog Testbench"
echo "========================================="
echo ""

# Run xsim
vivado -mode batch -source run_xsim.tcl -log xsim_batch.log -journal xsim.jou

# Check results
if [ -f xsim_batch.log ]; then
    echo ""
    echo "========================================="
    echo "Simulation Output:"
    echo "========================================="
    grep -E "COORD STATE|STEP COMPLETE|Agent\[0\] processing|Initializing" xsim_batch.log
    echo ""
    echo "========================================="
    echo "Full log: xsim_batch.log"
    echo "========================================="
fi
