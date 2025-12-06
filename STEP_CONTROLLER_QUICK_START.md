# Step Controller - Quick Start Guide

## What Is It?

A synchronous stepping interface for the RTL simulator that processes **one simulation step per pulse** with guaranteed stable outputs.

## Why Use It?

✅ **Eliminates timing issues** - No race conditions between simulation and readout
✅ **Stable outputs** - Can safely read agent states when `step_ready=1`
✅ **Deterministic** - Each step completes before accepting next step
✅ **Debug-friendly** - Step through simulation one step at a time
✅ **Precise verification** - Exact matching between Python and RTL possible

## Quick Test

```bash
cd rtl/sim
source ../../.venv/bin/activate
make test_step_control
```

Expected output:
```
test_step_controller_movement ✅ PASSED
```

## How It Works

### Signal Protocol

```
step_request: pulse this signal to start one step
step_busy:    1 while processing, 0 when idle
step_ready:   1 when outputs stable and safe to read
step_count:   number of completed steps
```

### Timing Diagram

```
step_request:  _____╱‾‾‾‾╲______________╱‾‾‾‾╲___
step_busy:     _____╱‾‾‾‾‾‾‾‾‾‾‾‾‾╲____╱‾‾‾‾‾╲__
step_ready:    ‾‾‾╱‾╲__╱‾‾‾‾╲____╱‾‾‾‾‾╲__╱‾‾‾╲_
               idle  start  process  stable  done
```

## Python Example

```python
import cocotb
from step_test import StepTester

@cocotb.test()
async def my_test(dut):
    # Create helper
    tester = StepTester(dut, width=320, height=240, num_agents=10)

    # Initialize
    await tester.reset()
    await tester.set_parameters(move_speed=1.0, sensor_distance=9.0)

    # Setup agents
    agents = {
        0: (160.0, 120.0, 0.0),      # x_px, y_px, angle_rad
        1: (161.0, 120.0, 0.0),
        # ... more agents
    }
    await tester.init_agents(agents)

    # Step through simulation
    for step_num in range(10):
        # Issue step pulse and wait for completion
        cycles = await tester.pulse_step()

        # Read agent state (outputs guaranteed stable)
        x, y, angle = await tester.read_agent(0)
        print(f"Step {step_num}: Agent 0 at ({x:.1f}, {y:.1f}), took {cycles} cycles")

        # Or read all agents
        all_agents = await tester.read_all_agents()
        for agent in all_agents:
            print(f"  Agent {agent['agent_id']}: ({agent['x_px']:.1f}, {agent['y_px']:.1f})")
```

## Key Methods

### Setup
- `reset()` - Reset DUT
- `set_parameters(move_speed, sensor_distance, sensor_angle, turn_speed)` - Configure
- `init_agents(agents_dict)` - Initialize agents from dict {id: (x_px, y_px, angle_rad)}

### Stepping
- `pulse_step()` - Process one step, returns number of cycles taken
- Waits for `step_busy` to go high, then `step_ready` to go high

### Readout (after step_ready=1)
- `read_agent(agent_id)` - Returns (x_px, y_px, angle_rad)
- `read_all_agents()` - Returns list of agent dicts
- `dump_step(output_dir, step_num)` - Save states to JSON

## Expected Behavior

### Single Agent Movement
```python
# Agent at (160, 120) facing 0° (right), move_speed=1.0
await tester.init_agents({0: (160.0, 120.0, 0.0)})

# After 1 step: should be at (161, 120) - moved 1 pixel right
x, y, angle = await tester.read_agent(0)
assert x == 161.0, f"Expected 161.0, got {x}"
```

### Circle Pattern (Default Initialization)
Agents spawn in a circle:
- Center: (160, 120)
- Radius: 80 pixels
- Facing: inward
- When stepped: should move toward center, deposit trail

## Output Files

When dumping:
```
output_dir/agent_state_step_00000.json
output_dir/agent_state_step_00001.json
...
```

Each JSON contains:
```json
{
  "step": 0,
  "agents": [
    {
      "agent_id": 0,
      "x_px": 160.0,
      "y_px": 120.0,
      "angle_rad": 0.0
    },
    ...
  ]
}
```

## Troubleshooting

### "step_busy never asserted"
- Check that `step_request` pulse is long enough (at least 1 cycle)
- Verify RTL is not in reset

### "step_ready never asserted"
- Processing cycles insufficient for agent count
- Increase `AGENT_PROCESS_CYCLES` in `step_controller.sv`
- Current: `(NUM_AGENTS * 25) + 100`

### Agents not initialized
- Verify `debug_agent_write_en` is pulsed correctly
- Each agent field (x, y, angle) requires 1 write cycle
- Total init time: `NUM_AGENTS * 3` cycles minimum

### Slow readout (timeout during read_all_agents)
- Increase timeout in `pulse_step()` or `read_all_agents()`
- Reading each agent field takes 2 cycles (set idx/sel, wait, read data)
- For 100 agents × 3 fields × 2 cycles = 600 cycles minimum

## Files

- **Implementation**: `rtl/src/step_controller.sv`, `rtl/src/step_test_tb.sv`
- **Tests**: `rtl/sim/step_test.py`
- **Documentation**: `STEP_CONTROLLER_IMPLEMENTATION.md`
- **Build**: `make test_step_control` (or `make test_step_controller_movement`)

## Integration Path

1. ✅ **Current**: Step controller works with Icarus Verilog cocotb
2. **Next**: Integrate with regression test framework
3. **Future**: Port to Verilator for faster simulation
4. **FPGA**: Implement USB/UART interface for hardware debugging

---

**Test Status**: ✅ Movement test passing - ready for integration!
