#!/usr/bin/env python3
"""Generate trig lookup table hex files for RTL simulation."""

import math
import os

def generate_trig_tables(table_bits=10, frac_bits=12, output_dir='.'):
    """Generate sin and cos hex files."""
    table_size = 1 << table_bits
    scale = 1 << frac_bits

    sin_file = os.path.join(output_dir, 'sin_lut.hex')
    cos_file = os.path.join(output_dir, 'cos_lut.hex')

    with open(sin_file, 'w') as sf, open(cos_file, 'w') as cf:
        for i in range(table_size):
            angle = 2.0 * math.pi * i / table_size
            sin_val = int(round(math.sin(angle) * scale))
            cos_val = int(round(math.cos(angle) * scale))

            # Handle negative values (two's complement for 25-bit)
            if sin_val < 0:
                sin_val = (1 << 25) + sin_val
            if cos_val < 0:
                cos_val = (1 << 25) + cos_val

            sf.write(f'{sin_val:07X}\n')
            cf.write(f'{cos_val:07X}\n')

    print(f"Generated {sin_file} and {cos_file} with {table_size} entries")

if __name__ == '__main__':
    import sys
    output_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    generate_trig_tables(output_dir=output_dir)
