#!/bin/bash

##############################################################################
# Extended RTL vs Python Comparison - Complete Automation Script
#
# This script automates the entire 10× extended comparison workflow:
#   1. Builds Verilator binary (10,000 steps, dumps every 10 steps)
#   2. Runs RTL simulation to generate trail dumps
#   3. Runs Python reference simulation
#   4. Generates 1,000 side-by-side comparison images
#
# Usage: ./run_extended_comparison.sh [options]
#   --resolution WIDTHxHEIGHT   Resolution (default: 800x600)
#   --agents NUM                Number of agents (default: 100000)
#   --steps NUM                 Number of simulation steps (default: 10000)
#   --no-build                  Skip Verilator compilation
#   --no-rtl                    Skip RTL simulation
#   --help                      Show this help message
#
# Examples:
#   ./run_extended_comparison.sh                    # 800x600, 100k agents, 10k steps
#   ./run_extended_comparison.sh --resolution 320x240 --agents 1000 --steps 100
#   ./run_extended_comparison.sh --steps 100 --no-build
#
# Expected total time: 30-50 minutes (varies with resolution/agents)
# Expected disk space: ~5 GB
#
##############################################################################

set -e  # Exit on error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RTL_SIM_DIR="$SCRIPT_DIR/rtl/sim"
VENV_DIR="$SCRIPT_DIR/.venv"
TRAIL_DUMPS_DIR="$RTL_SIM_DIR/rtl_trail_dumps"

# Default values
RESOLUTION_WIDTH=800
RESOLUTION_HEIGHT=600
NUM_AGENTS=100000
NUM_STEPS=10000

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'  # No Color

# Flags
DO_BUILD=true
DO_RTL=true
VERBOSE=false

##############################################################################
# Helper Functions
##############################################################################

print_header() {
    echo ""
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_section() {
    echo -e "${CYAN}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "  $1"
}

show_help() {
    sed -n '3,17p' "$0" | sed 's/^# //'
    exit 0
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        print_error "Command not found: $1"
        echo "  Please install $1 and try again."
        return 1
    fi
    return 0
}

##############################################################################
# Parse Arguments
##############################################################################

while [[ $# -gt 0 ]]; do
    case $1 in
        --resolution)
            if [[ ! $2 =~ ^[0-9]+x[0-9]+$ ]]; then
                print_error "Invalid resolution format: $2"
                print_info "Use format: WIDTHxHEIGHT (e.g., 800x600)"
                exit 1
            fi
            RESOLUTION_WIDTH=$(echo "$2" | cut -d'x' -f1)
            RESOLUTION_HEIGHT=$(echo "$2" | cut -d'x' -f2)
            shift 2
            ;;
        --agents)
            if ! [[ "$2" =~ ^[0-9]+$ ]]; then
                print_error "Invalid agent count: $2"
                print_info "Must be a positive integer"
                exit 1
            fi
            NUM_AGENTS=$2
            shift 2
            ;;
        --steps)
            if ! [[ "$2" =~ ^[0-9]+$ ]]; then
                print_error "Invalid step count: $2"
                print_info "Must be a positive integer"
                exit 1
            fi
            NUM_STEPS=$2
            shift 2
            ;;
        --no-build)
            DO_BUILD=false
            shift
            ;;
        --no-rtl)
            DO_RTL=false
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            show_help
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            ;;
    esac
done

# Set output directory based on configuration
COMPARISON_OUTPUT_DIR="$SCRIPT_DIR/rtl_comparison_${RESOLUTION_WIDTH}x${RESOLUTION_HEIGHT}_${NUM_AGENTS}agents_${NUM_STEPS}steps"

##############################################################################
# Main Workflow
##############################################################################

print_header "RTL vs Python Extended Comparison"
print_info "Resolution: ${RESOLUTION_WIDTH}×${RESOLUTION_HEIGHT}"
print_info "Agents: $NUM_AGENTS"
print_info "Steps: $NUM_STEPS (dumps every 10 steps)"
print_info "Output: rtl_comparison_${RESOLUTION_WIDTH}x${RESOLUTION_HEIGHT}_${NUM_AGENTS}agents_${NUM_STEPS}steps/"
echo ""

# Verify environment
print_section "Checking environment..."

check_command python3 || exit 1
check_command verilator || exit 1

print_success "Python3 found: $(python3 --version)"
print_success "Verilator found: $(verilator --version | head -1)"

if [[ ! -d "$VENV_DIR" ]]; then
    print_error "Virtual environment not found at $VENV_DIR"
    echo "  Please create with: python3 -m venv $VENV_DIR"
    exit 1
fi
print_success "Virtual environment found"

echo ""

##############################################################################
# Phase 1: Verilator Compilation
##############################################################################

if [[ "$DO_BUILD" == true ]]; then
    print_header "Phase 1: Verilator Compilation (1-2 minutes)"

    cd "$RTL_SIM_DIR"

    print_section "Cleaning previous builds..."
    rm -rf obj_dir obj_dir_slime_top obj_dir_full 2>/dev/null || true
    print_success "Cleaned"

    print_section "Updating testbench with configuration..."
    print_info "  Width: $RESOLUTION_WIDTH, Height: $RESOLUTION_HEIGHT, Agents: $NUM_AGENTS"

    # Update testbench parameters
    sed -i.bak "s/const int NUM_AGENTS = [0-9]\+;/const int NUM_AGENTS = $NUM_AGENTS;/" slime_verilator_full_tb.cpp
    sed -i.bak "s/const int WIDTH = [0-9]\+;/const int WIDTH = $RESOLUTION_WIDTH;/" slime_verilator_full_tb.cpp
    sed -i.bak "s/const int HEIGHT = [0-9]\+;/const int HEIGHT = $RESOLUTION_HEIGHT;/" slime_verilator_full_tb.cpp
    sed -i.bak "s/const int NUM_STEPS = [0-9]\+;/const int NUM_STEPS = $NUM_STEPS;/" slime_verilator_full_tb.cpp

    print_success "Testbench updated"

    print_section "Running Verilator (this may take 30-90 seconds)..."

    verilator -cc --trace -Wno-fatal --exe \
        -I../src \
        --top-module slime_top \
        -GWIDTH=$RESOLUTION_WIDTH \
        -GHEIGHT=$RESOLUTION_HEIGHT \
        -GNUM_AGENTS=$NUM_AGENTS \
        -o slime_verilator_full \
        ../src/slime_top.sv ../src/*.sv \
        slime_verilator_full_tb.cpp

    print_success "Verilator compilation completed"

    print_section "Building C++ executable..."

    cd obj_dir || exit 1
    make -f Vslime_top.mk -j4

    cd "$RTL_SIM_DIR"

    if [[ ! -f obj_dir/slime_verilator_full ]]; then
        print_error "Executable not built!"
        exit 1
    fi

    print_success "Executable built: obj_dir/slime_verilator_full"

    echo ""
fi

##############################################################################
# Phase 2: RTL Simulation
##############################################################################

if [[ "$DO_RTL" == true ]]; then
    print_header "Phase 2: RTL Simulation (10-15 minutes)"

    print_section "Cleaning old trail dumps..."
    rm -rf "$TRAIL_DUMPS_DIR"
    mkdir -p "$TRAIL_DUMPS_DIR"
    print_success "Trail dump directory ready"

    print_section "Running RTL simulation (10,000 steps)..."
    print_info "This will generate ~1,001 trail dump files (every 10 steps)"
    print_info "Progress will be shown as a percentage..."
    echo ""

    cd "$RTL_SIM_DIR"

    # Copy LUT files needed by trig_lut module
    cp ../src/sin_lut.hex obj_dir/ 2>/dev/null || true
    cp ../src/cos_lut.hex obj_dir/ 2>/dev/null || true

    # Run simulation with output capture
    if [[ "$VERBOSE" == true ]]; then
        ./obj_dir/slime_verilator_full
    else
        ./obj_dir/slime_verilator_full 2>&1 | grep -E "(Processing|Progress|trail_map)" || true
    fi

    # Verify dumps were created
    DUMP_COUNT=$(find "$TRAIL_DUMPS_DIR" -name "trail_step_*.bin" -type f | wc -l)

    if [[ $DUMP_COUNT -eq 0 ]]; then
        print_error "No trail dumps generated!"
        print_info "Check if RTL simulation crashed or wrote to different directory"
        exit 1
    fi

    print_success "RTL simulation completed"
    print_info "Generated $DUMP_COUNT trail dump files"
    print_info "Directory size: $(du -sh "$TRAIL_DUMPS_DIR" | cut -f1)"

    echo ""
fi

##############################################################################
# Phase 3: Python Reference Simulation & Comparison
##############################################################################

print_header "Phase 3: Comparison Generation (10-20 minutes)"

# Activate virtual environment
print_section "Activating Python virtual environment..."
source "$VENV_DIR/bin/activate"
print_success "Virtual environment activated"

cd "$SCRIPT_DIR"

print_section "Running Python reference simulation..."
print_info "Processing $NUM_AGENTS agents × $NUM_STEPS steps..."
print_info "Resolution: ${RESOLUTION_WIDTH}×${RESOLUTION_HEIGHT}"
echo ""

# Run comparison with progress
python3 rtl_final_comparison.py \
    --output "$COMPARISON_OUTPUT_DIR" \
    --width "$RESOLUTION_WIDTH" \
    --height "$RESOLUTION_HEIGHT" \
    --agents "$NUM_AGENTS" \
    --steps "$NUM_STEPS"

# Verify output
if [[ ! -d "$COMPARISON_OUTPUT_DIR" ]]; then
    print_warning "Using default output directory rtl_final_comparison_100k"
    COMPARISON_OUTPUT_DIR="$SCRIPT_DIR/rtl_final_comparison_100k"
fi

if [[ ! -d "$COMPARISON_OUTPUT_DIR" ]]; then
    print_error "Comparison output directory not found!"
    exit 1
fi

FRAME_COUNT=$(find "$COMPARISON_OUTPUT_DIR" -name "comparison_*.png" -type f | wc -l)

if [[ $FRAME_COUNT -eq 0 ]]; then
    print_error "No comparison frames generated!"
    exit 1
fi

echo ""
print_success "Comparison generation completed"
print_info "Generated $FRAME_COUNT comparison frames"
print_info "Directory size: $(du -sh "$COMPARISON_OUTPUT_DIR" | cut -f1)"

echo ""

##############################################################################
# Summary & Next Steps
##############################################################################

print_header "COMPARISON COMPLETE"

print_info "⚙️  Configuration:"
print_info "  • Resolution: ${RESOLUTION_WIDTH}×${RESOLUTION_HEIGHT}"
print_info "  • Agents: $NUM_AGENTS"
print_info "  • Steps: $NUM_STEPS (dumps every 10 steps)"
echo ""

print_info "📊 Results Summary:"
print_info "  • RTL trail dumps: $DUMP_COUNT files"
print_info "  • Comparison frames: $FRAME_COUNT PNG images"
print_info "  • Output directory: $COMPARISON_OUTPUT_DIR"
print_info "  • Statistics JSON: $COMPARISON_OUTPUT_DIR/comparison_stats.json"

echo ""
print_info "📈 Next Steps:"
print_info "  1. Review comparison frames:"
print_info "     open $COMPARISON_OUTPUT_DIR/comparison_00000.png"
print_info "     open $COMPARISON_OUTPUT_DIR/comparison_05000.png"
print_info "     open $COMPARISON_OUTPUT_DIR/comparison_09999.png"
print_info ""
print_info "  2. Analyze statistics:"
print_info "     python3 -c \"import json; s=json.load(open('$COMPARISON_OUTPUT_DIR/comparison_stats.json')); \""
print_info "     [check min/max/mean trends]"
print_info ""
print_info "  3. Look for patterns:"
print_info "     • Do agents form networks?"
print_info "     • Does trail intensity grow over time?"
print_info "     • Are Python and RTL visually similar?"

echo ""
print_info "💾 Disk Usage:"
print_info "  RTL dumps: $(du -sh "$TRAIL_DUMPS_DIR" 2>/dev/null | cut -f1 || echo "unknown")"
print_info "  Comparison images: $(du -sh "$COMPARISON_OUTPUT_DIR" 2>/dev/null | cut -f1 || echo "unknown")"
print_info "  Total: $(du -sh "$SCRIPT_DIR" 2>/dev/null | cut -f1 || echo "unknown")"

echo ""
print_info "📝 Documentation:"
print_info "  • EXTENDED_COMPARISON_GUIDE.md - Detailed instructions"
print_info "  • COMPARISON_ARCHITECTURE.md - Technical deep-dive"
print_info "  • CLAUDE.md - Project overview"

echo ""
print_success "All phases completed successfully!"

# Deactivate virtual environment
deactivate

exit 0
