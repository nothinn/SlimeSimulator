#!/usr/bin/env python3
"""
Download trail map image from FPGA via JTAG and compare with Python model.

This script uses Vivado's hw_server and JTAG-to-AXI to read the trail memory
from the FPGA and save it as an image for comparison with the Python simulation.

Usage:
    python download_image.py [--output image.png] [--compare python_dump.bin]

Requirements:
    - Vivado installed and in PATH
    - FPGA programmed with debug-enabled bitstream
    - numpy, PIL for image processing
"""

import argparse
import subprocess
import tempfile
import os
import sys
import struct
from pathlib import Path

try:
    import numpy as np
    from PIL import Image
except ImportError:
    print("Please install: pip install numpy pillow")
    sys.exit(1)


# Image dimensions (must match RTL parameters)
WIDTH = 640
HEIGHT = 480
TRAIL_MEM_SIZE = WIDTH * HEIGHT

# AXI address map
TRAIL_MEM_BASE = 0x00000000
CTRL_REG_BASE = 0x00100000


def create_vivado_tcl(output_file: str, start_addr: int, num_bytes: int) -> str:
    """Generate TCL script for reading memory via JTAG-to-AXI."""

    tcl_script = f'''
# Auto-generated TCL script for reading trail memory
# Output file: {output_file}

proc read_trail_memory {{output_file start_addr num_bytes}} {{
    set chunk_size 256
    set data_list {{}}

    puts "Reading $num_bytes bytes from address [format 0x%08X $start_addr]..."

    for {{set addr $start_addr}} {{$addr < ($start_addr + $num_bytes)}} {{incr addr $chunk_size}} {{
        set remaining [expr ($start_addr + $num_bytes) - $addr]
        set read_size [expr min($chunk_size, $remaining)]

        # Read via JTAG-to-AXI
        for {{set i 0}} {{$i < $read_size}} {{incr i}} {{
            set rd_addr [expr $addr + $i]
            create_hw_axi_txn rd_txn [get_hw_axis hw_axi_1] -type READ -address [format %08X $rd_addr] -len 1
            run_hw_axi rd_txn
            set rd_data [get_property DATA [get_hw_axi_txn rd_txn]]
            # Extract byte (data comes as hex string)
            set byte_val [expr 0x$rd_data & 0xFF]
            lappend data_list $byte_val
            delete_hw_axi_txn rd_txn
        }}

        # Progress indicator
        set progress [expr (($addr - $start_addr + $read_size) * 100) / $num_bytes]
        puts -nonewline "\\rProgress: $progress%"
        flush stdout
    }}

    puts "\\nWriting to $output_file..."

    # Write binary file
    set fp [open $output_file wb]
    foreach byte $data_list {{
        puts -nonewline $fp [binary format c $byte]
    }}
    close $fp

    puts "Done! Read [llength $data_list] bytes"
}}

# Connect to hardware
open_hw_manager
connect_hw_server -allow_non_jtag
open_hw_target

# Find JTAG-to-AXI core
refresh_hw_device [lindex [get_hw_devices] 0]

# Check for JTAG-to-AXI
set axi_cores [get_hw_axis]
if {{[llength $axi_cores] == 0}} {{
    puts "ERROR: No JTAG-to-AXI core found!"
    puts "Make sure the debug-enabled bitstream is loaded."
    exit 1
}}

puts "Found JTAG-to-AXI core: $axi_cores"

# Read trail memory
read_trail_memory "{output_file}" {start_addr} {num_bytes}

# Cleanup
close_hw_target
disconnect_hw_server
close_hw_manager

puts "Trail memory saved to: {output_file}"
'''
    return tcl_script


def create_vivado_tcl_fast(output_file: str) -> str:
    """Generate optimized TCL script using burst reads."""

    tcl_script = f'''
# Optimized TCL script for reading trail memory via JTAG-to-AXI
# Uses burst reads for faster transfer

set output_file "{output_file}"
set width {WIDTH}
set height {HEIGHT}
set total_bytes [expr $width * $height]

# Connect to hardware
open_hw_manager
connect_hw_server -allow_non_jtag
open_hw_target
refresh_hw_device [lindex [get_hw_devices] 0]

# Find JTAG-to-AXI core
set axi_cores [get_hw_axis]
if {{[llength $axi_cores] == 0}} {{
    puts "ERROR: No JTAG-to-AXI core found!"
    exit 1
}}

set axi_core [lindex $axi_cores 0]
puts "Using AXI core: $axi_core"

# First, freeze the simulation via control register
puts "Freezing simulation..."
create_hw_axi_txn freeze_txn $axi_core -type WRITE -address {CTRL_REG_BASE:08X} -data 00000001 -len 1
run_hw_axi freeze_txn
delete_hw_axi_txn freeze_txn

# Read memory in chunks using burst reads
puts "Reading trail memory ($total_bytes bytes)..."

set data_list {{}}
set chunk_size 64
set start_time [clock seconds]

for {{set addr 0}} {{$addr < $total_bytes}} {{incr addr $chunk_size}} {{
    set remaining [expr $total_bytes - $addr]
    set read_len [expr min($chunk_size, $remaining)]

    # Create burst read transaction
    create_hw_axi_txn rd_txn $axi_core -type READ \\
        -address [format %08X $addr] -len $read_len -size 8
    run_hw_axi rd_txn

    # Get data
    set rd_data [get_property DATA [get_hw_axi_txn rd_txn]]

    # Parse hex string to bytes (data comes in reverse order per word)
    for {{set i 0}} {{$i < [string length $rd_data]}} {{incr i 2}} {{
        set byte_hex [string range $rd_data $i [expr $i+1]]
        lappend data_list [expr 0x$byte_hex]
    }}

    delete_hw_axi_txn rd_txn

    # Progress every 10%
    set progress [expr (($addr + $read_len) * 100) / $total_bytes]
    if {{($addr % ($total_bytes / 10)) < $chunk_size}} {{
        puts "Progress: $progress%"
    }}
}}

set elapsed [expr [clock seconds] - $start_time]
puts "Read complete in $elapsed seconds"

# Unfreeze simulation
puts "Unfreezing simulation..."
create_hw_axi_txn unfreeze_txn $axi_core -type WRITE -address {CTRL_REG_BASE:08X} -data 00000000 -len 1
run_hw_axi unfreeze_txn
delete_hw_axi_txn unfreeze_txn

# Write binary file
puts "Writing to $output_file..."
set fp [open $output_file wb]
foreach byte $data_list {{
    puts -nonewline $fp [binary format c $byte]
}}
close $fp

puts "Saved [llength $data_list] bytes to $output_file"

# Cleanup
close_hw_target
disconnect_hw_server
close_hw_manager
'''
    return tcl_script


def run_vivado_tcl(tcl_script: str) -> bool:
    """Execute TCL script in Vivado."""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.tcl', delete=False) as f:
        f.write(tcl_script)
        tcl_file = f.name

    try:
        print(f"Running Vivado TCL script...")
        result = subprocess.run(
            ['vivado', '-mode', 'batch', '-source', tcl_file],
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )

        if result.returncode != 0:
            print(f"Vivado error:\n{result.stderr}")
            return False

        print(result.stdout)
        return True

    except FileNotFoundError:
        print("ERROR: Vivado not found in PATH")
        print("Please source Vivado settings: source /path/to/Vivado/settings64.sh")
        return False
    except subprocess.TimeoutExpired:
        print("ERROR: Vivado timed out")
        return False
    finally:
        os.unlink(tcl_file)


def binary_to_image(bin_file: str, output_image: str, width: int = WIDTH, height: int = HEIGHT):
    """Convert binary trail data to PNG image."""

    with open(bin_file, 'rb') as f:
        data = f.read()

    if len(data) != width * height:
        print(f"Warning: Expected {width*height} bytes, got {len(data)}")

    # Create numpy array
    arr = np.frombuffer(data[:width*height], dtype=np.uint8)
    arr = arr.reshape((height, width))

    # Create image (green channel for slime look)
    img_arr = np.zeros((height, width, 3), dtype=np.uint8)
    img_arr[:, :, 1] = arr  # Green channel
    img_arr[:, :, 0] = arr // 4  # Slight red tint

    img = Image.fromarray(img_arr, mode='RGB')
    img.save(output_image)
    print(f"Saved image to: {output_image}")

    return arr


def compare_images(fpga_data: np.ndarray, python_file: str) -> dict:
    """Compare FPGA capture with Python simulation output."""

    # Load Python reference
    if python_file.endswith('.bin'):
        with open(python_file, 'rb') as f:
            py_data = np.frombuffer(f.read(), dtype=np.uint8)
            py_data = py_data.reshape(fpga_data.shape)
    elif python_file.endswith('.npy'):
        py_data = np.load(python_file)
    else:
        # Assume it's an image
        py_img = Image.open(python_file).convert('L')
        py_data = np.array(py_img)

    # Calculate statistics
    diff = fpga_data.astype(np.int16) - py_data.astype(np.int16)
    abs_diff = np.abs(diff)

    results = {
        'match_percent': np.mean(fpga_data == py_data) * 100,
        'max_diff': np.max(abs_diff),
        'mean_diff': np.mean(abs_diff),
        'std_diff': np.std(abs_diff),
        'mse': np.mean(diff ** 2),
        'pixels_differ': np.sum(fpga_data != py_data),
        'total_pixels': fpga_data.size
    }

    # Create diff image
    diff_img = np.zeros((fpga_data.shape[0], fpga_data.shape[1], 3), dtype=np.uint8)
    diff_img[:, :, 0] = np.clip(abs_diff * 10, 0, 255)  # Red for differences
    diff_img[:, :, 1] = np.where(fpga_data == py_data, fpga_data, 0)  # Green for matches

    diff_image = Image.fromarray(diff_img, mode='RGB')
    diff_image.save('fpga_python_diff.png')

    return results


def download_via_vio(output_file: str):
    """Download using VIO for manual control (alternative method)."""

    tcl_script = f'''
# Download trail memory using VIO control
# This method allows manual triggering via VIO probes

open_hw_manager
connect_hw_server -allow_non_jtag
open_hw_target
refresh_hw_device [lindex [get_hw_devices] 0]

# Find VIO core
set vio_cores [get_hw_vios]
if {{[llength $vio_cores] == 0}} {{
    puts "ERROR: No VIO core found!"
    exit 1
}}

set vio [lindex $vio_cores 0]
puts "Using VIO: $vio"

# Trigger capture (freeze on next frame)
set_property OUTPUT_VALUE 1 [get_hw_probes probe_out0 -of_objects $vio]
commit_hw_vio $vio
after 100
set_property OUTPUT_VALUE 0 [get_hw_probes probe_out0 -of_objects $vio]
commit_hw_vio $vio

# Wait for capture done
puts "Waiting for capture..."
for {{set i 0}} {{$i < 100}} {{incr i}} {{
    refresh_hw_vio $vio
    set done [get_property INPUT_VALUE [get_hw_probes probe_in0 -of_objects $vio]]
    if {{$done == 1}} {{
        puts "Capture complete!"
        break
    }}
    after 100
}}

# Enable read mode and read all pixels
set_property OUTPUT_VALUE 1 [get_hw_probes probe_out2 -of_objects $vio]
commit_hw_vio $vio

set data_list {{}}
set total_pixels [expr {WIDTH} * {HEIGHT}]

for {{set addr 0}} {{$addr < $total_pixels}} {{incr addr}} {{
    # Set read address
    set_property OUTPUT_VALUE [format %d $addr] [get_hw_probes probe_out3 -of_objects $vio]
    commit_hw_vio $vio

    # Small delay for BRAM read
    after 1

    # Read data
    refresh_hw_vio $vio
    set pixel [get_property INPUT_VALUE [get_hw_probes probe_in2 -of_objects $vio]]
    lappend data_list [expr 0x$pixel]

    if {{($addr % 10000) == 0}} {{
        puts "Progress: [expr ($addr * 100) / $total_pixels]%"
    }}
}}

# Disable read mode
set_property OUTPUT_VALUE 0 [get_hw_probes probe_out2 -of_objects $vio]
commit_hw_vio $vio

# Write file
set fp [open "{output_file}" wb]
foreach byte $data_list {{
    puts -nonewline $fp [binary format c $byte]
}}
close $fp

puts "Saved to {output_file}"

close_hw_target
disconnect_hw_server
close_hw_manager
'''
    return tcl_script


def main():
    parser = argparse.ArgumentParser(description='Download FPGA trail map image')
    parser.add_argument('-o', '--output', default='fpga_capture.png',
                        help='Output image file')
    parser.add_argument('-b', '--binary', default='fpga_trail.bin',
                        help='Raw binary output file')
    parser.add_argument('-c', '--compare',
                        help='Python reference file to compare against')
    parser.add_argument('--method', choices=['jtag', 'vio'], default='jtag',
                        help='Download method (jtag=faster, vio=manual control)')
    parser.add_argument('--tcl-only', action='store_true',
                        help='Only generate TCL script, do not run')

    args = parser.parse_args()

    # Generate TCL script
    if args.method == 'jtag':
        tcl_script = create_vivado_tcl_fast(args.binary)
    else:
        tcl_script = download_via_vio(args.binary)

    if args.tcl_only:
        print(tcl_script)
        return

    # Run Vivado
    if not run_vivado_tcl(tcl_script):
        sys.exit(1)

    # Convert to image
    if os.path.exists(args.binary):
        fpga_data = binary_to_image(args.binary, args.output)

        # Compare if reference provided
        if args.compare and os.path.exists(args.compare):
            print("\nComparing with Python reference...")
            results = compare_images(fpga_data, args.compare)

            print(f"\n{'='*50}")
            print("Comparison Results:")
            print(f"{'='*50}")
            print(f"  Match:        {results['match_percent']:.2f}%")
            print(f"  Max diff:     {results['max_diff']}")
            print(f"  Mean diff:    {results['mean_diff']:.4f}")
            print(f"  Std diff:     {results['std_diff']:.4f}")
            print(f"  MSE:          {results['mse']:.4f}")
            print(f"  Pixels differ: {results['pixels_differ']:,} / {results['total_pixels']:,}")
            print(f"{'='*50}")
            print("Diff image saved to: fpga_python_diff.png")
    else:
        print(f"ERROR: Binary file not created: {args.binary}")
        sys.exit(1)


if __name__ == '__main__':
    main()
