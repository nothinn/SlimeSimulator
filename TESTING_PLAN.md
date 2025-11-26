# Comprehensive Testing Suite Plan for SlimeSimulator

## Overview
Create an autonomous, long-running test suite that validates RTL implementation against Python reference model across multiple configurations. Tests run in parallel, store results systematically, and generate minimal but informative summaries.

---

## Architecture

### Test Framework Structure
```
tests/
├── test_runner.py           # Main orchestrator for all tests
├── test_config.json         # Test configurations
├── test_suite.py            # Base test class and utilities
├── comparison_tools.py      # Trail map & agent comparison logic
├── image_generator.py       # VGA frame image generation
├── results_formatter.py     # Summary & report generation
└── runs/
    ├── test_run_001/
    │   ├── config.json
    │   ├── summary.txt
    │   ├── detailed_log.txt
    │   ├── frames/
    │   │   ├── frame_0000.png
    │   │   ├── frame_0001.png
    │   │   └── ...
    │   ├── comparisons/
    │   │   ├── step_0000.json
    │   │   ├── step_0001.json
    │   │   └── ...
    │   └── errors.json
    ├── test_run_002/
    └── ...
```

### Test Configurations (Parameterizable)
```python
[
  {
    "name": "default_1000_agents",
    "num_agents": 1000,
    "trail_width": 320,
    "trail_height": 240,
    "vga_width": 640,
    "vga_height": 480,
    "vga_upscale": 2,
    "steps": 1000,
    "seed": 0xDEADBEEF,
    "max_runtime_hours": 2
  },
  {
    "name": "small_100_agents",
    "num_agents": 100,
    "trail_width": 320,
    "trail_height": 240,
    "vga_width": 640,
    "vga_height": 480,
    "vga_upscale": 2,
    "steps": 5000,
    "seed": 0x12345678,
    "max_runtime_hours": 8
  },
  {
    "name": "high_res_500_agents",
    "num_agents": 500,
    "trail_width": 640,
    "trail_height": 480,
    "vga_width": 640,
    "vga_height": 480,
    "vga_upscale": 1,
    "steps": 2000,
    "seed": 0xABCDEF00,
    "max_runtime_hours": 4
  }
]
```

---

## Implementation Details

### 1. Test Runner (`test_runner.py`)
**Responsibilities:**
- Load test configurations from JSON
- Launch multiple tests in parallel (background processes)
- Monitor test progress
- Collect results
- Generate final summary report
- Handle timeouts and failures

**Key Features:**
```python
class TestRunner:
    def __init__(self, num_parallel=3):
        self.num_parallel = num_parallel
        self.processes = []
        self.results = {}

    def run_tests(self, config_file, output_dir):
        """Launch all tests from configuration"""
        configs = load_json(config_file)
        for i, config in enumerate(configs):
            test_run = TestRun(i, config, output_dir)
            proc = Process(target=test_run.execute)
            self.processes.append((config['name'], proc))
            if len(self.processes) >= self.num_parallel:
                self.wait_for_completion()

    def monitor_progress(self):
        """Display progress without verbose logs"""
        # Only show summary info per test

    def generate_final_summary(self):
        """Create consolidated results summary"""
```

### 2. Test Suite (`test_suite.py`)
**Base Class for Individual Tests:**
```python
class TestRun:
    def __init__(self, test_id, config, output_dir):
        self.test_id = test_id
        self.config = config
        self.output_dir = output_dir
        self.run_dir = output_dir / f"test_run_{test_id:03d}"
        self.errors = []
        self.mismatch_count = 0
        self.total_steps = 0

    def execute(self):
        """Main test loop"""
        self._setup()
        self._run_simulation()
        self._generate_summary()

    def _setup(self):
        """Initialize Python model & RTL simulation"""
        self.py_sim = SlimeSimulatorReference(**self.config)
        self.py_sim.init_agents_center()
        # Launch RTL simulator (cocotb)
        self.rtl_runner = RTLSimulationRunner(self.config)

    def _run_simulation(self):
        """Main step loop with comparison"""
        for step in range(self.config['steps']):
            # Get Python result
            py_trail, py_agents = self.py_sim.step()

            # Get RTL result
            rtl_trail, rtl_agents = self.rtl_runner.step()

            # Compare
            diffs = self._compare_step(step, py_trail, py_agents,
                                       rtl_trail, rtl_agents)

            if diffs['has_errors']:
                self.errors.append(diffs)
                self.mismatch_count += 1
                if self.mismatch_count <= 5:  # Log first 5 errors
                    self._log_mismatch(step, diffs)

            # Generate frame image
            self._save_frame_image(step, rtl_trail, rtl_agents)

            # Save comparison data (first & last only, or on error)
            if step == 0 or step == self.config['steps']-1 or diffs['has_errors']:
                self._save_comparison_json(step, diffs)

            self.total_steps += 1

            # Progress indicator (no spam)
            if step % 100 == 0:
                self._log_progress(step)

    def _compare_step(self, step, py_trail, py_agents, rtl_trail, rtl_agents):
        """Compare Python and RTL for single step"""
        return {
            'step': step,
            'has_errors': False,
            'trail_diffs': [],
            'agent_diffs': [],
            'error_count': 0
        }
```

### 3. Comparison Tools (`comparison_tools.py`)
**Fast Diff Detection:**
```python
class TrailComparator:
    """Efficient trail map comparison"""

    @staticmethod
    def compare(py_trail, rtl_trail, tolerance=0):
        """Return only differences"""
        diffs = []
        diff_positions = np.where(py_trail != rtl_trail)

        for y, x in zip(diff_positions[0], diff_positions[1]):
            diffs.append({
                'pos': (x, y),
                'python': int(py_trail[y, x]),
                'rtl': int(rtl_trail[y, x]),
                'diff': int(py_trail[y, x]) - int(rtl_trail[y, x])
            })

        return diffs[:100]  # Only return first 100 diffs

class AgentComparator:
    """Efficient agent state comparison"""

    @staticmethod
    def compare(py_agents, rtl_agents):
        """Return agent state mismatches"""
        diffs = []
        for i, (py_agent, rtl_agent) in enumerate(zip(py_agents, rtl_agents)):
            if py_agent != rtl_agent:
                diffs.append({
                    'agent_id': i,
                    'python': py_agent.to_dict(),
                    'rtl': rtl_agent.to_dict()
                })
        return diffs[:20]  # Only return first 20 agent diffs
```

### 4. Image Generator (`image_generator.py`)
**Frame Generation (VGA Output Format):**
```python
class FrameGenerator:
    """Generate PNG images matching VGA output"""

    def __init__(self, vga_width, vga_height, trail_width, trail_height, upscale):
        self.vga_width = vga_width
        self.vga_height = vga_height
        self.trail_width = trail_width
        self.trail_height = trail_height
        self.upscale = upscale

    def generate(self, trail_map, agents=None, filename=None):
        """
        Create image showing:
        - Upscaled trail map (grayscale)
        - Agent positions (overlay, optional)
        """
        # Upscale trail map
        if self.upscale > 1:
            upscaled = repeat_tile(trail_map, self.upscale)
        else:
            upscaled = trail_map

        # Convert to grayscale image (trail intensity → brightness)
        img = Image.fromarray(upscaled, mode='L')

        # Optional: Draw agent positions as red dots
        if agents:
            img = self._overlay_agents(img, agents)

        if filename:
            img.save(filename, 'PNG')

        return img

    def _overlay_agents(self, img, agents):
        """Draw agents as small circles on image"""
        # Implementation with PIL ImageDraw
        pass
```

### 5. Results Formatter (`results_formatter.py`)
**Minimal but Informative Output:**
```python
class ResultsFormatter:
    """Format test results into concise summaries"""

    @staticmethod
    def format_test_summary(test_run):
        """Generate summary.txt for single test"""
        summary = f"""
TEST RUN: {test_run.config['name']}
STATUS: {'PASS' if test_run.mismatch_count == 0 else 'FAIL'}

Configuration:
  Agents: {test_run.config['num_agents']}
  Trail: {test_run.config['trail_width']}×{test_run.config['trail_height']}
  VGA: {test_run.config['vga_width']}×{test_run.config['vga_height']} @{test_run.config['vga_upscale']}x
  Steps: {test_run.total_steps}
  Seed: 0x{test_run.config['seed']:08X}

Results:
  Mismatches: {test_run.mismatch_count}
  Runtime: {test_run.runtime:.1f}s
  Frame Rate: {test_run.total_steps / test_run.runtime:.1f} fps

Issues:
  {test_run.errors[:5] if test_run.errors else 'None detected'}
"""
        return summary.strip()

    @staticmethod
    def format_global_summary(all_results):
        """Generate master summary.txt"""
        pass_count = sum(1 for r in all_results if r['mismatch_count'] == 0)
        total_count = len(all_results)

        summary = f"""
COMPREHENSIVE TEST SUITE RESULTS
================================

Overall: {pass_count}/{total_count} tests passed

Test Details:
{ResultsFormatter._format_test_table(all_results)}

Errors Found: {sum(r['error_count'] for r in all_results)}
Total Runtime: {sum(r['runtime'] for r in all_results):.1f}s

Failed Tests:
{ResultsFormatter._format_failures(all_results)}

Recommendations:
{ResultsFormatter._generate_recommendations(all_results)}
"""
        return summary.strip()

    @staticmethod
    def _format_test_table(results):
        """ASCII table format"""
        lines = [
            "Name                          Status    Agents  Steps  Errors  Runtime",
            "-" * 80
        ]
        for r in results:
            status = "PASS" if r['mismatch_count'] == 0 else "FAIL"
            lines.append(
                f"{r['name']:30} {status:8} {r['num_agents']:6}  "
                f"{r['steps']:5}  {r['error_count']:6}  {r['runtime']:7.1f}s"
            )
        return "\n".join(lines)
```

---

## Execution Model

### Single Test Execution
```
for step in 1 to N:
  1. Python simulator: Execute 1 step
  2. RTL simulator: Execute 1 step
  3. Compare trails and agents
    - If mismatch: Log error details (first 5 only)
    - Save comparison JSON (step 0, step N, on errors)
  4. Generate VGA frame image (PNG)
  5. Update progress (every 100 steps)
```

### Parallel Execution
```
Main Process:
  ├─ Load test configs
  ├─ Launch up to N tests in parallel
  ├─ Monitor progress (via status files)
  ├─ Collect results as tests complete
  └─ Generate final summary

Test Process 1: test_run_001 (runs autonomously)
Test Process 2: test_run_002 (runs autonomously)
Test Process 3: test_run_003 (runs autonomously)
```

---

## Output Structure

### Per-Test Outputs
Each `test_run_XXX/` contains:

**`summary.txt`** (60 lines)
```
TEST RUN: small_100_agents
STATUS: PASS

Configuration:
  Agents: 100
  Trail: 320×240
  VGA: 640×480 @2x
  Steps: 5000

Results:
  Mismatches: 0
  Runtime: 47.3s
  Frame Rate: 105.7 fps
```

**`detailed_log.txt`** (errors only)
```
Step 42: Trail mismatch at (150, 120)
  Expected: 245, Got: 244
  Difference: -1

Step 150: Agent #5 position mismatch
  Expected: X=123.456, Y=78.910
  Got: X=123.455, Y=78.910
```

**`frames/frame_XXXX.png`** (PNG images)
- One per step (or sampled)
- Shows upscaled trail map + agent positions
- ~2-5 MB per test (300x1000 steps = 300 images)

**`comparisons/step_XXXX.json`** (JSON data)
```json
{
  "step": 42,
  "has_errors": true,
  "trail_diffs": [
    {"pos": [150, 120], "python": 245, "rtl": 244, "diff": 1}
  ],
  "agent_diffs": [
    {"agent_id": 5, "field": "x", "python": 123.456, "rtl": 123.455}
  ]
}
```

**`errors.json`** (All errors summary)
```json
{
  "total_mismatches": 5,
  "trail_errors": 3,
  "agent_errors": 2,
  "first_error_step": 42,
  "error_list": [...]
}
```

### Global Master Summary
**`tests/MASTER_SUMMARY.txt`**
```
COMPREHENSIVE TEST SUITE RESULTS
================================

Overall: 3/3 tests passed

Test Details:
Name                          Status    Agents  Steps  Errors  Runtime
default_1000_agents           PASS        1000   1000       0    54.2s
small_100_agents              PASS         100   5000       0   103.5s
high_res_500_agents           PASS         500   2000       0    78.1s

Total Runtime: 235.8s (3.9 minutes)
Total Agents Processed: 4,100,000
Average Frame Rate: 89.3 fps

All Tests Passed ✓
```

---

## Key Design Decisions

### 1. Minimal Logging
- Only log errors (first 5 per test to avoid spam)
- Save comparison data only at key points (step 0, step N, on errors)
- Progress indicator every 100 steps
- Result: Keep logs <10 MB per test

### 2. Fast Comparison
- Use NumPy for trail map diffs (vectorized)
- Agent comparison only when state actually differs
- Limit diff details to first 100 trail diffs, 20 agent diffs
- Result: Comparison overhead ~1-2% of simulation time

### 3. Image Generation
- Generate PNG for every step (visual verification)
- PNG compression keeps size manageable (2-5 MB per 1000 frames)
- Overlay agent positions for easy visual debugging
- Result: Can create video montage from frame sequence

### 4. Parallel Execution
- Run 3 tests in parallel by default (configurable)
- Each test completely autonomous (separate process)
- No inter-test dependencies
- Result: 8-hour test suite runs in ~3 hours

### 5. Long-Running Tests
- Default 1-2 hour max per test
- Tests automatically stop at timeout
- Results saved even if interrupted
- Result: Can leave running overnight safely

---

## Usage Examples

### Basic Usage
```bash
# Run with default configuration (3 tests in parallel, 2 hours each)
python tests/test_runner.py

# Run with custom config
python tests/test_runner.py --config my_tests.json --output results/

# Run single test for debugging
python tests/test_runner.py --single "small_100_agents" --verbose

# Monitor running tests
python tests/test_runner.py --monitor
```

### View Results
```bash
# Show master summary
cat tests/MASTER_SUMMARY.txt

# Show single test summary
cat tests/runs/test_run_001/summary.txt

# Show first error details
cat tests/runs/test_run_001/errors.json | jq '.first_error'

# Create video from frames
ffmpeg -framerate 30 -pattern_type glob -i 'tests/runs/test_run_001/frames/*.png' \
  -c:v libx264 -pix_fmt yuv420p output.mp4
```

---

## Implementation Phases

### Phase 1: Infrastructure (Week 1)
- [ ] Create test directory structure
- [ ] Implement test_runner.py (orchestration)
- [ ] Implement test_suite.py (base class)
- [ ] Implement results_formatter.py

### Phase 2: Comparison & Analysis (Week 2)
- [ ] Implement comparison_tools.py
- [ ] Implement image_generator.py
- [ ] Create test_config.json with 3 configurations
- [ ] Test with Python-only simulation first

### Phase 3: RTL Integration (Week 3)
- [ ] Integrate cocotb RTL simulation
- [ ] Implement RTL step execution
- [ ] Full RTL vs Python comparison
- [ ] Verify error detection works

### Phase 4: Validation & Refinement (Week 4)
- [ ] Run long-duration tests (8+ hours)
- [ ] Verify output format and sizes
- [ ] Performance optimization
- [ ] Documentation and examples

---

## Success Criteria

1. ✅ Tests run autonomously with no user interaction
2. ✅ Multiple tests run in parallel safely
3. ✅ Results stored in organized directory structure
4. ✅ Summaries are short and actionable (<100 lines)
5. ✅ Can run for 8+ hours without issues
6. ✅ Detects and reports discrepancies between RTL and Python
7. ✅ Visual frame generation for debugging
8. ✅ Can identify which step/agent/pixel caused failure
9. ✅ Frame rate: Can process 100+ fps per test
10. ✅ Memory efficient: <500 MB per running test

