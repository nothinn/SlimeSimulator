#!/bin/bash
# Quick Start Script for Slime Simulator Testing
# This script demonstrates the complete workflow

set -e  # Exit on error

echo "=================================================="
echo "Slime Simulator - Quick Start"
echo "=================================================="
echo ""

# Check if we're in the right directory
if [ ! -f "generate_xpr.tcl" ]; then
    echo "ERROR: Must run from rtl/ directory"
    exit 1
fi

# Activate Python environment
if [ -f "../.venv/bin/activate" ]; then
    echo "✓ Activating Python virtual environment..."
    source ../.venv/bin/activate
else
    echo "⚠ Warning: Virtual environment not found at ../.venv/"
    echo "  Install dependencies: python3 -m venv ../.venv && pip install numpy matplotlib"
fi

# Step 1: Generate Vivado Project (optional - can skip if already exists)
if [ "$1" = "--full" ]; then
    echo ""
    echo "[Step 1/3] Generating Vivado project..."
    if command -v vivado &> /dev/null; then
        vivado -mode batch -source generate_xpr.tcl
        echo "✓ Project generated"
    else
        echo "⚠ Vivado not found - skipping project generation"
    fi
fi

# Step 2: Build FPGA Bitstream (optional - very time consuming)
if [ "$1" = "--full" ] && [ "$2" = "--build" ]; then
    echo ""
    echo "[Step 2/3] Building FPGA bitstream (this takes 5-15 minutes)..."
    if command -v vivado &> /dev/null; then
        vivado -mode batch -source build.tcl
        echo "✓ Build complete"
    else
        echo "⚠ Vivado not found - skipping build"
    fi
fi

# Step 3: Run Tests
echo ""
echo "[Step 3/3] Running comprehensive tests..."
python3 comprehensive_test.py \
    --skip-rtl-sim \
    --skip-fpga \
    --iterations 1,5,10,20 \
    --output-dir test_results_quickstart

echo ""
echo "=================================================="
echo "Quick Start Complete!"
echo "=================================================="
echo ""
echo "Results:"
echo "  - Test report: test_results_quickstart/COMPREHENSIVE_TEST_REPORT.md"
echo "  - Trail maps:  test_results_quickstart/python_reference/iter_*/python_trail.png"
echo ""
echo "Next steps:"
echo "  1. View report:      cat test_results_quickstart/COMPREHENSIVE_TEST_REPORT.md"
echo "  2. Check images:     ls test_results_quickstart/python_reference/iter_*/python_trail.png"
echo "  3. Run full guide:   cat BUILD_AND_TEST_GUIDE.md"
echo ""
echo "For full workflow including Vivado:"
echo "  ./QUICK_START.sh --full"
echo ""
echo "For complete build (WARNING: takes 10+ minutes):"
echo "  ./QUICK_START.sh --full --build"
echo ""
