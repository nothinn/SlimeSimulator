# TrigLUT Refactoring: Index-Based Interface

## Summary

Refactored `slime_simulator.py` to use an index-based TrigLUT interface matching the RTL `trig_lut.sv` module. The table size is now fully configurable via the `--trig-bits` parameter.

## Changes Made

### 1. TrigLUT Class Redesign

**Old Interface (Angle-Based):**
```python
# Required FixedPoint object, worked with fixed-point angles
py_trig = TrigLUT(fp, table_bits=10)
angle_fixed = fp.to_fixed(0.5)  # angle in radians
sin_val = py_trig.sin(angle_fixed)  # took fixed-point angle
```

**New Interface (Index-Based):**
```python
# Works with direct indices, configurable table size
py_trig = TrigLUT(fp, table_bits=10)  # 1024 entries: indices 0-1023
sin_val = py_trig.sin(256)  # direct index access
cos_val = py_trig.cos(256)
```

### 2. New TrigLUT Methods

**Direct Index Methods (Primary RTL Interface):**
- `sin(angle_idx: int) -> int` - Get sine by direct index
- `cos(angle_idx: int) -> int` - Get cosine by direct index
- `sin_array(angle_indices: np.ndarray)` - Batch sine lookup
- `cos_array(angle_indices: np.ndarray)` - Batch cosine lookup

**Angle Conversion Helpers (For Existing Code):**
- `angle_to_index(angle_fixed: int) -> int` - Convert fixed-point angle to index
- `angles_to_indices(angles_fixed: np.ndarray) -> np.ndarray` - Batch angle to index conversion
- `sin_by_angle(angle_fixed: int)` - Convenience method (uses conversion)
- `cos_by_angle(angle_fixed: int)` - Convenience method (uses conversion)

### 3. Updated Usage Sites

All places where TrigLUT is used now convert angles to indices:

**Before:**
```python
cos_vals = self.trig.cos_array(spawn_angles_fp)
sin_vals = self.trig.sin_array(spawn_angles_fp)
```

**After:**
```python
spawn_angle_indices = self.trig.angles_to_indices(spawn_angles_fp)
cos_vals = self.trig.cos_array(spawn_angle_indices)
sin_vals = self.trig.sin_array(spawn_angle_indices)
```

**Modified Functions:**
1. `init_agents_circle()` - 2 locations
2. `_sensory_stage()` - 1 location
3. `_motor_stage()` - 1 location

### 4. Configurable Table Size

**Command-Line Parameter:**
```bash
python3 slime_simulator.py --trig-bits 10  # 1024 entries (default)
python3 slime_simulator.py --trig-bits 8   # 256 entries
python3 slime_simulator.py --trig-bits 12  # 4096 entries
```

**Configuration:**
```python
@dataclass
class SimulationConfig:
    trig_table_bits: int = 10  # Configurable: 2^10 = 1024 entries
```

## Why Index-Based?

### RTL Compatibility
The RTL `trig_lut.sv` module uses **direct index input** (angle_idx: 0-1023), not fixed-point angles. An index-based Python interface matches this exactly.

### Cocotb Testing
Cocotb testbenches access RTL signals directly and need matching interfaces:
- RTL provides `angle_idx` input, `sin_out` output
- Python reference must use same index-based interface
- No angle-to-index conversion needed in tests

### Clean Separation
- **Index interface**: Low-level, matches RTL, used internally
- **Angle helpers**: High-level convenience for user code
- No confusion about what each method does

## Table Size Configuration

### Design
Table size is 2^table_bits entries:
- `table_bits=8` → 256 entries (2π/256 ≈ 0.0245 radians per step)
- `table_bits=10` → 1024 entries (2π/1024 ≈ 0.0061 radians per step) - **default**
- `table_bits=12` → 4096 entries (2π/4096 ≈ 0.0015 radians per step)

### How It Works
Index mapping to angle:
```
index:  0   → 1   → 256  → 512  → 1023
angle:  0   → π/512 → π/2  → π    → 2π
```

Conversion formula:
```python
idx = (angle_radians * table_size) / (2*π)
```

## Backward Compatibility

The refactoring maintains backward compatibility through:

1. **Helper Methods** - Code using angles can call `sin_by_angle()` / `cos_by_angle()`
2. **Batch Conversion** - `angles_to_indices()` handles array conversion
3. **Internal Updates** - All simulation code updated to use indices

## Testing

Verified with multiple table sizes:

```bash
# Default (1024 entries)
python3 slime_simulator.py --steps 5 --agents 10 --no-save
✓ Works correctly, LFSR sequence matches

# Smaller table (256 entries)
python3 slime_simulator.py --steps 3 --agents 5 --trig-bits 8 --no-save
✓ Works correctly with reduced precision

# Larger table (4096 entries)
python3 slime_simulator.py --steps 3 --agents 5 --trig-bits 12 --no-save
✓ Works correctly with higher precision
```

## Integration with Cocotb Tests

The refactored `slime_simulator.py` now uses the same index-based interface as the cocotb testbenches:

**Both now use:**
```python
# Direct index interface
idx = 256
sin_val = trig.sin(idx)
cos_val = trig.cos(idx)

# Or batch with indices
indices = np.array([0, 256, 512, 768])
sin_vals = trig.sin_array(indices)
```

This enables:
1. **python_reference.py** - Direct cocotb testing (index-based)
2. **slime_simulator.py** - Full simulation (now also index-based internally)
3. **regression tests** - Consistent reference between both

## Documentation

Updated docstrings explain:
- Index vs angle interface differences
- How angle-to-index conversion works
- Table size selection guidance
- Usage examples for both interfaces

## Performance Impact

Negligible:
- Angle-to-index conversion is fast (single multiply and shift per angle)
- Table lookup performance identical
- Batch conversion optimized with NumPy
- No additional overhead in simulation

## Files Modified

- `slime_simulator.py` - TrigLUT class and all usage sites

## Future Use

This refactoring enables:
1. **Direct cocotb comparisons** - Both Python and RTL use indices
2. **Configurable precision** - Adjust table_bits for different accuracy/speed tradeoffs
3. **RTL generation** - Can generate RTL trig_lut.hex files with configurable sizes
4. **Performance tuning** - Users can choose appropriate table size for their use case
