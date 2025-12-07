# Regression Test Plan for SlimeSimulator

## Overview
Comprehensive regression testing strategy for FPGA-based slime mold simulator with multiple test levels and CI/CD integration.

## Test Hierarchy

### 1. Unit Tests (Cocotb)
**Purpose:** Test individual RTL modules in isolation
**Runtime:** Fast (seconds to minutes)
**CI Integration:** Run on every push
**Location:** `tests/unit/`

**Modules to Test:**
- `lfsr.sv` - Random number generator
  - Sequence validation
  - Seed repeatability
  - Period verification
- `fixed_point_mult.sv` - Q12.12 multiplier
  - Arithmetic accuracy
  - Overflow/saturation
  - Edge cases
- `trig_lut.sv` - Sin/cos lookup tables
  - Table accuracy vs Python reference
  - Boundary conditions
  - Symmetry properties
- `vga_controller.sv` - VGA timing
  - Hsync/vsync timing (640x480@60Hz)
  - Pixel clock generation
  - Frame boundaries
- `debouncer.sv` - Button debouncing
  - 20ms debounce window
  - Glitch rejection

### 2. Integration Tests (Verilator)
**Purpose:** Test subsystem interactions and data flow
**Runtime:** Medium (minutes to hours)
**CI Integration:** Run on PR and nightly
**Location:** `tests/integration/`

**Test Scenarios:**
- Agent processor pipeline (19 stages)
  - Single agent through full pipeline
  - Multi-agent concurrent processing
  - Hazard handling
- Trail map read/write
  - Concurrent access patterns
  - Memory consistency
  - Boundary conditions
- Python vs RTL comparison
  - Bit-exact arithmetic validation
  - State evolution matching
  - 10-100 steps, 10-100 agents

### 3. System Tests (Full Simulation)
**Purpose:** End-to-end validation with full agent count
**Runtime:** Long (hours)
**CI Integration:** Nightly builds only
**Location:** `tests/system/`

**Test Scenarios:**
- Full-scale simulation
  - 1000 agents, 100+ steps
  - Memory bandwidth validation
  - Performance benchmarking
- Resolution scaling
  - 160x120, 320x240, 640x480
  - Resource utilization
- Long-duration stability
  - 1000+ steps
  - No state corruption
  - Trail decay correctness

### 4. Synthesis Tests (Vivado)
**Purpose:** Verify design synthesizes and meets timing
**Runtime:** Very long (30min - 2hrs)
**CI Integration:** Nightly and release builds
**Location:** `tests/synthesis/`

**Validation:**
- Synthesis success
  - No critical warnings
  - Resource utilization within bounds
  - LUT: <20,800 (Basys3)
  - FF: <41,600
  - BRAM: <100
  - DSP: <90
- Timing closure
  - 100 MHz clock constraint met
  - No setup/hold violations
  - Clean timing report
- Implementation quality
  - Placement success
  - Routing completion
  - Power estimation reasonable

## Test Organization

```
tests/
├── unit/                    # Cocotb unit tests
│   ├── test_lfsr.py
│   ├── test_fixed_point.py
│   ├── test_trig_lut.py
│   ├── test_vga.py
│   └── test_debouncer.py
├── integration/             # Verilator integration tests
│   ├── test_agent_pipeline.py
│   ├── test_trail_map.py
│   ├── test_python_rtl_match.py
│   └── fixtures/            # Test data and references
├── system/                  # Full-scale system tests
│   ├── test_full_simulation.py
│   ├── test_resolution_scaling.py
│   └── test_long_duration.py
└── synthesis/               # Vivado synthesis tests
    ├── test_synthesis.py
    ├── test_timing.py
    └── scripts/
        ├── synth_check.tcl
        └── timing_check.tcl
```

## CI/CD Strategy

### GitHub Actions Workflows

**1. Unit Tests (Fast - Every Push)**
```yaml
- Cocotb unit tests
- Runtime: <5 minutes
- Runs on: ubuntu-latest
- Dependencies: Python, Verilator, Cocotb
```

**2. Integration Tests (Medium - Pull Requests)**
```yaml
- Verilator integration tests
- Python vs RTL validation
- Runtime: <30 minutes
- Runs on: ubuntu-latest
- Requires: Verilator, larger runner
```

**3. Nightly Build (Long - Scheduled)**
```yaml
- Full system tests
- Vivado synthesis check (if available)
- Runtime: 1-2 hours
- Runs on: self-hosted or large runner
- Scheduled: Daily at 2 AM UTC
```

### Test Gating

- **Merge Requirements:**
  - All unit tests pass
  - Integration tests pass for affected modules
  - No new lint warnings

- **Release Requirements:**
  - All tests pass (unit + integration + system)
  - Synthesis successful
  - Timing closure verified
  - Documentation updated

## Metrics and Reporting

### Coverage Metrics
- Line coverage (RTL)
- Branch coverage
- FSM state coverage
- Functional coverage points

### Performance Metrics
- Simulation throughput (agents/sec)
- Memory usage
- Compilation time
- Resource utilization trends

### Quality Metrics
- Test pass rate over time
- Mean time between failures
- Regression detection rate

## Implementation Phases

### Phase 1: Foundation (Week 1)
- [ ] Restructure test directories
- [ ] Migrate cocotb tests to `tests/unit/`
- [ ] Create GitHub Actions for unit tests
- [ ] Document test execution

### Phase 2: Integration (Week 2)
- [ ] Rename Verilator tests to `tests/integration/`
- [ ] Add Python vs RTL validation suite
- [ ] Create integration test GitHub Action
- [ ] Add test fixtures and references

### Phase 3: System Tests (Week 3)
- [ ] Implement full-scale system tests
- [ ] Add resolution scaling tests
- [ ] Create nightly build workflow
- [ ] Performance benchmarking

### Phase 4: Synthesis Validation (Week 4)
- [ ] Vivado synthesis test scripts
- [ ] Timing analysis automation
- [ ] Resource utilization tracking
- [ ] Release validation workflow

## Success Criteria

- All existing tests migrated and passing
- CI runs on every commit (<10 min feedback)
- Nightly builds catch integration issues
- Synthesis validated before releases
- Clear test failure diagnostics
- Reproducible test environments
