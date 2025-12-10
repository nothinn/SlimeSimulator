#!/usr/bin/env python3
"""
Compare Python vs RTL movement for Agent 0 step-by-step.
"""

import json
import sys

# Read RTL dumps
with open('rtl/sim/rtl_agent_dumps/agent_state_step_00000.json') as f:
    rtl_step0 = json.load(f)

with open('rtl/sim/rtl_agent_dumps/agent_state_step_00001.json') as f:
    rtl_step1 = json.load(f)

# Get Agent 0 from RTL
rtl_agent0_step0 = rtl_step0['agents'][0]
rtl_agent0_step1 = rtl_step1['agents'][0]

print("=" * 80)
print("RTL AGENT 0 MOVEMENT")
print("=" * 80)

print(f"\nStep 0 (initialization):")
print(f"  x_fp    = {rtl_agent0_step0['x_fp']:7d} ({rtl_agent0_step0['x_px']:10.6f} px)")
print(f"  y_fp    = {rtl_agent0_step0['y_fp']:7d} ({rtl_agent0_step0['y_px']:10.6f} px)")
print(f"  angle_fp= {rtl_agent0_step0['angle_fp']:5d} ({rtl_agent0_step0['angle_deg']:10.6f}°)")

print(f"\nStep 1 (after movement):")
print(f"  x_fp    = {rtl_agent0_step1['x_fp']:7d} ({rtl_agent0_step1['x_px']:10.6f} px)")
print(f"  y_fp    = {rtl_agent0_step1['y_fp']:7d} ({rtl_agent0_step1['y_px']:10.6f} px)")
print(f"  angle_fp= {rtl_agent0_step1['angle_fp']:5d} ({rtl_agent0_step1['angle_deg']:10.6f}°)")

dx_rtl = rtl_agent0_step1['x_fp'] - rtl_agent0_step0['x_fp']
dy_rtl = rtl_agent0_step1['y_fp'] - rtl_agent0_step0['y_fp']

print(f"\nRTL Movement:")
print(f"  Δx = {dx_rtl:7d} ({dx_rtl/4096:10.6f} px)")
print(f"  Δy = {dy_rtl:7d} ({dy_rtl/4096:10.6f} px)")

# Now compute Python expected movement
from slime_simulator import FixedPoint, TrigLUT

print("\n" + "=" * 80)
print("PYTHON EXPECTED MOVEMENT")
print("=" * 80)

fp = FixedPoint(12, 12)
trig = TrigLUT(fp, table_bits=10)

# Agent 0 initial state
x_fp = rtl_agent0_step0['x_fp']
y_fp = rtl_agent0_step0['y_fp']
angle_fp = rtl_agent0_step0['angle_fp']

print(f"\nInitial state (same as RTL):")
print(f"  x_fp    = {x_fp:7d}")
print(f"  y_fp    = {y_fp:7d}")
print(f"  angle_fp= {angle_fp:5d}")

# Convert angle to index
angle_idx = int((angle_fp * 1024) / 25737)
print(f"\nAngle to index:")
print(f"  angle_idx = {angle_idx}")

# Lookup trig
cos_val = trig.cos(angle_idx)
sin_val = trig.sin(angle_idx)

print(f"\nTrig lookup (unsigned 2's complement):")
print(f"  cos[{angle_idx}] = {cos_val} (0x{cos_val:07x})")
print(f"  sin[{angle_idx}] = {sin_val} (0x{sin_val:07x})")

# Convert to signed
def to_signed_25bit(val):
    if val >= (1 << 24):
        return val - (1 << 25)
    return val

cos_signed = to_signed_25bit(cos_val)
sin_signed = to_signed_25bit(sin_val)

print(f"\nConverted to signed:")
print(f"  cos = {cos_signed:7d} ({cos_signed/4096:10.6f})")
print(f"  sin = {sin_signed:7d} ({sin_signed/4096:10.6f})")

# Multiply by move_speed (1.0 = 4096)
move_speed = 4096

dx_py = fp.multiply(cos_val, move_speed)
dy_py = fp.multiply(sin_val, move_speed)

print(f"\nMultiply by move_speed ({move_speed}):")
print(f"  dx = {dx_py:7d} ({dx_py/4096:10.6f} px)")
print(f"  dy = {dy_py:7d} ({dy_py/4096:10.6f} px)")

# New position
new_x_py = x_fp + dx_py
new_y_py = y_fp + dy_py

print(f"\nNew position:")
print(f"  new_x = {new_x_py:7d} ({new_x_py/4096:10.6f} px)")
print(f"  new_y = {new_y_py:7d} ({new_y_py/4096:10.6f} px)")

print("\n" + "=" * 80)
print("COMPARISON")
print("=" * 80)

print(f"\nRTL    Δx = {dx_rtl:7d} ({dx_rtl/4096:10.6f} px)")
print(f"Python Δx = {dx_py:7d} ({dx_py/4096:10.6f} px)")
print(f"Difference = {abs(dx_rtl - dx_py):7d} ({'MATCH' if dx_rtl == dx_py else 'MISMATCH'})")

print(f"\nRTL    Δy = {dy_rtl:7d} ({dy_rtl/4096:10.6f} px)")
print(f"Python Δy = {dy_py:7d} ({dy_py/4096:10.6f} px)")
print(f"Difference = {abs(dy_rtl - dy_py):7d} ({'MATCH' if dy_rtl == dy_py else 'MISMATCH'})")

print(f"\nRTL    new_x = {rtl_agent0_step1['x_fp']:7d}")
print(f"Python new_x = {new_x_py:7d}")
print(f"Difference    = {abs(rtl_agent0_step1['x_fp'] - new_x_py):7d}")

print(f"\nRTL    new_y = {rtl_agent0_step1['y_fp']:7d}")
print(f"Python new_y = {new_y_py:7d}")
print(f"Difference    = {abs(rtl_agent0_step1['y_fp'] - new_y_py):7d}")

print("=" * 80)

if dx_rtl == dx_py and dy_rtl == dy_py:
    print("✅ BIT-EXACT MATCH")
    sys.exit(0)
else:
    print("❌ MISMATCH DETECTED")
    sys.exit(1)
