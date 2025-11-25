# Agent Processor Integration Guide

## Current Status

The SlimeSimulator FPGA design currently has **two simulation modes**:

### 1. **Simple Pattern Mode (ACTIVE)**
- Uses LFSR to generate pseudo-random trail patterns
- Fills entire 160×120 trail memory each frame
- No agent physics simulation
- **Current bitstream uses this mode**

### 2. **Full Agent Simulation (FRAMEWORK IN PLACE)**
- Agent orchestrator module created (`rtl/src/agent_orchestrator.sv`)
- Ready for integration with full sensory/motor pipeline
- Requires enabling in `slime_top.sv`

---

## Architecture Overview

### Current Pipeline (Simple Mode)
```
LFSR → Trail Memory → VGA Controller → Display (640×480)
```

### Full Agent Pipeline (Ready to Integrate)
```
Agent Orchestrator → Agent Memory → Agent Processor
    ↓                                    ↓
Trail Memory ← [Sensory Reads] ← [Trail Reads]
    ↓
VGA Controller → Display
```

---

## Module Dependencies

### Existing Modules
- ✅ `slime_top.sv` - Top-level integration point
- ✅ `vga_controller.sv` - 640×480 @ 60Hz output
- ✅ `agent_processor.sv` - 19-stage agent pipeline
- ✅ `fixed_point_mult.sv` - Q12.12 multiplier
- ✅ `trig_lut.sv` - Sine/cosine lookup tables
- ✅ `lfsr.sv` - Maximal-length LFSR
- ✅ `debouncer.sv` - Button input debouncing

### New Modules (Framework Ready)
- ✅ `agent_orchestrator.sv` - Agent state management and orchestration

---

## Integration Steps (Future Work)

### Phase 1: Enable Agent Orchestrator (Low Complexity)
**Status**: Code written, ready to enable

1. Uncomment the `agent_orchestrator` instantiation in `slime_top.sv` (lines 361-386)
2. Switch the mux to use `agent_trail_*` signals instead of simple pattern
3. Rebuild and test with 100 agents

**Expected Result**: Agents move across screen, deposit trails based on LFSR seed

### Phase 2: Integrate Full Agent Processor (High Complexity)
**Status**: Module exists, needs orchestration layer

1. Modify `agent_orchestrator.sv` to:
   - Implement multi-stage pipelining
   - Fetch agent state from memory
   - Call `agent_processor.sv` for each agent
   - Handle trail memory arbitration

2. Implement agent memory:
   - Dual-port BRAM for position (x, y) and angle
   - Support 1000 agents × 75 bits state

3. Integrate sensory pipeline:
   - Trail map reads at sensor positions
   - Comparison logic (forward vs left vs right)
   - Sensory decision (turn direction)

4. Implement trail deposition:
   - Write updated trail intensity at agent position
   - Apply decay/diffusion kernel

**Expected Result**: Full slime mold physics simulation with organic trail patterns

### Phase 3: Optimize for 1000 Agents
**Status**: Design considerations ready

1. Implement pipelined architecture:
   - Multiple agents in flight simultaneously
   - Reduces cycles per frame
   - Increases trail activity

2. BRAM optimization:
   - Currently: 4 RAMB36E1 blocks for trail (76.8 KB)
   - Available: Can use ~90 blocks total
   - Room for agent memory

3. Processing bandwidth:
   - Current: ~19 MHz for 1000 agents @ 60 FPS
   - Need: Pipelined execution to achieve target rate

---

## How to Enable Agent Orchestrator

### Quick Start (100 Agents)

1. **Edit `rtl/src/slime_top.sv`**:
```verilog
// Remove the comment markers /* and */ around lines 361-386
agent_orchestrator #(
    .NUM_AGENTS(100),
    // ... rest of instantiation
) u_orchestrator (
    // ... port connections
);
```

2. **Update trail memory mux** (around line 355):
```verilog
// Change from simple pattern to orchestrator
assign trail_addr_b = agent_trail_addr;  // Was: from SIM_RUN_AGENTS
assign trail_data_b_in = agent_trail_data;
assign trail_we_b = agent_trail_we;
```

3. **Rebuild**:
```bash
source ~/2025.2/Vivado/.settings64-Vivado.sh
python3 scripts/vivado_build.py main --verbose --clean
```

4. **Program FPGA**:
```bash
vivado -mode batch -source rtl/program_fpga.tcl \
  -tclargs rtl/vivado_project/slime_simulator.runs/impl_1/slime_top.bit
```

---

## Technical Details

### Agent State (per agent)
```
Position X:  25-bit signed fixed-point (Q12.12)
Position Y:  25-bit signed fixed-point (Q12.12)
Angle:       25-bit signed fixed-point (Q12.12)
Total:       75 bits per agent
```

### Trail Map
```
Resolution: 160×120 pixels
Memory:     19,200 × 8-bit = 152 KB
VGA Scale:  4× (640×480 output)
```

### LFSR
```
Width:       32 bits
Type:        Maximal-length LFSR
Purpose:     Random number generation for agent behavior
```

### Fixed-Point Arithmetic
```
Format:      Q12.12 (12 int bits, 12 frac bits, 1 sign)
Range:       -2048.0 to +2047.9998
Precision:   1/4096 ≈ 0.000244
```

---

## Performance Characteristics

### Current (Simple Pattern Mode)
- **Memory Writes**: 19,200 per frame (entire trail map)
- **Refresh Rate**: 60 FPS @ 100 MHz clock
- **Pipeline Depth**: Single pass through memory

### Expected (Full Agent Mode)
- **Memory Writes**: ~1000 per frame (agents deposit trails)
- **Refresh Rate**: 60 FPS (target)
- **Pipeline Depth**: 19-stage agent processor × agent count

### Throughput
- **Agent Processing**: 1 agent every ~19 clock cycles @ 100 MHz
- **Maximum Agents**: ~5 million/sec (limited by trail memory bandwidth)
- **1000 Agents @ 60 FPS**: Requires ~19 MHz = achievable

---

## Testing Strategy

### Phase 1: Orchestrator Verification
- [ ] Enable 100 agents with orchestrator
- [ ] Verify agents initialize across screen
- [ ] Confirm trails appear in expected positions
- [ ] Test BTNL (randomize) changes patterns

### Phase 2: Processor Integration
- [ ] Single agent through full processor
- [ ] Verify sensory readings work
- [ ] Check agent movement logic
- [ ] Validate trail deposition

### Phase 3: Multi-Agent
- [ ] Increase to 500 agents
- [ ] Monitor for timing violations
- [ ] Verify frame rate remains 60 FPS
- [ ] Check trail patterns are organic

### Phase 4: Full Scale
- [ ] Scale to 1000 agents
- [ ] Profile BRAM and LUT usage
- [ ] Optimize if needed
- [ ] Document final performance

---

## Known Limitations

1. **Trail Decay**: Not currently implemented
   - Trails accumulate indefinitely
   - Future: Add diffusion kernel for blur effect

2. **Memory Arbitration**: Simplified
   - VGA reads during blanking only
   - Agents write during active time
   - No pipelining yet

3. **Agent Count**: Flexible but limited
   - Currently designed for 100-1000 agents
   - Can scale higher with pipelining

4. **Fixed Sensor Parameters**: Hardcoded
   - Sensor distance: 9.0 pixels
   - Sensor angle: 0.5 radians (~30°)
   - Could add dynamic adjustment via buttons

---

## Resources Used

### Current (Simple Pattern)
- **LUTs**: ~570 (2.7%)
- **FFs**: ~210 (0.5%)
- **BRAM**: 4 blocks (8%)
- **DSP**: 0

### Projected (Full Agent + 1000 agents)
- **LUTs**: ~2,500 (12%)
- **FFs**: ~3,000 (7%)
- **BRAM**: 30-40 blocks (60%)
- **DSP**: 4 (4%)

**Basys3 Capacity**: 20,800 LUTs, 41,600 FFs, 100 BRAM blocks
**Conclusion**: Design fits comfortably with room for optimization

---

## References

### Key Files
- `rtl/src/slime_top.sv` - Main integration point
- `rtl/src/agent_orchestrator.sv` - Agent management
- `rtl/src/agent_processor.sv` - Agent physics
- `rtl/sim/python_reference.py` - Bit-exact Python model

### Documentation
- `CLAUDE.md` - Project overview
- `rtl/QUICKSTART_DEBUG.md` - Vivado debugging guide

### Related
- Sebastian Lague Slime Mold: https://www.youtube.com/watch?v=X-iSQQgOd1A
- Academic Paper: https://uwe-repository.worktribe.com/output/980579
