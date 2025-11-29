# Agent Trajectory Visualizer - Quick Start

## 30-Second Start

```bash
# Activate environment
source .venv/bin/activate

# Run visualizer
python3 agent_trajectory_visualizer.py

# Or with custom file
python3 agent_trajectory_visualizer.py path/to/data.csv
```

## Controls

| Action | Method |
|--------|--------|
| Previous frame | ◄ Button or Left Arrow |
| Next frame | ► Button or Right Arrow |
| Toggle Python agents | Checkbox "Show Python" |
| Toggle RTL agents | Checkbox "Show RTL" |
| Toggle vectors | Checkbox "Show Vectors" |
| Toggle spawn circle | Checkbox "Spawn Circle" |
| Quit | Close window or press Q |

## Color Code

- **Red circles** = Python agents
- **Orange arrows** = Python direction vectors
- **Cyan squares** = RTL agents
- **Blue arrows** = RTL direction vectors
- **Gray dashed circle** = Spawn pattern

## Files

- `agent_trajectory_visualizer.py` - Main tool
- `VISUALIZER_README.md` - Full documentation
- `VISUALIZER_SUMMARY.md` - Technical summary
- `agent_comparison.csv` - Example data (100 agents)

## Test Without GUI

```bash
source .venv/bin/activate
python3 test_visualizer.py
```

## Generate Multi-Step Example

```bash
source .venv/bin/activate
python3 generate_trajectory_example.py --agents 50 --steps 20
python3 agent_trajectory_visualizer.py example_trajectory.csv
```

## Common Issues

**Q: ModuleNotFoundError: No module named 'numpy'**
A: Run `source .venv/bin/activate` first

**Q: Navigation buttons disabled**
A: This is single-step data (initialization only)

**Q: Large angle differences (359°+)**
A: Wraparound issue in CSV data, not visualizer bug

## Example Output

```
Loaded 100 agents from agent_comparison.csv
Single-step initialization data
Number of agents: 100

Visualization state:
  Canvas: 320x240
  Spawn radius: 96.00
  Mean position difference: 3.004 px
  Max position difference: 4.359 px
```

## Help

```bash
python3 agent_trajectory_visualizer.py --help
```

See `VISUALIZER_README.md` for detailed documentation.
