# Slime Simulator RTL - Debug Report

## Executive Summary

**Root Cause of Black Screen**: The main `slime_top.sv` design has two critical issues:

1. **Missing write enable signal** (FIXED): `trail_we_b` was never assigned to 1
2. **Missing agent processor** (PENDING): The `agent_processor` module is not instantiated

---

## Issue 1: Missing Trail Memory Write Enable

### Problem
- File: `src/slime_top.sv`
- Signal: `trail_we_b` (line 182)
- Status: **FIXED** ✅

### Root Cause
The signal was declared but never assigned, so all memory write attempts were blocked:

```systemverilog
// Line 182: Declared but not assigned
logic trail_we_b;

// Line 194-196: Used in memory write, but never set to 1
always_ff @(posedge clk_100mhz) begin
    if (trail_we_b) begin  // Always false!
        trail_mem[trail_addr_b] <= trail_data_b_in;
    end
end
```

### Solution Applied
Added assignment at line 318:

```systemverilog
// Trail memory write enable during agent processing
assign trail_we_b = (sim_state == SIM_RUN_AGENTS) && !sim_pause;
```

This enables writes only when:
- Simulation state is SIM_RUN_AGENTS (processing agents)
- Simulation is not paused (SW[0] switch not activated)

---

## Issue 2: Missing Agent Processor Instantiation

### Problem
- File: `src/slime_top.sv` (main design)
- Component: `agent_processor` module exists but is NOT instantiated
- Status: **PENDING** ⚠️

### Evidence
```bash
$ grep -r "agent_processor" src/ --include="*.sv"
src/agent_processor.sv:module agent_processor #(
src/agent_sim_tb.sv:    agent_processor #(  ← Only in testbench!
```

The `agent_processor` module is only used in `agent_sim_tb.sv` (testbench), NOT in `slime_top.sv` (main FPGA design).

### Current Workaround
The simulation state machine has a placeholder in `SIM_RUN_AGENTS` state (lines 262-279):

```systemverilog
SIM_RUN_AGENTS: begin
    if (!sim_pause) begin
        // Simple pattern: write LFSR value to trail memory at agent index
        trail_addr_b <= agent_idx % (WIDTH * HEIGHT);
        trail_data_b_in <= {agent_idx[7:0]};  // Pattern value
        // ...
    end
end
```

This writes simple index-based values to demonstrate memory is working, but does NOT implement the actual slime mold behavior.

### What Agent Processor Does
The `agent_processor.sv` implements a 19-state pipeline that performs per-agent:

1. **Sensory stage**:
   - Reads trail intensity in 3 directions (forward, left, right)
   - Uses trig lookup table to compute sensor positions
   - Uses fixed-point multiplier for distance calculations

2. **Decision stage**:
   - Compares 3 sensory inputs
   - Updates agent angle based on trail gradients
   - Uses LFSR for random turn direction

3. **Motor stage**:
   - Computes new position using trig lookup table
   - Applies movement speed
   - Deposits trail at new location

### Why It Matters
Without agent_processor, the RTL cannot:
- Track agent positions (1000 agents in fixed-point coordinates)
- Read trail values and make steering decisions
- Generate emergent slime-like behavior patterns

---

## Expected Behavior vs. Actual

### Expected Trail Patterns (from Python Reference)

Generated reference trail maps for 160×120 resolution (matching RTL):

| Simulation Steps | Non-Zero Pixels | Trail Sum | Max Intensity |
|------------------|-----------------|-----------|----------------|
| 1 step           | 22 (0.1%)       | 279       | 26             |
| 5 steps          | 95 (0.5%)       | 1,217     | 26             |
| 10 steps         | 228 (1.2%)      | 2,902     | 26             |

**Key characteristic**: With 1000 agents all starting at center, they spread outward and leave observable trails. After 10 steps, about 1.2% of the 160×120 memory has been marked with trail values between 1-26.

### Actual Behavior (Current RTL)

**Before fix**: Black screen (no writes happening)

**After fix**: Will show simple sequential pattern:
- Pixels 0-999 will be written with values 0x00-0xFF (agent index)
- Pattern repeats every 1000 pixels
- Not emergent behavior, just a test pattern

---

## Debugging Framework

### Reference Data Generated

Three reference trail maps have been created for easy testing:

1. `reference_trail_160x120_1step.bin` (19,200 bytes)
   - Single simulation step
   - 22 pixels modified
   - Good for unit testing

2. `reference_trail_160x120_5steps.bin` (19,200 bytes)
   - 5 simulation steps
   - 95 pixels modified
   - Medium complexity test

3. `reference_trail_160x120_10steps.bin` (19,200 bytes)
   - 10 simulation steps
   - 228 pixels modified
   - More substantial trail pattern

### Analysis Tool

Created `analyze_trails.py` for comparison:

```bash
# Analyze single trail
python3 analyze_trails.py reference_trail_160x120_1step.bin

# Compare two trails
python3 analyze_trails.py reference_trail_160x120_1step.bin rtl_captured_trail.bin
```

This shows:
- Histogram of intensity values
- Matching percentage
- Max/mean/RMS differences
- Statistics on trail distribution

---

## Next Steps

### Immediate (Will enable basic functionality)
1. **Rebuild with trail_we_b fix** ✅ Code already edited
2. **Test pattern generator output** - Should see sequential pattern on screen
3. **Verify pattern writes to memory** - Can capture via Vivado memory viewer

### Medium Term (Required for actual simulation)
1. **Integrate agent_processor module**
   - Connect it in `SIM_RUN_AGENTS` state
   - Manage pipelined data flow
   - Handle trail memory contention

2. **Implement agent state storage**
   - Need memory for 1000 agents (3 words each: x, y, angle)
   - Coordinate reading/writing with agent_processor

3. **Add diffusion/decay logic**
   - Implement 3×3 box blur
   - Apply decay_rate (0.95x each frame)

### Long Term (Validation)
1. **Compare RTL vs. Python reference**
   - Use generated .bin files
   - Create cocotb testbench with memory extraction
   - Validate trail maps match after same steps

2. **Performance optimization**
   - Current design processes one agent per cycle (1000 cycles per frame)
   - Could parallelize multiple agents if needed

---

## File Status

### Modified
- ✅ `src/slime_top.sv` - Added `trail_we_b` assignment (line 318)

### Needs Attention
- 🔴 `src/slime_top.sv` - Missing `agent_processor` instantiation
- 🔴 `src/slime_top.sv` - Missing agent memory (1000 agents)
- 🔴 `src/slime_top.sv` - Missing diffusion/decay implementation

### Reference Materials Created
- ✅ `reference_trail_160x120_1step.bin` - Python reference data
- ✅ `reference_trail_160x120_5steps.bin` - Python reference data
- ✅ `reference_trail_160x120_10steps.bin` - Python reference data
- ✅ `reference_state_160x120_10steps.txt` - Agent positions after 10 steps
- ✅ `analyze_trails.py` - Debug tool for trail comparison
- ✅ `DEBUG_REPORT.md` - This file

---

## Commands for Testing

Build with fix:
```bash
cd rtl
vivado -mode batch -source build_vivado.tcl
```

Analyze reference:
```bash
source ../venv/bin/activate
python3 analyze_trails.py reference_trail_160x120_1step.bin
```

Program FPGA:
```bash
vivado -mode batch -source program_main.tcl
```

Once agent_processor is integrated, compare RTL output against reference using captured memory dumps.

