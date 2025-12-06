#!/bin/bash
# Quick reference script for running 2x movement bug tests

set -e

echo "========================================================================"
echo "2x Movement Scaling Bug - Cocotb Testbench"
echo "========================================================================"
echo ""

# Check we're in the right directory
if [ ! -f "Makefile" ] || [ ! -f "test_2x_movement_bug.py" ]; then
    echo "ERROR: This script must be run from rtl/sim directory"
    echo "Usage: cd rtl/sim && bash RUN_2X_BUG_TEST.sh"
    exit 1
fi

# Activate venv
if [ ! -d "../../.venv" ]; then
    echo "ERROR: Python venv not found at ../../.venv"
    exit 1
fi

source ../../.venv/bin/activate

echo "Test Configuration:"
echo "  - Testbench: test_2x_movement_bug.py"
echo "  - Module: agent_sim_tb (full simulator)"
echo "  - Tests: 3 (right direction, diagonal, components)"
echo "  - Duration: < 3 seconds"
echo ""

echo "Running tests..."
echo ""

cd $(dirname "${BASH_SOURCE[0]}")
make clean
make test_2x_movement_bug 2>&1 | tee 2x_bug_test_output.log

echo ""
echo "========================================================================"
echo "Test Complete"
echo "========================================================================"
echo ""
echo "Log saved to: 2x_bug_test_output.log"
echo ""
echo "Test Results:"
grep -E "PASSED|FAILED|ERROR" 2x_bug_test_output.log | head -10 || echo "  (Check log above for details)"
echo ""
echo "Key Lines to Check:"
echo "  1. Look for 'Expected movement' values in the log"
echo "  2. Compare with 'observed' values in agent dumps"
echo "  3. If ratio ≈ 2.0, the 2x bug is confirmed"
echo ""
echo "For detailed analysis:"
echo "  vim 2x_bug_test_output.log"
echo ""
