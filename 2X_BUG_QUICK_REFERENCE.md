# 2x Movement Bug - Quick Reference Card

## 🎯 The Bug in One Sentence
RTL UPDATE_POS wraps at pixel-scaled fixed-point range (WIDTH_FP) instead of bit boundary, causing positions to stay in fixed-point format and accumulate scaling errors.

## 📍 Location
**File**: `rtl/src/agent_processor.sv`
**Lines**: 346-356 (UPDATE_POS state)
**Module**: `agent_processor`

## 🔴 Buggy Code
```verilog
wrapped_x = ((sum_x % WIDTH_FP) + WIDTH_FP) % WIDTH_FP;
wrapped_y = ((sum_y % HEIGHT_FP) + HEIGHT_FP) % HEIGHT_FP;
new_x <= wrapped_x;  // ← Wrong: stays in fixed-point
new_y <= wrapped_y;  // ← Wrong: stays in fixed-point
```

Where:
- `WIDTH_FP = 320 × 4096 = 1,310,720` (pixel-scaled)
- `HEIGHT_FP = 240 × 4096 = 983,040` (pixel-scaled)

## 🟢 Correct Approach (Python)
```python
# Step 1: Add movement (fixed-point)
new_x = (agent.x + dx) & self.fp.mask  # Wrap at bit boundary

# Step 2: Convert to pixels
px = int(new_x >> 12) % self.width  # Shift by frac_bits

# Step 3: Convert back to fixed-point
agent.x = px * 4096  # Multiply by scale
```

## 🔧 The Fix
Replace UPDATE_POS to:
1. Wrap at bit boundary: `& 0x1FFFFFF` (not `% WIDTH_FP`)
2. Convert to pixels: `>> FP_FRAC_BITS` (12 bits)
3. Wrap pixel range: `% WIDTH` and `% HEIGHT`
4. Convert back to fixed: `* FP_SCALE` (4096)

## 📊 Evidence
| Test | Agents | Steps | Expected | Observed | Error |
|------|--------|-------|----------|----------|-------|
| Test 1 | 100 | 10 | 10 px | 20 px | 2.0x |
| Test 2 | 100 | 1 | 1 px | 2 px | 2.0x |
| Test 5 | 500 | 50 | 50 px | 100 px | 2.0x |
| Test 10 | 100 | 2000 | 2000 px | 4000 px | 2.0x |

## ⚡ Impact
- **Movement**: 2× expected distance
- **All tests**: 9/10 FAIL (mean error 97-167 px)
- **Consistency**: Always 2x ratio (not random)

## 🧪 Testing
```bash
# Run focused testbench
cd rtl/sim
make test_2x_movement_bug

# Run full regression (should pass after fix)
python3 run_regression_tests.py
```

## ✅ Success Criteria After Fix
- [x] Testbench: `observed dx ≈ 1.0 px` (not 2.0)
- [x] Regression: `10/10 PASSED` (not 9/10)
- [x] Error: `< 0.5 px` (not 97-167 px)
- [x] Ratio: `1.0x` (not 2.0x)

## 📚 Documentation
- **Root Cause Analysis**: `2X_BUG_ROOT_CAUSE_IDENTIFIED.md`
- **Visual Comparison**: `2X_BUG_VISUALIZATION.txt`
- **Testing Guide**: `rtl/sim/2X_MOVEMENT_BUG_TEST.md`
- **Testbench Code**: `rtl/sim/test_2x_movement_bug.py`

## 🔑 Key Insight
**Python does**: FP → Pixels → back to FP (resets scaling at each step)
**RTL does**: FP → stays FP (accumulates scaling error)

This fundamental difference in coordinate transformation is the 2x bug.
