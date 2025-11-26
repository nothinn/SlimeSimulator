#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================================================${NC}"
echo -e "${GREEN}  SLIME SIMULATOR - VERILATOR RTL SIMULATION BUILD${NC}"
echo -e "${GREEN}========================================================================${NC}"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="${SCRIPT_DIR}/build_verilator"
RTL_DIR="${SCRIPT_DIR}/../src"
BIN_DIR="${SCRIPT_DIR}/bin"

echo "Script directory: $SCRIPT_DIR"
echo "Build directory: $BUILD_DIR"
echo "RTL directory: $RTL_DIR"
echo ""

# Create build directory
echo -e "${YELLOW}[1/4]${NC} Creating build directory..."
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# Run CMake
echo -e "${YELLOW}[2/4]${NC} Running CMake..."
cd "$BUILD_DIR"
cmake .. || {
    echo -e "${RED}ERROR: CMake failed!${NC}"
    exit 1
}

# Build with make
echo -e "${YELLOW}[3/4]${NC} Building with make..."
make -j4 || {
    echo -e "${RED}ERROR: Build failed!${NC}"
    exit 1
}

# Check binary exists
if [ ! -f "$BIN_DIR/slime_sim" ]; then
    echo -e "${RED}ERROR: Binary not found at $BIN_DIR/slime_sim${NC}"
    exit 1
fi

echo -e "${YELLOW}[4/4]${NC} Running simulation..."
echo ""

# Run simulation
cd "$SCRIPT_DIR"
"$BIN_DIR/slime_sim" 2>&1 | tee rtl_simulation.log

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}========================================================================${NC}"
    echo -e "${GREEN}  BUILD AND SIMULATION COMPLETE${NC}"
    echo -e "${GREEN}========================================================================${NC}"
    echo ""
    echo "Binary location: $BIN_DIR/slime_sim"
    echo "Simulation log: $SCRIPT_DIR/rtl_simulation.log"
    echo "Trail dumps: $SCRIPT_DIR/rtl_trail_dumps/"
    echo ""
else
    echo -e "${RED}ERROR: Simulation failed!${NC}"
    exit 1
fi
