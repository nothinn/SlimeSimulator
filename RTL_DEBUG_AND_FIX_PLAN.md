# RTL Debug and Fix Plan

## Objective
Fix RTL simulation so it produces trail values matching Python reference implementation.

## Current Issue
RTL trail values remain zero despite agent processor integration and LUT files loading correctly.

## Investigation Phases

### Phase 1: Instrumentation and Debugging
**Goal:** Add comprehensive debug signals to trace execution flow

Tasks:
1. Add debug outputs to coordinator state machine
   - Log state transitions (IDLE → INITIALIZE → RUNNING)
   - Log when agents are fed to processor
   - Log when processor outputs (proc_done, agent update)

2. Add debug outputs to agent processor signals
   - Log proc_start pulses
   - Log proc_done assertions
   - Log trail_write_en and trail_write_data values
   - Log agent input/output values

3. Update testbench to print debug signals
   - Print coordinator state each cycle
   - Print processor signals each cycle
   - Print trail memory access patterns

### Phase 2: Trace Coordinator Execution
**Goal:** Verify coordinator state machine is working

Tasks:
1. Verify coordinator starts and enters RUNNING state
   - Check state transitions in debug output
   - Verify sim_start signal propagates
   - Confirm state machine reaches RUNNING

2. Verify agent feeding
   - Check if processor receives agents sequentially
   - Verify agent_idx increments correctly
   - Confirm agent state is read from memory

3. Verify state latching
   - Check if latched_valid flag is set when proc_done
   - Verify processor outputs are saved
   - Confirm agent memory is updated with new values

### Phase 3: Trace Processor Execution
**Goal:** Verify agent processor is running correctly

Tasks:
1. Verify processor receives valid inputs
   - Check agent_x_in, agent_y_in, agent_angle_in are non-zero
   - Verify processor receives start signal
   - Confirm proc_busy toggle indicates processing

2. Verify processor pipeline progression
   - Check processor states advance through 19 stages
   - Log stage transitions
   - Verify trig LUT outputs are sensible

3. Verify processor outputs
   - Check proc_x_out, proc_y_out, proc_angle_out change
   - Verify proc_trail_write_en is asserted
   - Check proc_trail_write_data has correct values
   - Verify proc_trail_write_x/y are valid addresses

### Phase 4: Trace Trail Memory Operations
**Goal:** Verify trail memory reads/writes work

Tasks:
1. Verify trail memory interface
   - Check debug_trail_data reads work correctly
   - Write test values and verify readback
   - Confirm memory addressing is correct

2. Verify accumulation logic
   - Check trail_we_b signal is asserted when processor writes
   - Verify trail_data_b_in contains deposit values
   - Confirm saturating add logic works
   - Check trail values increase over time

3. Verify trail scaling
   - Check deposit_amount is properly scaled (>> 12 bits)
   - Verify trail_write_data is properly scaled
   - Confirm fixed-point to integer conversion

### Phase 5: Fix Issues
**Goal:** Correct any identified problems

Tasks:
1. Fix coordinator if state machine not advancing
2. Fix processor start/done signal flow if not triggering
3. Fix agent state initialization if values are wrong
4. Fix trail write interface if writes not happening
5. Fix fixed-point scaling if arithmetic is wrong
6. Re-verify each fix works

### Phase 6: Comprehensive Testing
**Goal:** Validate RTL matches Python reference

Tasks:
1. Unit tests for each component
   - Test coordinator state transitions
   - Test processor pipeline
   - Test trail accumulation
   - Test fixed-point arithmetic

2. Integration tests
   - Run full simulation for 1, 10, 100 steps
   - Compare trail values with Python
   - Verify agent positions evolve correctly
   - Check statistical properties (mean, max, distribution)

3. Comparison tests
   - Run small-scale comparison (100 agents, 10 steps, 320x240)
   - Verify visual output matches Python
   - Check frame-by-frame correlation
   - Run larger tests (1000 agents, 100 steps)

## Success Criteria
- [ ] RTL trail values non-zero
- [ ] RTL matches Python at step 1
- [ ] RTL matches Python at step 10
- [ ] RTL visual output matches Python
- [ ] All units tests pass
- [ ] Full integration test passes (100k agents, 10k steps)

## Timeline
Expected to complete within 1-2 hours with parallel agents

## Files to Modify
- rtl/src/agent_coordinator.sv (add debug outputs)
- rtl/src/agent_processor.sv (add debug outputs)
- rtl/src/slime_top.sv (possibly)
- rtl/sim/slime_verilator_full_tb.cpp (add debug prints)

## Key Signals to Monitor
- coordinator state
- proc_start, proc_done, proc_busy
- proc_trail_write_en, proc_trail_write_data
- trail_addr_b, trail_data_b_in, trail_we_b
- agent_x, agent_y, agent_angle (input and output)
