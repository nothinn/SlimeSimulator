# RTL vs Python Simulation Divergence - Debug Findings & Plan

## Executive Summary

The RTL simulation produces trail values ~400x lower than Python. Root cause: **The orchestrator is not actually simulating agents** - it's a test pattern stub that doesn't integrate the agent_processor module.

## Root Causes Identified

### 1. ✅ FIXED: Trail Accumulation Was Overwriting Instead of Accumulating
**File:** `rtl/src/slime_top.sv` lines 197-202

**Problem:** Trail memory writes overwrote values instead of accumulating
```systemverilog
// BEFORE (WRONG)
trail_mem[trail_addr_b] <= trail_data_b_in;  // Overwrites!

// AFTER (CORRECT)
if (trail_mem[trail_addr_b] + trail_data_b_in > 18'h3FFFF)
    trail_mem[trail_addr_b] <= 18'h3FFFF;
else
    trail_mem[trail_addr_b] <= trail_mem[trail_addr_b] + trail_data_b_in;
```

**Status:** ✅ Fixed in both slime_top.sv and agent_orchestrator.sv

### 2. ✅ FIXED: Fixed-Point Scaling Was Zeroing Out Deposits
**File:** `rtl/src/agent_orchestrator.sv` line 91

**Problem:** deposit_amount (25-bit Q12.12 = 20480) was truncated to [7:0] = 0
```systemverilog
// BEFORE (WRONG)
assign trail_data_b_in = trail_data_counter;  // Just a counter!

// AFTER (CORRECT)
logic [7:0] deposit_amount_scaled;
assign deposit_amount_scaled = deposit_amount[19:12];  // Shift >> 12 bits
assign trail_data_b_in = deposit_amount_scaled;  // Now uses actual deposit value
```

**Status:** ✅ Fixed by using deposit_amount[19:12] to extract integer portion

### 3. ❌ CRITICAL: Agent Orchestrator Is a Test Pattern, Not a Simulation

**File:** `rtl/src/agent_orchestrator.sv`

**Problem:** The orchestrator completely ignores agent state. It:
- Doesn't maintain agent positions or angles
- Doesn't read trail values at sensor positions
- Doesn't make sensory-based decisions
- Just fills memory sequentially (0 to WIDTH×HEIGHT)
- Ignores sensor_angle, sensor_distance, turn_speed, move_speed inputs

**Evidence from code:**
```systemverilog
// Just increments addresses and writes constant values
if (trail_addr_counter < (WIDTH * HEIGHT - 1))
    trail_addr_counter <= trail_addr_counter + 1'b1;
```

**What it should do (from Python):**
1. Maintain 1000 agent positions (x, y, angle)
2. Calculate F/L/R sensor positions
3. Read trail at those positions
4. Compare sensory values to decide new angle
5. Update position based on angle and move_speed
6. Deposit trail at new position

### 4. ❌ CRITICAL: agent_processor Module Exists but Never Integrated

**File:** `rtl/src/agent_processor.sv` (350 LOC, full 19-stage pipeline)

**Status:** ✅ Module is complete with 19-stage pipelined processing but ❌ never instantiated in top-level simulation

The agent_processor implements the full sensory-motor cycle:
- Stages 1-3: Forward sensor calculation (trig lookup)
- Stages 4-5: Forward trail read
- Stages 6-8: Left sensor calculation
- Stages 9-10: Left trail read
- Stages 11-13: Right sensor calculation
- Stages 14-15: Right trail read
- Stage 16: Decision logic (compare F/L/R)
- Stage 17: Angle update
- Stage 18: Position calculation
- Stage 19: Agent write + trail deposit

### 5. ❌ Trail Decay Not Implemented

**Status:** Decay (0.95x per step) is defined as a parameter but never applied

The Python simulation applies decay in the step() function but RTL has no mechanism for it. This accounts for additional ~170x reduction over 100 steps.

## Performance Comparison

| Metric | Python | RTL (Current) | Ratio |
|--------|--------|---------------|-------|
| Max trail value @ step 99 | 1,044,480 | 1,351 | 773x |
| Mean trail value @ step 99 | 4,148 | 12.5 | 331x |
| Simulation Type | Full agent + physics | Test pattern only | N/A |

## Implementation Plan

### Phase 1: Complete Current Fixes (In Progress)
- ✅ Trail accumulation (saturating add)
- ✅ Deposit amount fixed-point scaling
- ⏳ Verify fixes work correctly

### Phase 2: Integrate Agent Processor into Simulation Flow
This requires significant architectural changes:

1. **Agent State Memory:** Create RAM blocks to store 1000 × {position(50-bit), angle(25-bit)} = ~10KB
2. **Agent Index Counter:** Cycle through agents 0-999 each simulation cycle
3. **Pipeline Orchestration:** 
   - Feed agent N to agent_processor at cycle N
   - Receive completed agent from pipeline (19 cycles later)
   - Write updated position and trail back to memory
   - Move to next agent
4. **Trail Update Pipeline:**
   - Connect processor output trail_write_data to the trail memory accumulation logic
5. **LFSR Integration:** Pass LFSR state to agent_processor for random turns

### Phase 3: Implement Trail Decay
1. **Add decay state machine** to simulation controller
2. **Process trail map** after agent updates: `trail[x,y] = trail[x,y] × 0.95`
3. **Optional:** Implement diffusion kernel for blurring effect

### Phase 4: Validation & Testing
1. Compare RTL outputs with Python frame-by-frame
2. Verify agent positions stay within bounds
3. Verify trail accumulation patterns match Python
4. Test edge cases (agents at boundaries, sensor distance calculations)

## Why This Is Complex

1. **Pipelined Latency:** agent_processor takes 19 cycles per agent. With 1000 agents, this is 19,000 cycles per simulation step.
2. **Memory Bottleneck:** Need simultaneous read/write access:
   - Trail map read (F/L/R sensor positions)
   - Trail map write (current position)
   - Agent state read/write (1000 agents)
3. **Timing Constraints:** Must synchronize multiple clocks (100MHz simulation, 25MHz VGA)
4. **Fixed-Point Precision:** All arithmetic must match Python's Q12.12 format exactly

## Files That Need Modification

### High Priority
- `rtl/src/slime_top.sv` - Add agent state RAM, orchestration logic
- `rtl/src/agent_orchestrator.sv` - Replace stub with real implementation OR
- Create new `rtl/src/agent_coordinator.sv` - Proper pipeline orchestration

### Medium Priority
- `rtl/sim/slime_verilator_full_tb.cpp` - Update testbench for new trail format
- `rtl/src/agent_processor.sv` - May need minor fixes (verify against Python)

### Low Priority
- `rtl/src/vga_controller.sv` - Trail normalization for display

## Quick Workaround (Not Recommended)

For immediate testing, could modify agent_processor to run continuously in parallel:
1. Make agent_processor stateless (input agent index + state)
2. Run 100 copies in parallel for 100 agents per cycle
3. Use multiplexing to feed/read from pipeline
4. Trade area for speed (but Basys3 might not have enough LUTs)

## Next Steps

**Option A (Recommended):** Implement full agent processor integration (1-2 days of work)
- Will match Python exactly
- Required for any agent simulation at scale
- Enables full behavioral validation

**Option B (Quick Patch):** Keep test pattern but tune constants
- Won't match Python behavior
- Useful for testing trail rendering and VGA output
- Not suitable for algorithm validation

## Reference Implementations

- **Python Reference:** `slime_simulator.py` - Full behavioral implementation
- **Working Agent Processor:** `rtl/src/agent_processor.sv` - 19-stage pipeline
- **Test Comparison Data:** Dumps in `rtl/sim/rtl_trail_dumps/` - Can be analyzed frame-by-frame

