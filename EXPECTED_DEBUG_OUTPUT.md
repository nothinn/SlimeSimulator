# Expected Debug Output After Fix

This document shows what the Verilator simulation should output after the `latched_valid` initialization fix is applied.

## Simulation Start

```
========================================================================
  FULL RTL SIMULATION WITH ACTUAL AGENT LOGIC: 100k agents
========================================================================

Configuration:
  Agents: 100
  Resolution: 320×240
  Steps: 1
  Sensory logic: Forward, Left, Right comparison
  Decay rate: 0.95 (matching Python reference)

This runs actual agent sensory processing matching Python reference.
```

## Reset and Initialization

```
[TB] Resetting RTL...
[TB] Reset complete

[TB] Initializing 100 agents...
[TB] Agents initialized in circle pointing inward

[TB] Testing trail memory interface...
[TB] Trail[0] = 0
[TB] Trail[1] = 0
[TB] Trail[2] = 0
...
[TB] Trail[9] = 0
```

## State Machine Transitions (CRITICAL SECTION)

This is where the fix makes a difference:

```
[TB] Asserting sim_start signal...
[TB] Waiting for state machine transitions...

[TB] Cycle 0: coordinator_state=0 proc_busy=0 proc_done=0 current_agent=0
[COORD] State transition (cycle=20): 0 -> 1
[TB] Cycle 1: coordinator_state=1 proc_busy=0 proc_done=0 current_agent=0
[COORD] Entering INITIALIZE state

[COORD] State transition (cycle=21): 1 -> 2
[TB] Cycle 2: coordinator_state=2 proc_busy=0 proc_done=0 current_agent=0
[COORD] Entering RUNNING state (will process agents)

[TB] Cycle 3: coordinator_state=2 proc_busy=0 proc_done=0 current_agent=0
[COORD] Starting processor for agent[0]: x=131072 y=98304 angle=0 (busy=0)

[TB] Cycle 4: coordinator_state=2 proc_busy=1 proc_done=0 current_agent=0
[TB] Cycle 5: coordinator_state=2 proc_busy=1 proc_done=0 current_agent=0
[TB] Cycle 6: coordinator_state=2 proc_busy=1 proc_done=0 current_agent=0
```

**KEY OBSERVATION:** Notice that between cycle 2 and cycle 3:
- No "Writing back agent[...]" message appears
- This confirms `latched_valid=0` at startup
- Processor starts cleanly without corruption

## Agent Processing

After ~19 cycles, the processor completes:

```
[TB] Cycle 22: coordinator_state=2 proc_busy=1 proc_done=1 current_agent=0
[COORD] Processor done for agent[0], latching outputs x=132072 y=98304 angle=300
[COORD] Advancing to agent[1]

[TB] Cycle 23: coordinator_state=2 proc_busy=0 proc_done=0 current_agent=1
[COORD] Trail write: addr=38560 (160,120) data=50 (from agent[0])
[COORD] Writing back agent[0]: x=132072 y=98304 angle=300
[COORD] Starting processor for agent[1]: x=131072 y=98304 angle=6283 (busy=0)
```

**KEY OBSERVATION:** Trail write occurs with **non-zero data** (data=50).

## Continued Processing

```
[TB] Cycle 42: coordinator_state=2 proc_busy=1 proc_done=1 current_agent=1
[COORD] Processor done for agent[1], latching outputs
[COORD] Advancing to agent[2]
[TB] Cycle 43: TRAIL_WRITE addr=... data=50 (agent[1])
[COORD] Writing back agent[1]: ...
[COORD] Starting processor for agent[2]: ...

...

[TB] Cycle 100: state=2 agent=5 busy=1 done=0 agents_processed=10
[TB] Cycle 200: state=2 agent=10 busy=1 done=0 agents_processed=20
...
[TB] Cycle 1900: state=2 agent=99 busy=1 done=0 agents_processed=199
```

## Trail Map Dump

```
[TB] Step    0: Trail (min=0 max=50 mean=0.1)
```

**KEY OBSERVATION:** `max=50` confirms non-zero trail values!

## Simulation Complete

```
[TB] Simulation complete. Total agents processed: 200

  Dumping final trail map at step 0...
[TB] Step    0: Trail (min=0 max=50 mean=0.1)


========================================================================
  SIMULATION COMPLETE
========================================================================

Results:
  Trail dumps: rtl_trail_dumps/
  Sensory logic: Fully functional
  Trail map size: 76800 bytes

Next: Run comparison with Python reference
```

## What to Look For (Verification Checklist)

### ✓ GOOD (Fix Working)
1. State transition 0→1→2 (IDLE→INITIALIZE→RUNNING) within first 25 cycles
2. "Starting processor for agent[0]" appears at cycle ~23
3. "Trail write: ... data=50" appears (non-zero data)
4. Trail dump shows `max > 0` (not all zeros)
5. `agents_processed` counter increments steadily

### ✗ BAD (Fix Not Working)
1. State stuck in IDLE (state never changes from 0)
2. No "Starting processor" messages
3. "Trail write: ... data=0" (all zero data)
4. Trail dump shows `max=0` (all zeros)
5. `agents_processed` stays at 0

## Trail Dump File Verification

```bash
# Check file exists
ls -lh rtl_trail_dumps/trail_step_00000.bin
# Expected: 230400 bytes (320*240*3 for 18-bit values)

# Check for non-zero bytes
od -An -tu1 rtl_trail_dumps/trail_step_00000.bin | tr ' ' '\n' | grep -v '^$' | grep -v '^0$' | wc -l
# Expected: > 0 (should have hundreds of non-zero bytes)

# Show first non-zero values
od -An -tu1 rtl_trail_dumps/trail_step_00000.bin | tr ' ' '\n' | grep -v '^$' | grep -v '^0$' | head -20
# Expected: Values in range 1-50
```

## Troubleshooting

If you still see all zeros after applying the fix:

1. **Verify fix was applied:**
   ```bash
   grep -n "latched_valid <= 1'b0" rtl/src/agent_coordinator.sv
   # Should show line 177 with the reset initialization
   ```

2. **Check recompilation:**
   ```bash
   rm -rf rtl/sim/obj_dir_fix
   # Rebuild from scratch
   ```

3. **Check debug output for other issues:**
   - Look for synthesis warnings about undriven signals
   - Look for X (undefined) values in simulation
   - Check if reset signal is actually asserted (rst_n=0 for at least 10 cycles)

## Summary

**Before Fix:** State machine stuck or agents corrupted → zero trail values
**After Fix:** Clean startup → agents process → non-zero trail deposits → SUCCESS
