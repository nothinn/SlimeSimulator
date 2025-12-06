# Why These Testbenches Use python_reference.py (Not slime_simulator.py)

## Overview

The cocotb testbenches (`test_modules_vs_python.py`) use `python_reference.py` instead of `slime_simulator.py` for module-level comparisons. This document explains why.

## Key Difference: Interface Design

### slime_simulator.py (Main Simulator)
- **Designed for:** Full end-to-end slime mold simulation
- **TrigLUT Interface:** Takes **fixed-point angles** as input (radians in Q12.12 format)
  ```python
  py_trig = TrigLUT(fp, table_bits=10)  # Takes FixedPoint object
  angle_fixed = fp.to_fixed(0.5)  # Convert float to Q12.12
  sin_val = py_trig.sin(angle_fixed)  # Takes fixed-point angle
  ```
- **Focus:** High-level behavioral match with Python semantics

### python_reference.py (RTL Reference Model)
- **Designed for:** Direct comparison with RTL modules
- **TrigLUT Interface:** Takes **direct table indices** (0-1023)
  ```python
  py_trig = TrigLUT(addr_bits=10, frac_bits=12)  # Just bit widths
  sin_val = py_trig.sin(256)  # Takes integer index
  cos_val = py_trig.cos(256)
  ```
- **Focus:** Bit-exact match with RTL implementation

## RTL Module Interfaces

The actual RTL modules use direct index-based interfaces:

### rtl/src/trig_lut.sv
```verilog
input  logic [9:0]  angle_idx,      // Direct index (0-1023)
output logic [24:0] sin_out,        // Sine output
output logic [24:0] cos_out         // Cosine output
```

### rtl/src/fixed_point_mult.sv
```verilog
input  logic signed [24:0] a,       // Q12.12 fixed-point value
input  logic signed [24:0] b,       // Q12.12 fixed-point value
output logic signed [24:0] result   // Q12.12 result
```

## Test Interface Requirements

**Cocotb testbenches directly access RTL signals**, so they need reference models that match those signal interfaces:

1. **Direct Index Access** - RTL trig_lut takes `angle_idx` (0-1023), not fixed-point angles
2. **Bit-Exact Values** - RTL fixed-point multiply needs exact 25-bit values, not Python floats
3. **Unsigned 2's Complement** - RTL uses unsigned 2's complement for negative trig values
4. **No Conversion Overhead** - Tests should compare raw RTL values directly

## Complementary Use

**Both reference models are valuable:**

| Use Case | Model | Reason |
|----------|-------|--------|
| Cocotb module tests | python_reference.py | Matches RTL signal interfaces |
| Regression tests | slime_simulator.py | Full behavioral simulation |
| Full simulation | slime_simulator.py | Complete physics engine |

## Regression Test Usage

The regression test suite (`run_regression_tests.py`) uses **slime_simulator.py** because:
- It needs full agent behavior (sensing, turning, moving)
- It simulates complete trail maps
- It uses fixed-point angles and positions throughout
- It generates reference data for RTL comparison

## Why Not Unify?

Could we make python_reference.py just wrap slime_simulator.py?

**No.** They serve fundamentally different purposes:

- **python_reference.py**: RTL value equivalence (indices, raw bit patterns)
- **slime_simulator.py**: Behavioral equivalence (physics, full simulation)

Trying to use one for both purposes would:
1. Add unnecessary angle-to-index conversion overhead in tests
2. Mix two different abstraction levels
3. Make test assertions more complex
4. Hide potential interface bugs

## Summary

- **Cocotb tests use `python_reference.py`** because RTL modules use direct index/bit interfaces
- **Regression tests use `slime_simulator.py`** because they need full behavioral simulation
- **Both are correct** - each optimized for its specific use case
- **No conflict** - they complement each other in the testing strategy

The testbenches explicitly import from `python_reference.py` with a clear comment explaining this design choice.
