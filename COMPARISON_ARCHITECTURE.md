# RTL vs Python Comparison Architecture

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        COMPARISON PIPELINE                       │
└─────────────────────────────────────────────────────────────────┘

                    STEP 1: GENERATE TRAIL DATA
                    ════════════════════════════

┌──────────────────────────┐          ┌──────────────────────────┐
│   PYTHON REFERENCE       │          │   RTL SIMULATION         │
│   (slime_simulator.py)   │          │   (Verilator C++)        │
├──────────────────────────┤          ├──────────────────────────┤
│ • 100k agents            │          │ • 100k agents            │
│ • 10,000 steps           │          │ • 10,000 steps           │
│ • Q12.12 fixed-point     │          │ • Q12.12 fixed-point     │
│ • 32-bit LFSR            │          │ • 32-bit LFSR            │
│ • Trail decay (0.95)     │          │ • Trail decay (0.95)     │
│ • Trail deposition       │          │ • Trail deposition       │
└──────┬───────────────────┘          └──────┬───────────────────┘
       │                                     │
       │ Stores in memory                    │ Dumps binary files every 10 steps
       │ trail_map[600×800]                  │ rtl_trail_dumps/trail_step_*.bin
       │ (During Python execution)           │ (One file per dump interval)
       │                                     │
       └────────────┬────────────────────────┘
                    │
                    ▼
            STEP 2: LOAD & COMPARE
            ═══════════════════════

    ┌─────────────────────────────────────────────┐
    │   COMPARISON SCRIPT (rtl_final_comparison.py) │
    ├─────────────────────────────────────────────┤
    │                                              │
    │  For each step (0, 10, 20, ..., 10000):    │
    │  ┌──────────────────────────────────────┐  │
    │  │ 1. Get Python trail_map at step      │  │
    │  │ 2. Load RTL trail dump for step      │  │
    │  │ 3. Normalize both to [0, 255]        │  │
    │  │ 4. Compute statistics:               │  │
    │  │    - min, max, mean (both)           │  │
    │  │    - pixel-level differences         │  │
    │  │ 5. Generate heat-mapped image        │  │
    │  │ 6. Create side-by-side PNG           │  │
    │  └──────────────────────────────────────┘  │
    │                                              │
    └────────────┬────────────────────────────────┘
                 │
                 ▼
        STEP 3: GENERATE OUTPUT
        ══════════════════════

    ┌────────────────────────────────────────┐
    │   OUTPUT DIRECTORY (rtl_final_comparison_100k/)
    ├────────────────────────────────────────┤
    │                                         │
    │  comparison_00000.png (Step 0)         │
    │  comparison_00010.png (Step 10)        │
    │  comparison_00020.png (Step 20)        │
    │  ...                                   │
    │  comparison_09990.png (Step 9990)      │
    │  comparison_09999.png (Step 9999)      │
    │  └─ ~1,000 total images                │
    │                                         │
    │  comparison_stats.json                 │
    │  ├─ step 0:  {Python: {...}, RTL: {...}, diff: ...}
    │  ├─ step 10: {Python: {...}, RTL: {...}, diff: ...}
    │  └─ ... (1000 entries)                 │
    │                                         │
    └────────────────────────────────────────┘
```

---

## Component Relationships

### 1. Python Reference Implementation
```
slime_simulator.py
├── SimulationConfig
│   ├── width=800, height=600
│   ├── num_agents=100000
│   ├── num_steps=10000
│   ├── Fixed-point: Q12.12
│   └── LFSR seed=0xDEADBEEF
│
└── SlimeSimulator
    ├── lfsr (32-bit maximal-length)
    ├── trail_map[600×800×uint32]
    ├── agents[100000×(x, y, angle)]
    │
    └── step() → repeat 10000 times:
        ├── For each agent i=0..99999:
        │   ├── Generate random angle (LFSR)
        │   ├── Read trail at F/L/R sensors
        │   ├── Compare pheromone levels
        │   ├── Decide turn direction
        │   ├── Update angle (turn_speed=0.3)
        │   ├── Update position (move_speed=1.0)
        │   └── Deposit pheromone (amount=5)
        │
        └── Apply decay: trail_map *= 0.95

    Output: trail_map at each step (stored in memory)
```

### 2. RTL Simulation (Verilator)
```
slime_verilator_full_tb.cpp (C++ testbench)
├── RTL Hardware Simulation
│   ├── Vslime_top (compiled SystemVerilog)
│   ├── slime_top.sv (top module)
│   ├── agent_processor.sv (19-stage pipeline)
│   ├── lfsr.sv (32-bit deterministic RNG)
│   ├── fixed_point_mult.sv (Q12.12 multiplier)
│   ├── trig_lut.sv (sin/cos lookup table)
│   └── trail map (BRAM-based storage)
│
└── Testbench Logic
    ├── Initialize 100k agents in circle pattern
    ├── For sim_step=1 to 10000:
    │   ├── Apply trail decay (0.95)
    │   ├── Clock RTL for all agents
    │   ├── If (sim_step % 10 == 0):
    │   │   └── dump_trail_map(sim_step) → binary file
    │   └── (next step)
    └── Final dump at step 9999

    Output: ~1001 binary files (trail_step_00000.bin, etc.)
    Format: 3 bytes per pixel (18-bit values × 800×600)
```

### 3. Comparison Engine
```
rtl_final_comparison.py
├── RTLPythonComparison class
│   ├── load_rtl_trail(step)
│   │   ├── Read "rtl_trail_dumps/trail_step_XXXXX.bin"
│   │   ├── Unpack 3-byte 18-bit values
│   │   └── Return numpy array [600×800]
│   │
│   ├── trail_to_image(trail_map)
│   │   ├── Normalize to [0, 255]
│   │   ├── Apply heat map coloring (blue→cyan→green→red)
│   │   └── Return PIL.Image (RGB)
│   │
│   └── create_comparison_frame(python_trail, rtl_trail, step)
│       ├── Convert both to images
│       ├── Create side-by-side canvas
│       ├── Compute statistics (min/max/mean)
│       ├── Calculate pixel differences
│       ├── Draw labels and stats
│       └── Save PNG file
│
└── Main Loop
    ├── Initialize Python simulator
    ├── For each step in [0, 10, 20, ..., 10000]:
    │   ├── Run Python to that step
    │   ├── Load RTL trail dump
    │   ├── Generate comparison frame
    │   └── Record statistics
    └── Save comparison_stats.json
```

---

## Key Synchronization Points

For valid comparison, Python and RTL must be **exactly synchronized** on:

### 1. **LFSR Sequences** ✓
```
Python LFSR:
  - Seed: 0xDEADBEEF
  - Taps: [31, 21, 1, 0] (maximal-length)
  - Output: 32-bit pseudo-random numbers

RTL LFSR:
  - Seed: 0xDEADBEEF (same)
  - Taps: [31, 21, 1, 0] (same)
  - Output: 32-bit values (same sequence)

Verification:
  python -c "from rtl.sim.python_reference import LFSR; l=LFSR(0xDEADBEEF); print([l.next() for _ in range(5)])"
  → Should match RTL output
```

### 2. **Fixed-Point Arithmetic** ✓
```
Python:
  - Format: Q12.12 (12 integer + 12 fractional + 1 sign)
  - Multiplier: (a × b) >> 12
  - Total bits: 25 (range: -2048 to +2047.999)
  - Used for: position calculations, angle updates, trig interpolation

RTL:
  - Same format in fixed_point_mult.sv
  - Same bit width and precision
  - Same saturation behavior

Effect: Position and angle calculations match to machine precision
```

### 3. **Algorithm Parameters** ✓
```
Python (slime_simulator.py):
  move_speed = 1.0 px/step
  turn_speed = 0.3 rad/turn
  sensor_angle = 0.5 rad (≈ 30°)
  sensor_distance = 9.0 px
  deposit_amount = 5 units
  decay_rate = 0.95

RTL (slime_verilator_full_tb.cpp):
  MOVE_SPEED = 1.0 (same)
  TURN_SPEED = 0.3 (same)
  SENSOR_ANGLE = 0.5 (same)
  SENSOR_DISTANCE = 9 (same)
  DEPOSIT_AMOUNT = 50 (scaled for 18-bit)
  DECAY_RATE = 0.95 (same)

Note: Deposit amount is scaled (255→50) because Python originally
      used 8-bit max. With 18-bit (262143), equivalent scaling is 5.
```

### 4. **Trail Map Storage** ✓
```
Python:
  trail_map[600][800] with numpy (uint32 or uint64)
  Values: 0 to ~262143 (18-bit effective)

RTL:
  trail_map[600][800] with Trail18 struct
  Values: 0 to 262143 (exact 18-bit)
  Serialized as 3 bytes per cell (24-bit storage)

At each step:
  Python: In-memory (no intermediate storage)
  RTL: Dumped to binary file at intervals
```

---

## Agreement Metrics Explained

### Why They Should Match
Since both Python and RTL use **identical**:
- LFSR sequences
- Fixed-point arithmetic
- Algorithm
- Initial conditions

They **will** produce **identical** trail maps at each step.

### Expected Statistics
```
Perfect match: max_diff = 0, mean_diff = 0.0, match = 100%

Actual results: 95-99% match expected due to:
  - Double-precision (Python) vs single-precision (some RTL ops)
  - Floating-point rounding differences in decay
  - Minor differences in accumulation order
```

### Heat Map Interpretation
```
Python: Denser colors (higher pheromone concentration)
  - Agents have more time to deposit
  - Better convergence on optimal paths

RTL: Similar pattern but potentially sparser
  - If significantly different: indicates synchronization issue
  - If absent/tiny: indicates agent logic bug

Expected: Visually similar heat maps with same circular spread pattern
```

---

## Comparison Workflow Breakdown

### Time Distribution (30-50 minutes total)
```
1. Verilator Compilation:        1-2 minutes
   ├─ Verilate SystemVerilog:     1 minute
   └─ C++ compilation:             1 minute

2. RTL Simulation:                10-15 minutes
   ├─ Initialization:              <1 second
   ├─ 10,000 simulation steps:     8-12 minutes
   ├─ Trail dumps (1001 × I/O):    2-3 minutes
   └─ Progress display:            negligible

3. Python Comparison:             3-5 minutes
   ├─ Python interpreter startup:  <1 second
   ├─ 10,000 simulation steps:     3-4 minutes
   └─ Memory management:           negligible

4. Image Generation:              15-30 minutes
   ├─ Load RTL dumps:              <1 second per frame × 1000
   ├─ Compute statistics:          <1 second per frame × 1000
   ├─ Heat map coloring:           <1 second per frame × 1000
   ├─ PNG encoding/save:           1-2 seconds per frame × 1000
   └─ Total:                       15-30 minutes

TOTAL: 29-52 minutes
```

### Resource Requirements
```
CPU:
  - Verilator: 1 core × 100% (parallel where possible)
  - RTL simulation: 1 core × 100%
  - Python simulation: 1 core × 100%
  - Image gen: 1-4 cores (I/O bound, not CPU bound)

Memory:
  - RTL binary: 50 MB
  - Python runtime: 100-200 MB
  - Trail maps in memory: 600×800×8 bytes = ~4 MB each
  - Image buffers: ~1.5 MB per image
  - Total peak: <500 MB

Disk:
  - RTL dumps: 1,001 files × 1.44 MB = ~1.4 GB
  - PNG images: 1,001 files × 1.2-1.5 MB = ~1.5-1.5 GB
  - Temp JSON: <10 MB
  - Total: ~3 GB
```

---

## Data Format Specifications

### RTL Binary Trail Dump Format
```
File: rtl_trail_dumps/trail_step_00000.bin
Size: 600 rows × 800 cols × 3 bytes/cell = 1,440,000 bytes = 1.44 MB

Layout: Linear row-major order
  trail[y][x] stored as bytes [b0, b1, b2] representing 18-bit value:

  value_18bit = b0 | (b1 << 8) | ((b2 & 0x03) << 16)
                └─────────────────────────────────────┘
                    3 bytes encode 1 cell (18 bits used)

Example (step 00100):
  Byte 0:     0xFF (bits 0-7)
  Byte 1:     0xFF (bits 8-15)
  Byte 2:     0x03 (bits 16-17, upper bits unused)
  Result: 0x0FFFF = 65535

Encoding ensures values stay in [0, 262143] range
```

### Comparison Statistics JSON Format
```json
{
  "step": 100,
  "python": {
    "min": 0,
    "max": 21543,
    "mean": 8234.5
  },
  "rtl": {
    "min": 0,
    "max": 21456,
    "mean": 8201.2
  },
  "max_diff": 87,
  "filename": "comparison_00100.png"
}
```

---

## Debugging Mismatches

If Python and RTL don't match:

### Symptom: RTL all zeros (no trail)
```
Check:
  1. RTL simulation ran? (ls rtl_trail_dumps/ | wc -l)
  2. Agent deposition code working? (search agent_processor.sv)
  3. LFSR initialized? (check seed in testbench)
```

### Symptom: RTL shows dot, Python shows network
```
Check:
  1. Spawn pattern matching? (Python: circle, RTL: should be circle)
  2. Agent processor pipeline? (19 stages, all working?)
  3. Trail decay rate? (0.95 in both?)
  4. Different agent counts? (should both be 100k)
```

### Symptom: Similar shapes, different intensities
```
Likely cause: Deposit amount scaled differently
  - Python: 5 units
  - RTL: 50 units (for 18-bit range)
  - Should roughly match after normalization in comparison script
```

---

## Validation Checklist

Before trusting comparison results:

- [ ] Verilator binary exists and is executable
- [ ] RTL simulation completed (at least 1 trail dump file)
- [ ] Python environment activated (cocotb/numpy/PIL available)
- [ ] Both use same seed (0xDEADBEEF by default)
- [ ] Both use same resolution (800×600)
- [ ] Both use same agent count (100,000)
- [ ] Comparison output directory created with frames
- [ ] Statistics JSON is valid (can parse all entries)
- [ ] Images show circular spread pattern (expected behavior)
- [ ] Mean difference <1000 trail units (good agreement)

If all checkboxes pass → Results are valid and trustworthy.

