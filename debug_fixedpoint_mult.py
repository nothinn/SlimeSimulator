#!/usr/bin/env python3
"""Debug fixed-point multiplication discrepancy."""

import sys
sys.path.insert(0, 'rtl/sim')

from python_reference import FixedPoint

fp = FixedPoint(12, 12)

# Agent 0, angle 512 (pi radians)
# cos(pi) = -1.0 in floating point
# In fixed point at angle index 512:
# From the LUT, cos(512) should be -1.0

# Load the LUT value
from python_reference import TrigLUT
trig = TrigLUT(10, 12)

sin_512 = trig.sin(512)
cos_512 = trig.cos(512)

print(f"Trig LUT values for angle index 512:")
print(f"  sin(512): 0x{sin_512:07X}")
print(f"  cos(512): 0x{cos_512:07X}")

# Convert to signed for easier visualization
def to_signed_25bit(val):
    if val >= (1 << 24):
        return val - (1 << 25)
    return val

sin_512_signed = to_signed_25bit(sin_512)
cos_512_signed = to_signed_25bit(cos_512)

print(f"  sin(512) signed: {sin_512_signed:+7d} ({sin_512_signed/4096:+.5f})")
print(f"  cos(512) signed: {cos_512_signed:+7d} ({cos_512_signed/4096:+.5f})")

# Move speed = 1.0 = 4096 in fixed-point
move_speed = fp.to_fixed(1.0)
print(f"\nMove speed: 0x{move_speed:07X} = {move_speed} (expected 4096)")

# Now multiply cos * move_speed
# This should give us -1.0 * 1.0 = -1.0
# Which in fixed-point is -4096

# Simulate both sign-extended and unsigned versions
print(f"\n--- Multiplication: cos(512) * move_speed ---")

# Method 1: Treat as unsigned (what RTL might be doing if sign extension is wrong)
result_unsigned = fp.multiply(cos_512, move_speed)
print(f"Using unsigned LUT value:")
print(f"  0x{cos_512:07X} * 0x{move_speed:07X} = 0x{result_unsigned:07X}")
print(f"  As signed: {to_signed_25bit(result_unsigned):+7d} ({fp.from_fixed(to_signed_25bit(result_unsigned)):+.5f})")

# Method 2: Properly sign-extend the LUT value first
cos_512_fp = cos_512_signed  # Already sign-extended
result_correct = fp.multiply(cos_512_fp, move_speed)
print(f"\nUsing properly sign-extended LUT value:")
print(f"  {cos_512_fp:+7d} * {move_speed} = {to_signed_25bit(result_correct):+7d}")
print(f"  Result: {fp.from_fixed(to_signed_25bit(result_correct)):+.5f}")

# Check what the Python reference actually does
print(f"\n--- Check python_reference.py TrigLUT.cos() return value ---")
cos_512_from_trig = trig.cos(512)
print(f"trig.cos(512) = 0x{cos_512_from_trig:07X} = {cos_512_from_trig}")

# The issue: if we don't properly sign-extend when storing in fixed-point,
# we get wrong results!

# Let's compute what happens if cos_512 is treated as unsigned 25-bit
print(f"\n--- HYPOTHESIS: RTL not sign-extending LUT values ---")
print(f"If RTL treats cos(512) = 0x{cos_512:07X} as UNSIGNED:")
print(f"  Then as positive Q12.12: {cos_512 / 4096:.5f}")
print(f"  Instead of negative Q12.12: {cos_512_signed / 4096:.5f}")
print(f"\nIf multiply treats unsigned as {cos_512}:")
result_bad = fp.multiply(cos_512, move_speed)
print(f"  {cos_512} * {move_speed} >> 12 = {to_signed_25bit(result_bad):+7d}")
print(f"  Which interprets as: {result_bad / 4096:.5f}")

# The real bug: when RTL reads from LUT, does it sign-extend?
# Let's check what value causes a 2x movement error

print(f"\n--- DEBUGGING 2X MOVEMENT BUG ---")
# We observed RTL moved -2.0 instead of -1.0
# That means it applied -8192 instead of -4096
# -8192 = -2 * 4096
# So the multiplication gave -8192 instead of -4096

# If cos = -1 and speed = 1, result should be -1
# If we got -2 instead, that means either:
# 1. cos = -2 (but LUT has -1)
# 2. speed = 2 (but we set it to 1)
# 3. The multiply is doing something wrong
# 4. The result is being applied twice

print(f"If RTL move_speed was set to 2.0 instead of 1.0:")
move_speed_wrong = fp.to_fixed(2.0)
print(f"  move_speed = 0x{move_speed_wrong:07X} = {move_speed_wrong}")
result_2x = fp.multiply(cos_512_fp, move_speed_wrong)
print(f"  cos(-1.0) * 2.0 = {to_signed_25bit(result_2x):+7d}")
print(f"  = {fp.from_fixed(to_signed_25bit(result_2x)):+.5f}")

