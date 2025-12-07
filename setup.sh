#!/bin/bash
# SlimeSimulator Repository Setup Script
#
# This script initializes the Python virtual environment and installs
# all required dependencies for development and testing.
#
# Usage: ./setup.sh

set -e  # Exit on error

echo "=== SlimeSimulator Repository Setup ==="
echo ""

# Check Python version
echo "[1/4] Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 not found. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "Found Python $PYTHON_VERSION"
echo ""

# Create virtual environment
echo "[2/4] Creating Python virtual environment..."
if [ -d ".venv" ]; then
    echo "Virtual environment already exists. Skipping creation."
else
    python3 -m venv .venv
    echo "Virtual environment created at .venv/"
fi
echo ""

# Activate virtual environment
echo "[3/4] Activating virtual environment..."
source .venv/bin/activate
echo "Virtual environment activated"
echo ""

# Install dependencies
echo "[4/4] Installing Python dependencies..."
pip install --upgrade pip
pip install \
    cocotb==2.0.1 \
    numpy==2.3.5 \
    pillow==12.0.0 \
    scipy==1.16.3 \
    pygame \
    git-filter-repo

echo ""
echo "=== Setup Complete ==="
echo ""
echo "To activate the virtual environment in the future, run:"
echo "  source .venv/bin/activate"
echo ""
echo "To run regression tests:"
echo "  source .venv/bin/activate"
echo "  python3 run_regression_tests.py"
echo ""
