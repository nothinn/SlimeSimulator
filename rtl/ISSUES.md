# Known Issues & Design Gaps

## Critical Issues

### 1. Agent Processor Not Integrated ❌
**Status**: Blocking simulation
**File**: `slime_top.sv`
**Problem**:
- The `agent_processor.sv` module exists and is fully implemented (19-state state machine)
- BUT it is **not instantiated** in `slime_top.sv`
- Current `slime_top.sv` has a skeletal state machine that cycles through agents without actually processing them
- This means: **No simulation is happening**

**Impact**:
- VGA displays static/empty screen (trail memory never gets written to)
- Buttons do cycle through states but no actual computation occurs
- LEDs show state changes but no trail updates

**Required Fix**:
- Instantiate `agent_processor` module in `slime_top.sv`
- Wire agent state register to pass agent data to processor
- Connect trail memory read/write signals
- Connect LFSR outputs for random behavior
- Implement agent memory (currently missing)

**Estimated Effort**: Medium (~200 lines of integration code)

---

### 2. VGA Display Not Working ❌
**Status**: Symptom of #1 or separate hardware issue
**Observation**:
- VGA test pattern programmed but no output
- Main design also not displaying anything
- Could be either:
  a) Design issue (likely due to #1 - no content to display)
  b) Hardware issue (cable, monitor, FPGA pins)

**Next Steps**:
1. Fix #1 first - if trail memory is written, VGA should display it
2. If still no VGA output after fixing #1, then investigate hardware

---

## Missing Components

### Agent Memory
**Status**: Not implemented
- Need to store state for all NUM_AGENTS (currently 1000 - should be ~64)
- Each agent needs: x, y, angle (3 × 25-bit signed = 75 bits per agent)
- Current design has `agent_idx` but nowhere to store agent data

**Solution**:
```systemverilog
// Simple dual-port RAM for agents
typedef struct packed {
    logic signed [FP_TOTAL-1:0] x, y, angle;
} agent_t;
agent_t agent_mem [0:NUM_AGENTS-1];
```

### Agent Processor Instantiation
**Status**: Missing from slime_top
- Module exists but not instantiated
- Need to connect:
  - agent_x_in, agent_y_in, agent_angle_in (from agent_mem)
  - trail_read_addr, trail_write_addr
  - trail_read_data, trail_write_data, trail_write_en
  - trig_sin, trig_cos (from trig_lut)
  - LFSR outputs for randomization

### Diffusion Kernel
**Status**: Stub only
**File**: `slime_top.sv` SIM_DIFFUSE state
**Current Code**:
```systemverilog
SIM_DIFFUSE: begin
    // Apply diffusion and decay to trail map
    // (Simplified - would need diffusion kernel)
    sim_state <= SIM_WAIT_FRAME;
end
```

**Needed**:
- Convolution kernel for trail diffusion (8-neighbor average)
- Decay multiplier (0.95 per frame)
- Could be optimized with parallel processing or pipelined

---

## Parameter Issues

### NUM_AGENTS = 1000
**Status**: Unrealistic default
**Problem**:
- 1000 agents × 75 bits = 75,000 bits of dual-port RAM
- Plus trail memory and temporary registers
- May cause resource exhaustion

**Recommendation**: Change to 64 agents (reasonable for Basys3)
```systemverilog
parameter NUM_AGENTS = 64,  // Realistic for Basys3
```

### Clock Division
**Status**: Correct but could be optimized
- Current: Simple /4 divider for 25MHz from 100MHz
- Works fine but could use DCM/PLL for better precision if needed
- Current design acceptable for prototype

---

## Testing Strategy

Once fixes are in place:

1. **Stage 1**: Verify agent processor instantiation
   - Check synthesis doesn't fail
   - Verify no timing issues

2. **Stage 2**: Test agent memory initialization
   - BTNC starts simulation
   - LEDs should cycle through states
   - Check trail memory reads/writes via simulation

3. **Stage 3**: Test VGA output
   - Program FPGA with fixed design
   - Watch for trail patterns on display
   - Use BTNL to randomize agent positions

4. **Stage 4**: Validation
   - Compare with Python reference simulator
   - Verify agent behavior matches (sensory, decision, movement)
   - Check trail diffusion accuracy

---

## Build Status

- ✅ VGA test pattern: Builds without issues
- ✅ Main design: Builds without errors (because agent_processor is optional/unused)
- ✅ All modules individually: Testbenches pass
- ❌ Integration: Agent processor not wired up
- ❌ Simulation: No actual trail updates occurring

---

## Files to Modify

### Required Changes
1. **slime_top.sv** (~300 lines new code)
   - Add agent memory
   - Instantiate agent_processor
   - Wire signals
   - Implement diffusion kernel

2. **basys3.xdc** (minimal, if any)
   - Verify pin assignments (already correct)

### Optional Improvements
1. **agent_processor.sv**
   - Already well-designed, minimal changes needed

2. **vga_controller.sv**
   - Works correctly, no changes needed

3. **Testbenches**
   - Need integration testbench for top module

---

## Estimated Timeline

- **Agent memory + instantiation**: 2-3 hours
- **Diffusion kernel**: 1-2 hours
- **Testing & debugging**: 2-4 hours
- **Total**: ~5-9 hours of development

---

## Verification Checklist

- [ ] agent_processor instantiated in slime_top
- [ ] Agent memory properly initialized
- [ ] Trail memory reads/writes working
- [ ] State machine properly sequencing
- [ ] LEDs showing correct state progression
- [ ] VGA displaying trail patterns
- [ ] BTNC start/stop working
- [ ] BTNU/BTND speed control functional
- [ ] BTNL randomization working
- [ ] Trail shows expected slime mold behavior

---

**Last Updated**: 2025-11-24 09:45 UTC
**Priority**: 🔴 Critical - Blocks all simulation
