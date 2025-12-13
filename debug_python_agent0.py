#!/usr/bin/env python3
"""
Debug Python simulator Agent 0 movement step-by-step.
"""

from slime_simulator import SlimeSimulatorReference, FixedPoint, TrigLUT

# Create simulator with 10 agents
sim = SlimeSimulatorReference(num_agents=10, width=320, height=240)

# Initialize agents in center (available method)
sim.init_agents_center()

print("=" * 80)
print("PYTHON AGENT 0 DETAILED DEBUG")
print("=" * 80)

# Get Agent 0 initial state
agent = sim.agents[0]
print(f"\nInitial state (Step 0):")
print(f"  agent.x      = {agent.x:7d} ({agent.x/4096:10.6f} px)")
print(f"  agent.y      = {agent.y:7d} ({agent.y/4096:10.6f} px)")
print(f"  agent.angle  = {agent.angle:5d} ({agent.angle * 360.0 / 1024:10.6f}°)")

# Manually trace through the motor stage for Agent 0
print("\n" + "=" * 80)
print("MOTOR STAGE TRACE")
print("=" * 80)

# Step 1: Convert angle to index
angle_idx = agent.angle & 0x3FF  # 10-bit mask
print(f"\n1. Angle to index:")
print(f"   agent.angle = {agent.angle} (0x{agent.angle:03x})")
print(f"   angle_idx   = {angle_idx} (after 10-bit mask)")

# Step 2: Trig lookup
sin_val = sim.trig.sin(angle_idx)
cos_val = sim.trig.cos(angle_idx)
print(f"\n2. Trig lookup:")
print(f"   sin[{angle_idx}] = {sin_val:10d} (0x{sin_val:07x})")
print(f"   cos[{angle_idx}] = {cos_val:10d} (0x{cos_val:07x})")

# Convert to signed for display
def to_signed(val):
    if val >= (1 << 24):
        return val - (1 << 25)
    return val

sin_signed = to_signed(sin_val)
cos_signed = to_signed(cos_val)
print(f"   sin signed  = {sin_signed:10d} ({sin_signed/4096:10.6f})")
print(f"   cos signed  = {cos_signed:10d} ({cos_signed/4096:10.6f})")

# Step 3: Multiply by move_speed
print(f"\n3. Multiply by move_speed:")
print(f"   move_speed  = {sim.move_speed:10d} ({sim.move_speed/4096:10.6f})")

dx = sim.fp.multiply(cos_val, sim.move_speed)
dy = sim.fp.multiply(sin_val, sim.move_speed)

print(f"   dx = cos * move_speed = {dx:10d} ({dx/4096:10.6f})")
print(f"   dy = sin * move_speed = {dy:10d} ({dy/4096:10.6f})")

# Step 4: Add to position
print(f"\n4. Add to current position:")
print(f"   old x = {agent.x:10d}")
print(f"   dx    = {dx:10d}")

new_x = (agent.x + dx) & sim.fp.mask
new_y = (agent.y + dy) & sim.fp.mask

print(f"   new_x = {new_x:10d} ({new_x/4096:10.6f} px)")

print(f"\n   old y = {agent.y:10d}")
print(f"   dy    = {dy:10d}")
print(f"   new_y = {new_y:10d} ({new_y/4096:10.6f} px)")

# Step 5: Get pixel coordinates
px = int(sim.fp.from_fixed(new_x)) % sim.width
py = int(sim.fp.from_fixed(new_y)) % sim.height

print(f"\n5. Extract pixel coordinates:")
print(f"   px = int({new_x/4096:.6f}) % {sim.width} = {px}")
print(f"   py = int({new_y/4096:.6f}) % {sim.height} = {py}")

# Now run the actual step
print("\n" + "=" * 80)
print("RUNNING ACTUAL STEP")
print("=" * 80)

sim.step()

print(f"\nAfter step():")
print(f"  agent.x = {sim.agents[0].x:7d} ({sim.agents[0].x/4096:10.6f} px)")
print(f"  agent.y = {sim.agents[0].y:7d} ({sim.agents[0].y/4096:10.6f} px)")

# Compare with expected
print("\n" + "=" * 80)
print("COMPARISON")
print("=" * 80)

print(f"\nExpected new_x = {new_x:7d}")
print(f"Actual   new_x = {sim.agents[0].x:7d}")
print(f"Match: {'YES' if new_x == sim.agents[0].x else 'NO'}")

print(f"\nExpected new_y = {new_y:7d}")
print(f"Actual   new_y = {sim.agents[0].y:7d}")
print(f"Match: {'YES' if new_y == sim.agents[0].y else 'NO'}")

print(f"\nExpected dx = {dx:7d} ({dx/4096:10.6f} px)")
print(f"Actual   dx = {sim.agents[0].x - 1048576:7d} ({(sim.agents[0].x - 1048576)/4096:10.6f} px)")

print(f"\nExpected dy = {dy:7d} ({dy/4096:10.6f} px)")
print(f"Actual   dy = {sim.agents[0].y - 491520:7d} ({(sim.agents[0].y - 491520)/4096:10.6f} px)")

# Final check against RTL
print("\n" + "=" * 80)
print("RTL COMPARISON")
print("=" * 80)

rtl_dx = -4096
rtl_dy = 25

print(f"\nRTL dx = {rtl_dx:7d} ({rtl_dx/4096:10.6f} px)")
print(f"Py  dx = {sim.agents[0].x - 1048576:7d} ({(sim.agents[0].x - 1048576)/4096:10.6f} px)")

print(f"\nRTL dy = {rtl_dy:7d} ({rtl_dy/4096:10.6f} px)")
print(f"Py  dy = {sim.agents[0].y - 491520:7d} ({(sim.agents[0].y - 491520)/4096:10.6f} px)")

if (sim.agents[0].x - 1048576) == rtl_dx and (sim.agents[0].y - 491520) == rtl_dy:
    print("\n✅ BIT-EXACT MATCH WITH RTL!")
else:
    print("\n❌ MISMATCH WITH RTL")

print("=" * 80)
