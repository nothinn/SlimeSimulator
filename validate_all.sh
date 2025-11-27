#!/bin/bash
#
# Agent Initialization Validation - All-in-One Script
#
# This script runs the complete validation pipeline:
# 1. Compile RTL validator testbench with Verilator
# 2. Run Python validation to generate reference data
# 3. Run RTL testbench to extract agent state
# 4. Compare Python vs RTL and generate reports
# 5. Create visualization plots
#
# Usage:
#   ./validate_all.sh [options]
#
# Options:
#   --resolution WxH     Simulation resolution (default: 320x240)
#   --agents NUM         Number of agents (default: 1000)
#   --num-validate NUM   Number of agents to validate (default: all)
#   --no-build           Skip RTL compilation (use existing binary)
#   --no-rtl             Skip RTL simulation (use existing data)
#   --no-python          Skip Python validation (use existing data)
#   --help               Show this help message

set -e  # Exit on error

# Default parameters
RESOLUTION="320x240"
NUM_AGENTS=1000
NUM_VALIDATE=""
DO_BUILD=1
DO_RTL=1
DO_PYTHON=1

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --resolution)
            RESOLUTION="$2"
            shift 2
            ;;
        --agents)
            NUM_AGENTS="$2"
            shift 2
            ;;
        --num-validate)
            NUM_VALIDATE="$2"
            shift 2
            ;;
        --no-build)
            DO_BUILD=0
            shift
            ;;
        --no-rtl)
            DO_RTL=0
            shift
            ;;
        --no-python)
            DO_PYTHON=0
            shift
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --resolution WxH     Simulation resolution (default: 320x240)"
            echo "  --agents NUM         Number of agents (default: 1000)"
            echo "  --num-validate NUM   Number of agents to validate (default: all)"
            echo "  --no-build           Skip RTL compilation (use existing binary)"
            echo "  --no-rtl             Skip RTL simulation (use existing data)"
            echo "  --no-python          Skip Python validation (use existing data)"
            echo "  --help               Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Run with --help for usage information"
            exit 1
            ;;
    esac
done

# Parse resolution
IFS='x' read -r WIDTH HEIGHT <<< "$RESOLUTION"

echo "========================================"
echo "Agent Initialization Validation"
echo "========================================"
echo ""
echo "Configuration:"
echo "  Resolution: ${WIDTH}x${HEIGHT}"
echo "  Agents: $NUM_AGENTS"
if [ -n "$NUM_VALIDATE" ]; then
    echo "  Validate: $NUM_VALIDATE agents"
else
    echo "  Validate: All agents"
fi
echo ""

# Activate Python virtual environment
if [ -f ".venv/bin/activate" ]; then
    echo "[1/6] Activating Python virtual environment..."
    source .venv/bin/activate
else
    echo "WARNING: Python virtual environment not found at .venv/"
    echo "Please run: python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
fi

# Step 1: Compile RTL validator testbench
if [ $DO_BUILD -eq 1 ]; then
    echo ""
    echo "[2/6] Compiling RTL validator testbench with Verilator..."
    echo "------------------------------------------------------------"

    cd rtl/sim

    # Remove old build
    rm -rf obj_dir

    # Compile with Verilator
    # Include all necessary RTL files
    verilator -Wall -Wno-fatal \
        --cc ../../rtl/src/slime_top.sv \
        ../../rtl/src/debouncer.sv \
        ../../rtl/src/lfsr.sv \
        ../../rtl/src/vga_controller.sv \
        ../../rtl/src/agent_coordinator.sv \
        ../../rtl/src/agent_processor.sv \
        ../../rtl/src/trig_lut.sv \
        ../../rtl/src/fixed_point_mult.sv \
        --exe agent_init_validator_tb.cpp \
        -I../../rtl/src \
        --top-module slime_top \
        -CFLAGS "-std=c++17 -O2" \
        --build

    if [ $? -ne 0 ]; then
        echo "ERROR: Verilator compilation failed!"
        exit 1
    fi

    cd ../..

    echo "✓ RTL validator compiled successfully"
else
    echo ""
    echo "[2/6] Skipping RTL compilation (using existing binary)"
fi

# Step 2: Run Python validation
if [ $DO_PYTHON -eq 1 ]; then
    echo ""
    echo "[3/6] Running Python validation..."
    echo "------------------------------------------------------------"

    PYTHON_ARGS="--resolution $RESOLUTION --agents $NUM_AGENTS"
    if [ -n "$NUM_VALIDATE" ]; then
        PYTHON_ARGS="$PYTHON_ARGS --num-validate $NUM_VALIDATE"
    fi

    python3 validate_agent_initialization.py $PYTHON_ARGS

    if [ $? -ne 0 ]; then
        echo "ERROR: Python validation failed!"
        exit 1
    fi

    echo "✓ Python validation complete"
else
    echo ""
    echo "[3/6] Skipping Python validation (using existing data)"
fi

# Step 3: Run RTL testbench
if [ $DO_RTL -eq 1 ]; then
    echo ""
    echo "[4/6] Running RTL testbench..."
    echo "------------------------------------------------------------"

    cd rtl/sim

    RTL_ARGS=""
    if [ -n "$NUM_VALIDATE" ]; then
        RTL_ARGS="--num-validate $NUM_VALIDATE"
    fi

    ./obj_dir/Vslime_top $RTL_ARGS

    if [ $? -ne 0 ]; then
        echo "ERROR: RTL testbench failed!"
        exit 1
    fi

    # Move RTL validation output to project root
    if [ -f rtl_agent_validation.json ]; then
        mv rtl_agent_validation.json ../../
    fi

    cd ../..

    echo "✓ RTL testbench complete"
else
    echo ""
    echo "[4/6] Skipping RTL testbench (using existing data)"
fi

# Step 4: Compare Python vs RTL
echo ""
echo "[5/6] Comparing Python vs RTL..."
echo "------------------------------------------------------------"

python3 compare_agent_initialization.py

COMPARISON_RESULT=$?

if [ $COMPARISON_RESULT -ne 0 ]; then
    echo "⚠ Comparison found discrepancies (see report for details)"
else
    echo "✓ Comparison complete - all agents match!"
fi

# Step 5: Create visualizations
echo ""
echo "[6/6] Creating visualization plots..."
echo "------------------------------------------------------------"

python3 visualize_agent_init.py

if [ $? -ne 0 ]; then
    echo "WARNING: Visualization failed (may be missing matplotlib)"
else
    echo "✓ Visualizations created"
fi

# Final summary
echo ""
echo "========================================"
echo "Validation Complete!"
echo "========================================"
echo ""
echo "Output files:"
echo "  • python_agent_validation.json      - Python reference data"
echo "  • rtl_agent_validation.json         - RTL implementation data"
echo "  • agent_validation_report.txt       - Human-readable comparison report"
echo "  • agent_validation_report.json      - Machine-readable comparison data"
echo "  • agent_comparison.png              - Visual comparison plot"
echo "  • agent_error_distribution.png      - Error distribution analysis"
echo "  • agent_polar_distribution.png      - Polar distribution view"
echo ""

if [ $COMPARISON_RESULT -eq 0 ]; then
    echo "✓ VALIDATION PASSED - All agents within tolerance"
    echo ""
    echo "Next steps:"
    echo "  1. Review agent_validation_report.txt for detailed results"
    echo "  2. View agent_comparison.png for visual verification"
    exit 0
else
    echo "✗ VALIDATION FAILED - Some agents outside tolerance"
    echo ""
    echo "Next steps:"
    echo "  1. Review agent_validation_report.txt for failed agents"
    echo "  2. View agent_comparison.png to see failed agent positions"
    echo "  3. Check RTL initialization logic in rtl/src/agent_coordinator.sv"
    exit 1
fi
