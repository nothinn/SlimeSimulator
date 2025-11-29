# Agent Trajectory Visualizer

Interactive Python tool for analyzing and comparing agent trajectories between Python reference implementation and RTL simulation.

## Features

- **Interactive stepping** through simulation frames (if multi-step data available)
- **Toggle visibility** for Python/RTL agents, vectors, and spawn circle
- **Vector visualization** showing agent direction and angle
- **Statistics panel** with position/angle differences and metrics
- **Keyboard shortcuts** for quick navigation
- **Spawn circle overlay** showing initialization pattern

## Requirements

- Python 3.6+
- numpy
- matplotlib

Activate the project virtual environment:
```bash
source .venv/bin/activate
```

## Usage

### Basic Usage

```bash
# Use default file (agent_comparison.csv in current directory)
python3 agent_trajectory_visualizer.py

# Specify a different CSV file
python3 agent_trajectory_visualizer.py path/to/agent_data.csv

# Custom canvas dimensions
python3 agent_trajectory_visualizer.py --width 640 --height 480 agent_data.csv
```

### Input CSV Format

The visualizer expects CSV files with the following columns:

**Single-step initialization data:**
```
Agent,Python_X,Python_Y,Python_Angle_Deg,RTL_X,RTL_Y,RTL_Angle_Deg,X_Diff,Y_Diff,Angle_Diff
0,253.0,120.0,180.00,256.0,120.0,179.99,3.00,0.00,0.01
1,252.0,125.0,183.60,255.8,126.0,183.58,3.81,1.03,0.01
...
```

**Multi-step trajectory data (future):**
```
Step,Agent,Python_X,Python_Y,Python_Angle_Deg,RTL_X,RTL_Y,RTL_Angle_Deg,X_Diff,Y_Diff,Angle_Diff
0,0,253.0,120.0,180.00,256.0,120.0,179.99,3.00,0.00,0.01
0,1,252.0,125.0,183.60,255.8,126.0,183.58,3.81,1.03,0.01
1,0,254.0,121.0,181.00,257.0,121.0,180.98,3.01,0.01,0.02
...
```

## Interactive Controls

### Buttons
- **◄ Previous Step** - Navigate to previous frame (if multi-step data)
- **Next Step ►** - Navigate to next frame (if multi-step data)

### Checkboxes
- **Show Python** - Toggle Python agent visibility (red circles + orange vectors)
- **Show RTL** - Toggle RTL agent visibility (cyan squares + blue vectors)
- **Show Vectors** - Toggle direction vectors on/off
- **Spawn Circle** - Toggle spawn pattern circle overlay

### Keyboard Shortcuts
- **Left Arrow** - Previous step
- **Right Arrow** - Next step
- **Q** - Quit visualization

## Visualization Elements

### Color Scheme
| Element | Color | Marker |
|---------|-------|--------|
| Python agents | Red | Circle (o) |
| Python vectors | Orange | Arrow |
| RTL agents | Cyan | Square (s) |
| RTL vectors | Blue | Arrow |
| Spawn circle | Gray | Dashed line |

### Information Panel

The right panel displays:

- **Simulation Info:** Canvas size, agent count, current step
- **Spawn Pattern:** Circle radius and center position
- **Position Differences:** Mean/max X/Y differences and Euclidean distances
- **Angle Differences:** Mean/max angular differences between Python and RTL
- **Controls:** Quick reference for keyboard shortcuts

### Canvas Layout

- **Origin:** Top-left corner (0, 0)
- **Coordinate System:** Screen coordinates (Y-axis inverted)
- **Grid:** Enabled with 0.3 alpha for reference
- **Spawn Circle:** Centered at (width/2, height/2) with radius = 40% of min(width, height)

## Example Session

```bash
# Activate virtual environment
source .venv/bin/activate

# Run visualizer with default settings
python3 agent_trajectory_visualizer.py

# The visualization window will open showing:
# - 100 agents (initialization data from agent_comparison.csv)
# - Python agents (red circles) vs RTL agents (cyan squares)
# - Direction vectors (orange/blue arrows)
# - Spawn circle (gray dashed circle at center)
# - Statistics panel on the right

# Use checkboxes to toggle visibility
# - Uncheck "Show Python" to see only RTL agents
# - Uncheck "Show Vectors" to see only positions
# - Uncheck "Spawn Circle" to hide the spawn pattern

# Close window or press 'Q' to exit
```

## Testing

A test script is provided to verify the visualizer without displaying the GUI:

```bash
source .venv/bin/activate
python3 test_visualizer.py
```

This will:
- Load the agent_comparison.csv file
- Initialize the visualizer
- Print statistics and data ranges
- Verify all components are working correctly

## Expected Output (agent_comparison.csv)

When loading the default `agent_comparison.csv` file (100 agents, 320×240 canvas):

```
Loaded 100 agents from agent_comparison.csv
Single-step initialization data
Number of agents: 100

Visualization state:
  Current step: 0
  Total steps: 1
  Number of agents: 100
  Canvas size: 320x240
  Spawn radius: 96.00

Python agent data:
  X range: [67.00, 253.00]
  Y range: [27.00, 213.00]
  Angle range: [0.00, 356.41]

RTL agent data:
  X range: [64.00, 256.00]
  Y range: [24.00, 216.00]
  Angle range: [3.59, 359.97]

Differences:
  Mean X diff: 1.905 px
  Mean Y diff: 1.905 px
  Mean Euclidean distance: 3.004 px
  Max Euclidean distance: 4.359 px
```

## Known Issues

### Angle Wraparound
Some agents may show large angle differences (e.g., 359.97°) due to wraparound at 360°. For example:
- Python angle: 0.00°
- RTL angle: 359.97°
- Reported difference: 359.97° (actual difference is ~0.03°)

This is a data generation issue in the CSV, not a visualizer bug. The actual angle difference is small (0.03°), but the wraparound calculation shows 359.97°.

## Future Enhancements

- **Multi-step trajectory playback** - Animate agent movement over time
- **Agent selection/hover** - Click agents to see detailed info
- **Difference heatmap** - Color-code agents by position/angle error
- **Export frames** - Save visualization as PNG/GIF
- **Zoom/pan** - Interactive canvas navigation
- **Trail visualization** - Show agent paths over time
- **Side-by-side comparison** - Separate Python/RTL canvases

## Tips

1. **Single-step data:** The default `agent_comparison.csv` contains only initialization data (step 0). Navigation buttons are disabled for single-step data.

2. **Large datasets:** For files with many agents, consider:
   - Disabling vectors for better performance
   - Using subset of agents for initial analysis
   - Increasing figure size for better visibility

3. **Custom analysis:** The visualizer can be imported and extended:
   ```python
   from agent_trajectory_visualizer import AgentTrajectoryVisualizer

   viz = AgentTrajectoryVisualizer('my_data.csv', width=640, height=480)
   # Customize viz.show_python, viz.show_rtl, etc.
   viz.draw_frame()
   viz.show()
   ```

## Troubleshooting

**ModuleNotFoundError: No module named 'numpy'**
- Solution: Activate virtual environment: `source .venv/bin/activate`

**FileNotFoundError: agent_comparison.csv**
- Solution: Specify full path to CSV file or run from correct directory

**No display/GUI errors in headless environment**
- Solution: Use test script (`python3 test_visualizer.py`) or set matplotlib backend to 'Agg'

## Related Files

- `agent_trajectory_visualizer.py` - Main visualizer script
- `test_visualizer.py` - Test harness (no GUI)
- `agent_comparison.csv` - Example input data (100 agents, initialization)
- `VISUALIZER_README.md` - This documentation

## License

Part of the SlimeSimulator project. See project root for license information.
