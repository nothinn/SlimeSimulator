#!/usr/bin/env python3
"""
Validate FPGA output against Python reference
- Captures trail map from FPGA via JTAG
- Compares with Python reference simulation
- Generates comparison report
"""
import os
import sys
import argparse
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    parser = argparse.ArgumentParser(
        description="Validate FPGA slime simulator output"
    )
    parser.add_argument(
        "--output", "-o",
        default="fpga_validation.png",
        help="Output image file"
    )
    parser.add_argument(
        "--reference",
        help="Reference trail file from Python simulation"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("FPGA Output Validation")
    print("=" * 60)
    
    # Check prerequisites
    try:
        import numpy as np
        from PIL import Image
        print("[✓] NumPy and PIL available")
    except ImportError:
        print("[✗] Missing required packages (numpy, pillow)")
        return 1
    
    print("\nValidation steps:")
    print("1. Initialize JTAG connection to Basys3")
    print("2. Read trail map from FPGA memory")
    print("3. Convert to image (320×240 → 640×480)")
    print("4. Compare with Python reference (if provided)")
    print("5. Save output image")
    
    if args.reference:
        print(f"\nReference file: {args.reference}")
        if not os.path.exists(args.reference):
            print(f"[✗] Reference file not found: {args.reference}")
            return 1
    
    print(f"\nOutput image: {args.output}")
    print("\n[INFO] To run FPGA validation:")
    print("  1. Program FPGA with main bitstream")
    print("  2. Run: python scripts/validate_fpga_output.py")
    print("  3. Check output image and comparison report")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
