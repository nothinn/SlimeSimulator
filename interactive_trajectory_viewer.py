#!/usr/bin/env python3
"""
Interactive Trajectory Viewer - Web-based visualization tool
Allows stepping through agent trajectories with Python/RTL comparison.
Uses HTML/JavaScript for interactive controls without requiring GUI libraries.
"""

import json
import csv
import math
import argparse
from pathlib import Path


def load_trajectory_csv(csv_file):
    """Load trajectory data from CSV."""
    data = []
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['step'] = int(row['step'])
            row['agent_id'] = int(row['agent_id'])
            # Convert numeric fields for trajectory_comparison_100steps.csv format
            for field in ['python_x', 'python_y', 'python_angle',
                         'rtl_x', 'rtl_y', 'rtl_angle',
                         'x_diff', 'y_diff', 'distance', 'angle_diff']:
                try:
                    row[field] = float(row[field])
                except (ValueError, KeyError):
                    row[field] = 0.0

            # Rename fields to match template expectations
            row['python_angle_deg'] = row['python_angle']
            row['rtl_angle_deg'] = row['rtl_angle']

            data.append(row)
    return data


def generate_html(csv_file, width=320, height=240, output_file='trajectory_viewer.html'):
    """Generate interactive HTML viewer for trajectories."""

    # Load CSV data
    trajectory_data = load_trajectory_csv(csv_file)

    if not trajectory_data:
        print("[Error] No data loaded from CSV")
        return None

    # Group by step
    steps_data = {}
    for row in trajectory_data:
        step = row['step']
        if step not in steps_data:
            steps_data[step] = []
        steps_data[step].append(row)

    steps = sorted(steps_data.keys())
    num_agents = len(steps_data[steps[0]]) if steps else 0

    print(f"[Viewer] Loaded {len(trajectory_data)} rows")
    print(f"[Viewer] Steps: {steps}")
    print(f"[Viewer] Agents per step: {num_agents}")

    # Convert data to JSON
    json_data = json.dumps(steps_data, indent=2)

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Agent Trajectory Viewer</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #1e1e1e;
            color: #e0e0e0;
            display: flex;
            height: 100vh;
        }}

        .container {{
            display: flex;
            width: 100%;
            gap: 20px;
            padding: 20px;
        }}

        .canvas-panel {{
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}

        canvas {{
            border: 2px solid #444;
            background: #000;
            flex: 1;
            border-radius: 4px;
        }}

        .controls-panel {{
            width: 300px;
            background: #2d2d2d;
            border-radius: 4px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 15px;
            overflow-y: auto;
        }}

        .control-section {{
            border-bottom: 1px solid #444;
            padding-bottom: 15px;
        }}

        .control-section:last-child {{
            border-bottom: none;
        }}

        h3 {{
            font-size: 14px;
            color: #61dafb;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .step-info {{
            background: #3d3d3d;
            padding: 10px;
            border-radius: 4px;
            font-size: 13px;
        }}

        .step-number {{
            font-size: 24px;
            font-weight: bold;
            color: #61dafb;
        }}

        .button-group {{
            display: flex;
            gap: 10px;
        }}

        button {{
            flex: 1;
            padding: 8px 12px;
            background: #0ea5e9;
            border: none;
            color: white;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
            transition: background 0.2s;
        }}

        button:hover {{
            background: #0284c7;
        }}

        button:active {{
            background: #0369a1;
        }}

        button:disabled {{
            background: #666;
            cursor: not-allowed;
        }}

        .checkbox-group {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}

        .checkbox-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 6px;
            border-radius: 4px;
            cursor: pointer;
            user-select: none;
        }}

        .checkbox-item:hover {{
            background: #3d3d3d;
        }}

        input[type="checkbox"] {{
            cursor: pointer;
            width: 16px;
            height: 16px;
        }}

        .label {{
            flex: 1;
            font-size: 13px;
        }}

        .color-indicator {{
            width: 12px;
            height: 12px;
            border-radius: 2px;
        }}

        .python-color {{
            background: #ff4444;
        }}

        .rtl-color {{
            background: #00ccff;
        }}

        .stats {{
            background: #3d3d3d;
            padding: 10px;
            border-radius: 4px;
            font-size: 12px;
            font-family: monospace;
            line-height: 1.6;
        }}

        .stat-row {{
            display: flex;
            justify-content: space-between;
            gap: 10px;
        }}

        .stat-label {{
            color: #aaa;
        }}

        .stat-value {{
            color: #61dafb;
            font-weight: bold;
        }}

        .keyboard-hint {{
            background: #3d3d3d;
            padding: 10px;
            border-radius: 4px;
            font-size: 12px;
            color: #aaa;
            line-height: 1.6;
        }}

        .keyboard-hint code {{
            background: #000;
            padding: 2px 4px;
            border-radius: 2px;
            color: #61dafb;
            font-family: monospace;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="canvas-panel">
            <canvas id="canvas" width="{width * 2}" height="{height * 2}"></canvas>
        </div>

        <div class="controls-panel">
            <div class="control-section">
                <h3>Step Navigation</h3>
                <div class="step-info">
                    <div class="step-number" id="stepNumber">0</div>
                    <div style="color: #aaa; font-size: 12px; margin-top: 5px;">
                        <span id="stepLabel">Step</span> / <span id="totalSteps">5</span>
                    </div>
                </div>
                <div class="button-group" style="margin-top: 10px;">
                    <button onclick="previousStep()">&larr; Previous</button>
                    <button onclick="nextStep()">Next &rarr;</button>
                </div>
            </div>

            <div class="control-section">
                <h3>Agent Display</h3>
                <div class="checkbox-group">
                    <div class="checkbox-item" onclick="togglePython()">
                        <input type="checkbox" id="showPython" checked>
                        <div class="color-indicator python-color"></div>
                        <label class="label">Show Python</label>
                    </div>
                    <div class="checkbox-item" onclick="toggleRTL()">
                        <input type="checkbox" id="showRTL" checked>
                        <div class="color-indicator rtl-color"></div>
                        <label class="label">Show RTL</label>
                    </div>
                    <div class="checkbox-item" onclick="toggleVectors()">
                        <input type="checkbox" id="showVectors" checked>
                        <div style="width: 12px; height: 12px; border: 1px solid #aaa;"></div>
                        <label class="label">Show Vectors</label>
                    </div>
                    <div class="checkbox-item" onclick="toggleSpawnCircle()">
                        <input type="checkbox" id="showSpawnCircle" checked>
                        <label class="label">Show Spawn Circle</label>
                    </div>
                </div>
            </div>

            <div class="control-section">
                <h3>Statistics</h3>
                <div class="stats">
                    <div class="stat-row">
                        <span class="stat-label">Agents:</span>
                        <span class="stat-value" id="agentCount">0</span>
                    </div>
                    <div class="stat-row">
                        <span class="stat-label">Mean X Diff:</span>
                        <span class="stat-value" id="meanXDiff">0.00</span>
                    </div>
                    <div class="stat-row">
                        <span class="stat-label">Mean Y Diff:</span>
                        <span class="stat-value" id="meanYDiff">0.00</span>
                    </div>
                    <div class="stat-row">
                        <span class="stat-label">Mean Angle Diff:</span>
                        <span class="stat-value" id="meanAngleDiff">0.00°</span>
                    </div>
                </div>
            </div>

            <div class="control-section">
                <h3>Keyboard Shortcuts</h3>
                <div class="keyboard-hint">
                    <div><code>←</code> / <code>→</code> Navigate steps</div>
                    <div><code>P</code> Toggle Python</div>
                    <div><code>R</code> Toggle RTL</div>
                    <div><code>V</code> Toggle vectors</div>
                    <div><code>C</code> Toggle circle</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const WIDTH = {width};
        const HEIGHT = {height};
        const SCALE = 2;  // Canvas scale for clarity
        const SPAWN_RADIUS = Math.min(WIDTH, HEIGHT) * 0.4;

        let trajectoryData = {json_data};
        let steps = Object.keys(trajectoryData).map(s => parseInt(s)).sort((a, b) => a - b);
        let currentStep = 0;

        let showPython = true;
        let showRTL = true;
        let showVectors = true;
        let showSpawnCircle = true;

        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');

        // Setup keyboard shortcuts
        document.addEventListener('keydown', (e) => {{
            if (e.key === 'ArrowLeft') previousStep();
            if (e.key === 'ArrowRight') nextStep();
            if (e.key.toLowerCase() === 'p') togglePython();
            if (e.key.toLowerCase() === 'r') toggleRTL();
            if (e.key.toLowerCase() === 'v') toggleVectors();
            if (e.key.toLowerCase() === 'c') toggleSpawnCircle();
        }});

        function previousStep() {{
            if (currentStep > 0) {{
                currentStep--;
                render();
            }}
        }}

        function nextStep() {{
            if (currentStep < steps.length - 1) {{
                currentStep++;
                render();
            }}
        }}

        function togglePython() {{
            showPython = !showPython;
            document.getElementById('showPython').checked = showPython;
            render();
        }}

        function toggleRTL() {{
            showRTL = !showRTL;
            document.getElementById('showRTL').checked = showRTL;
            render();
        }}

        function toggleVectors() {{
            showVectors = !showVectors;
            document.getElementById('showVectors').checked = showVectors;
            render();
        }}

        function toggleSpawnCircle() {{
            showSpawnCircle = !showSpawnCircle;
            document.getElementById('showSpawnCircle').checked = showSpawnCircle;
            render();
        }}

        function render() {{
            // Clear canvas
            ctx.fillStyle = '#000';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Draw grid
            ctx.strokeStyle = '#222';
            ctx.lineWidth = 1;
            for (let i = 0; i <= WIDTH; i += 40) {{
                ctx.beginPath();
                ctx.moveTo(i * SCALE, 0);
                ctx.lineTo(i * SCALE, HEIGHT * SCALE);
                ctx.stroke();
            }}
            for (let i = 0; i <= HEIGHT; i += 40) {{
                ctx.beginPath();
                ctx.moveTo(0, i * SCALE);
                ctx.lineTo(WIDTH * SCALE, i * SCALE);
                ctx.stroke();
            }}

            // Draw spawn circle
            if (showSpawnCircle) {{
                ctx.strokeStyle = '#444';
                ctx.lineWidth = 2;
                const cx = WIDTH / 2;
                const cy = HEIGHT / 2;
                ctx.beginPath();
                ctx.arc(cx * SCALE, cy * SCALE, SPAWN_RADIUS * SCALE, 0, 2 * Math.PI);
                ctx.stroke();
            }}

            // Get current step data
            const stepNum = steps[currentStep];
            const agents = trajectoryData[stepNum] || [];

            // Calculate statistics
            let sumXDiff = 0, sumYDiff = 0, sumAngleDiff = 0;
            let validCount = 0;

            // Draw agents
            agents.forEach(agent => {{
                const py_x = parseFloat(agent.python_x);
                const py_y = parseFloat(agent.python_y);
                const py_angle = parseFloat(agent.python_angle_deg);

                const rtl_x = agent.rtl_x ? parseFloat(agent.rtl_x) : null;
                const rtl_y = agent.rtl_y ? parseFloat(agent.rtl_y) : null;
                const rtl_angle = agent.rtl_angle_deg ? parseFloat(agent.rtl_angle_deg) : null;

                // Draw Python agent
                if (showPython && py_x !== null && py_y !== null) {{
                    ctx.fillStyle = '#ff4444';
                    ctx.beginPath();
                    ctx.arc(py_x * SCALE, py_y * SCALE, 4, 0, 2 * Math.PI);
                    ctx.fill();

                    // Draw vector
                    if (showVectors) {{
                        const rad = py_angle * Math.PI / 180;
                        const vlen = 15;
                        const vx = Math.cos(rad) * vlen;
                        const vy = Math.sin(rad) * vlen;

                        ctx.strokeStyle = '#ff4444';
                        ctx.lineWidth = 1;
                        ctx.beginPath();
                        ctx.moveTo(py_x * SCALE, py_y * SCALE);
                        ctx.lineTo((py_x + vx/SCALE) * SCALE, (py_y + vy/SCALE) * SCALE);
                        ctx.stroke();
                    }}
                }}

                // Draw RTL agent (colored by error magnitude)
                if (showRTL && rtl_x !== null && rtl_y !== null) {{
                    // Color by error magnitude: green=0, red=100+
                    const distance = parseFloat(agent.distance) || 0;
                    let color = '#00ccff';  // default cyan
                    if (distance > 0) {{
                        if (distance < 20) color = '#7fff00';     // lime-green
                        else if (distance < 40) color = '#ffff00';  // yellow
                        else if (distance < 60) color = '#ff7f00';  // orange
                        else color = '#ff0000';                     // red
                    }}

                    ctx.fillStyle = color;
                    ctx.beginPath();
                    ctx.rect(rtl_x * SCALE - 3, rtl_y * SCALE - 3, 6, 6);
                    ctx.fill();

                    // Draw vector
                    if (showVectors) {{
                        const rad = rtl_angle * Math.PI / 180;
                        const vlen = 15;
                        const vx = Math.cos(rad) * vlen;
                        const vy = Math.sin(rad) * vlen;

                        ctx.strokeStyle = color;
                        ctx.lineWidth = 1;
                        ctx.beginPath();
                        ctx.moveTo(rtl_x * SCALE, rtl_y * SCALE);
                        ctx.lineTo((rtl_x + vx/SCALE) * SCALE, (rtl_y + vy/SCALE) * SCALE);
                        ctx.stroke();
                    }}
                }}

                // Calculate stats
                if (rtl_x !== null && rtl_y !== null && rtl_angle !== null) {{
                    const xDiff = Math.abs(py_x - rtl_x);
                    const yDiff = Math.abs(py_y - rtl_y);
                    const angleDiff = Math.abs(py_angle - rtl_angle);

                    sumXDiff += xDiff;
                    sumYDiff += yDiff;
                    sumAngleDiff += angleDiff;
                    validCount++;
                }}
            }});

            // Update UI
            document.getElementById('stepNumber').textContent = stepNum;
            document.getElementById('stepLabel').textContent = `Step ${{stepNum}}`;
            document.getElementById('totalSteps').textContent = steps.length;
            document.getElementById('agentCount').textContent = agents.length;

            if (validCount > 0) {{
                document.getElementById('meanXDiff').textContent = (sumXDiff / validCount).toFixed(2);
                document.getElementById('meanYDiff').textContent = (sumYDiff / validCount).toFixed(2);
                document.getElementById('meanAngleDiff').textContent = (sumAngleDiff / validCount).toFixed(2) + '°';
            }}
        }}

        // Initial render
        render();
    </script>
</body>
</html>
"""

    with open(output_file, 'w') as f:
        f.write(html_content)

    print(f"[Viewer] ✓ Generated {output_file}")
    return output_file


def main():
    parser = argparse.ArgumentParser(description='Generate interactive trajectory viewer')
    parser.add_argument('csv_file', help='CSV file with trajectory data')
    parser.add_argument('--output', default='trajectory_viewer.html', help='Output HTML file')
    parser.add_argument('--width', type=int, default=320, help='Canvas width')
    parser.add_argument('--height', type=int, default=240, help='Canvas height')

    args = parser.parse_args()

    html_file = generate_html(args.csv_file, args.width, args.height, args.output)

    if html_file:
        print(f"\n{'='*70}")
        print(f"✓ Interactive viewer created: {html_file}")
        print(f"{'='*70}")
        print(f"\nUsage:")
        print(f"  Open in browser: open {html_file}")
        print(f"  Or: xdg-open {html_file}  (Linux)")
        print(f"\nFeatures:")
        print(f"  • Step through trajectories with ← / → buttons or arrow keys")
        print(f"  • Toggle Python/RTL agents and vectors")
        print(f"  • View real-time statistics")
        print(f"  • Keyboard shortcuts: P/R/V/C for toggles")
    else:
        print("[Error] Failed to create viewer")
        return 1

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
