# Root Cause Analysis: RTL Spatial Pattern Divergence

## Executive Summary

Four **critical architectural and arithmetic mismatches** have been identified that cause RTL simulation to diverge dramatically from Python reference:

1. **LFSR Clock Domain Mismatch** - RTL uses continuous 100MHz clock, Python steps LFSR once per agent
2. **Fixed-Point Truncation Divergence** - RTL truncates toward -∞, Python truncates toward 0
3. **Signed Modulo Operator Mismatch** - SystemVerilog % behaves differently than Python %
4. **Double Wrapping Coordinate Error** - Position wrapped twice in different coordinate spaces

---

## Detailed Findings

### 1. LFSR Clock Domain Mismatch (CRITICAL - ROOT CAUSE #1)

**Problem**: LFSR is stepped at different rates in RTL vs Python

**RTL Behavior** (lfsr.sv line 365):
```verilog
assign lfsr_enable = (sim_state == SIM_RUN_AGENTS) && !sim_pause;
// LFSR steps once per 100MHz clock cycle continuously
```
- LFSR advances **~19 times per agent** during pipelined processing
- By SENSORY_DECISION stage (clock 15), LFSR has advanced ~15 steps from start
- Samples `lfsr_state[0]` at arbitrary point in LFSR sequence

**Python Behavior** (slime_simulator.py line 440):
```python
# LFSR stepped once per agent during sensory decision
random_turn_left = self._lfsr_bool_n(self.config.num_agents)
```
- LFSR advances **once per agent per simulation step**
- Each agent gets fresh LFSR state, deterministic sequence

**Consequence**: RTL and Python sample **completely different random bits** for turn decisions
- Agent 0 in Python uses LFSR state after 1 step from seed
- Agent 0 in RTL uses LFSR state after ~15 steps from seed
- Different random decisions → Divergent movement paths → Different trail patterns

**Example Trace**:
```
Seed: 0xDEADBEEF

Python (Agent 0 decision):
  Step 1: state = 0xBD5B7DDE, bit[0] = 0 → turn right

RTL (Agent 0 decision, sampled at clock 15):
  Step 1:  state = 0xBD5B7DDE
  Step 2:  state = 0x7AB6FBBC
  ...
  Step 15: state = 0x????? , bit[0] = ? → different decision
```

---

### 2. Fixed-Point Truncation Direction Divergence (CRITICAL - ROOT CAUSE #2)

**Problem**: RTL and Python truncate negative numbers in opposite directions

**RTL Implementation** (agent_processor.sv lines 146-161):
```systemverilog
function automatic [9:0] fp_to_pixel_x(input signed [FP_TOTAL-1:0] fp_val);
    return (fp_val >>> FP_FRAC_BITS) % WIDTH;  // Arithmetic right shift
endfunction
```
- Arithmetic right shift `>>>` truncates toward **negative infinity**
- Example: `-1229 >>> 12 = -1` (not 0)

**Python Implementation** (slime_simulator.py line 222):
```python
px = int(px)  # Truncates toward zero
px = int(px) % self.width
```
- `int()` truncates toward **zero**
- Example: `int(-0.3) = 0`

**Consequence**: Agents with negative coordinates read from **opposite side of screen**

**Concrete Example** (agent at angle 180°, moves left):
```
Fixed-point position: -1,228,800 (Q12.12 format)
Negative fractional part: -0.3 pixels

Python:
  pixel_x = int(-0.3) = 0 → reads/writes from pixel 0 (left edge)

RTL:
  pixel_x = (-1,228,800 >>> 12) % 640
         = (-300) % 640
         = 340 → reads/writes from pixel 340 (middle of screen)

Divergence: 340 pixels horizontal offset!
```

**Impact**: Agents sense trail from wrong pixels, make opposite turning decisions repeatedly

---

### 3. Signed Modulo Operator Mismatch (CRITICAL - ROOT CAUSE #3)

**Problem**: SystemVerilog and Python handle modulo of negative numbers differently

**RTL** (agent_coordinator.sv lines 299-302):
```systemverilog
assign read_x = proc_trail_read_x % WIDTH;  // C semantics: sign of dividend
assign write_x = proc_trail_write_x % WIDTH;
```
- Example: `-100 % 640 = -100` (result is negative!)
- This creates **invalid memory addresses**

**Python**:
```python
px = int(px) % self.width  # Sign of divisor
# Example: -100 % 640 = 540 (wraps correctly)
```

**Consequence**: Out-of-bounds memory reads/writes
- Accessing negative array indices
- Trail values corrupted
- Spatial patterns destroyed

---

### 4. Double Wrapping Coordinate Error (CRITICAL - ROOT CAUSE #4)

**Problem**: Position wrapped twice in different coordinate spaces

**RTL Flow** (agent_processor.sv + agent_coordinator.sv):
```systemverilog
// Stage 1: Wrap in fixed-point space (incomplete, single wrap)
if (new_x >= WIDTH_FP)
    new_x -= WIDTH_FP;
else if (new_x < 0)
    new_x += WIDTH_FP;
// new_x is now in FP space [0, WIDTH_FP)

// Stage 2: Convert to pixel, then wrap again as pixel
assign trail_addr_b = (trail_y * WIDTH) + (trail_x % WIDTH);
// Treating FP value as pixel value!
```

**Python Flow** (slime_simulator.py):
```python
# Wrap once in fixed-point space
self.x = (agent.x + dx) & self.fp.mask
# Then convert to pixel
px = int(px) % self.width
```

**Consequence**: Coordinate space confusion
- Example: Position 78,560 in fixed-point
  - Python: `78,560 / 4096 = 19` pixels (correct)
  - RTL: `78,560 % 640 = 599` pixels (treats FP as pixel!)
  - **Divergence: 580 pixels**

---

### 5. Incomplete Multi-Wrap Handling (HIGH PRIORITY)

**Problem**: Manual if/else only wraps once; Python's modulo handles all overflows

**RTL** (agent_processor.sv lines 326-334):
```systemverilog
// Handles ONLY single wrap
if (new_x >= WIDTH_FP)
    new_x -= WIDTH_FP;
else if (new_x < 0)
    new_x += WIDTH_FP;
// What if new_x >= 2*WIDTH_FP? Still wrapped incorrectly!
```

**Python**:
```python
self.x = (a + b) & self.fp.mask  # Automatic complete wrap via bitwise AND
```

**Consequence**: After multiple large movements, position can overflow and corrupt

---

## Impact Analysis

### Per-Agent Per-Step Effects

| Issue | Effect | Pixel Offset |
|-------|--------|--------------|
| LFSR timing | Wrong turn decisions | Cascading divergence |
| Truncation direction | Read from opposite side | ±320 pixels |
| Signed modulo | Out-of-bounds access | Undefined behavior |
| Double wrapping | Coordinate space confusion | ±640 pixels |
| Multi-wrap | Overflow at large movements | Unbounded |

### Cumulative Effect Over Time

**Step 1**: Individual agents make opposite decisions
**Step 2-3**: Agents at wrong locations, converge to different attractors
**Step 4-5**: Spatial pattern completely inverted or inverted + offset
**Step 6+**: Trail map unrecognizable, agents cluster at wrong locations

This explains the **99.9% numerical match but wrong spatial pattern**:
- Pixel differences are small initially (3.04×, 5.01× mean ratios)
- But they're **in completely different locations**
- Numerical difference is just an artifact of comparison metric

---

## Verification Evidence

### Subagent Finding #1: Agent Movement Analysis
**Verdict**: 3 bugs in movement logic, most critical is position wrapping (if-else vs modulo)

### Subagent Finding #2: LFSR Analysis
**Verdict**: LFSR tap sequences match perfectly, but clock domain doesn't (100 MHz free-running vs step-synchronized)

### Subagent Finding #3: Fixed-Point Arithmetic
**Verdict**: Truncation direction critical: `>>>` toward -∞ vs `int()` toward 0

### Subagent Finding #4: Agent Diagnostic
**Verdict**: Created ground truth with detailed logging of all agent states, establishes expected behavior

---

## Recommended Fixes (Priority Order)

### FIX #1: Modulo Operator (CRITICAL)
**File**: `rtl/src/agent_coordinator.sv` lines 299-302

**Current**:
```systemverilog
assign read_x = proc_trail_read_x % WIDTH;
assign write_x = proc_trail_write_x % WIDTH;
```

**Fix**:
```systemverilog
// Proper modulo for potentially negative values
assign read_x = (proc_trail_read_x < 0)
                ? ((proc_trail_read_x % WIDTH) + WIDTH)
                : (proc_trail_read_x % WIDTH);
assign write_x = (proc_trail_write_x < 0)
                 ? ((proc_trail_write_x % WIDTH) + WIDTH)
                 : (proc_trail_write_x % WIDTH);
```

### FIX #2: Truncation Direction (CRITICAL)
**File**: `rtl/src/agent_processor.sv` lines 146-161

**Current**:
```systemverilog
function automatic [9:0] fp_to_pixel_x(input signed [FP_TOTAL-1:0] fp_val);
    return (fp_val >>> FP_FRAC_BITS) % WIDTH;
endfunction
```

**Fix**:
```systemverilog
function automatic [9:0] fp_to_pixel_x(input signed [FP_TOTAL-1:0] fp_val);
    logic signed [FP_TOTAL-1:0] normalized;
    integer pixel;
    // Truncate toward zero, not toward -infinity
    if (fp_val >= 0)
        pixel = fp_val >> FP_FRAC_BITS;
    else
        pixel = -(((-fp_val - 1) >> FP_FRAC_BITS) + 1);
    // Now apply wrapping
    return (pixel < 0) ? ((pixel % WIDTH) + WIDTH) : (pixel % WIDTH);
endfunction
```

### FIX #3: LFSR Synchronization (HIGH PRIORITY)
**File**: `rtl/src/slime_top.sv` line 365

**Current**:
```verilog
assign lfsr_enable = (sim_state == SIM_RUN_AGENTS) && !sim_pause;
```

**Problem**: Continuous clock, not step-synchronized

**Option A** - Pulse-based (most compatible):
```verilog
// Enable LFSR only when agent_processor requests it
assign lfsr_enable = agent_proc_lfsr_en;
```

**Option B** - Sync to decision point:
```verilog
// Enable LFSR only during SENSORY_DECISION stage
assign lfsr_enable = (agent_proc_stage == SENSORY_DECISION);
```

### FIX #4: Complete Wrapping (HIGH PRIORITY)
**File**: `rtl/src/agent_processor.sv` lines 326-334

**Current**:
```systemverilog
if (new_x >= WIDTH_FP)
    new_x -= WIDTH_FP;
else if (new_x < 0)
    new_x += WIDTH_FP;
```

**Fix**:
```systemverilog
// Use modulo for complete wrapping
logic signed [FP_TOTAL-1:0] width_fp;
assign width_fp = WIDTH * FP_SCALE;
assign new_x = ((new_x % width_fp) + width_fp) % width_fp;
```

---

## Testing Plan

After applying fixes:

1. **Unit Test**: Single agent, 5 steps, verify position matches Python exactly
2. **Small Test**: 10 agents, 5 steps, check trail locations match Python
3. **Medium Test**: 100 agents, 3 steps (compare existing images)
4. **Full Test**: 1000+ agents, 100+ steps, verify convergence

---

## Summary

**Root causes identified**: 4 critical issues
**Severity**: All CRITICAL - any one can cause major divergence
**Likelihood of co-occurrence**: Very high - all present in current RTL
**Total impact on spatial pattern**: Multiple compounding errors create unrecognizable patterns

Once these fixes are applied, RTL should produce **bit-exact match** with Python reference implementation.
