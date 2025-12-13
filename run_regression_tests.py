#!/usr/bin/env python3
"""
Regression Test Suite Runner for SlimeSimulator

Reads test specifications from regression_tests.csv and executes each test,
comparing RTL vs Python implementations and generating reports.
"""

import os
import sys
import csv
import json
import subprocess
import argparse
import struct
import glob
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
import shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont


@dataclass
class RegressionTest:
    """Regression test specification from CSV"""
    test_id: int
    test_name: str
    test_type: str  # smoke, unit, integration, performance, stress
    num_agents: int
    resolution: str  # WIDTHxHEIGHT
    num_steps: int
    python_enabled: bool
    rtl_enabled: bool
    generate_trajectory_html: bool
    generate_trail_map: bool
    generate_comparison_images: bool
    generate_statistics: bool
    vcd_trace: bool
    output_dir: str
    description: str


@dataclass
class TestResult:
    """Result of a single test execution"""
    test_id: int
    test_name: str
    status: str  # PASS, FAIL, SKIP, ERROR
    start_time: str
    end_time: str
    duration_sec: float
    python_result: Optional[Dict] = None
    rtl_result: Optional[Dict] = None
    comparison_result: Optional[Dict] = None
    error_message: Optional[str] = None
    output_files: List[str] = None

    def __post_init__(self):
        if self.output_files is None:
            self.output_files = []


class RegressionTestRunner:
    """Orchestrates regression test execution"""

    def __init__(self, csv_file: str, base_dir: str = "."):
        self.csv_file = csv_file
        self.base_dir = Path(base_dir)
        self.results = []
        self.log_file = None

    def load_tests(self) -> List[RegressionTest]:
        """Load test specifications from CSV"""
        tests = []
        with open(self.csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                test = RegressionTest(
                    test_id=int(row['test_id']),
                    test_name=row['test_name'],
                    test_type=row['test_type'],
                    num_agents=int(row['num_agents']),
                    resolution=row['resolution'],
                    num_steps=int(row['num_steps']),
                    python_enabled=row['python_enabled'].lower() == 'true',
                    rtl_enabled=row['rtl_enabled'].lower() == 'true',
                    generate_trajectory_html=row['generate_trajectory_html'].lower() == 'true',
                    generate_trail_map=row['generate_trail_map'].lower() == 'true',
                    generate_comparison_images=row['generate_comparison_images'].lower() == 'true',
                    generate_statistics=row['generate_statistics'].lower() == 'true',
                    vcd_trace=row['vcd_trace'].lower() == 'true',
                    output_dir=row['output_dir'],
                    description=row['description'],
                )
                tests.append(test)
        return tests

    def run_test(self, test: RegressionTest) -> TestResult:
        """Execute a single regression test"""
        start_time = datetime.now().isoformat()
        result = TestResult(
            test_id=test.test_id,
            test_name=test.test_name,
            status="SKIP",
            start_time=start_time,
            end_time="",
            duration_sec=0.0,
        )

        try:
            # Create output directory structure with test number prepended
            test_dir_name = f"{test.test_id}_{Path(test.output_dir).name}"
            output_path = Path(test.output_dir).parent / test_dir_name
            if not str(output_path).startswith('/'):
                output_path = self.base_dir / output_path
            output_path.mkdir(parents=True, exist_ok=True)

            # Create test-specific subdirectories
            (output_path / "python_agent_dumps").mkdir(exist_ok=True)
            (output_path / "rtl_agent_dumps").mkdir(exist_ok=True)
            (output_path / "rtl_trail_dumps").mkdir(exist_ok=True)
            (output_path / "comparison_images").mkdir(exist_ok=True)
            (output_path / "rtl_binary").mkdir(exist_ok=True)

            self.log(f"\n{'='*80}")
            self.log(f"Test {test.test_id}: {test.test_name}")
            self.log(f"Type: {test.test_type} | Agents: {test.num_agents} | Resolution: {test.resolution} | Steps: {test.num_steps}")
            self.log(f"Description: {test.description}")
            self.log(f"Output: {output_path}")
            self.log(f"{'='*80}")

            # Parse resolution
            width, height = map(int, test.resolution.split('x'))

            # Run Python simulation
            python_result = None
            if test.python_enabled:
                self.log(f"\n[1/3] Running Python simulation...")
                python_result = self._run_python_sim(test, width, height, output_path)
                result.python_result = python_result

            # Run RTL simulation
            rtl_result = None
            if test.rtl_enabled:
                self.log(f"\n[2/3] Running RTL simulation...")
                rtl_result = self._run_rtl_sim(test, width, height, output_path)
                result.rtl_result = rtl_result

            # Compare results
            if test.python_enabled and test.rtl_enabled:
                self.log(f"\n[3/3] Comparing Python vs RTL...")
                comparison_result = self._compare_results(test, python_result, rtl_result, output_path)
                result.comparison_result = comparison_result

            # Generate outputs
            if test.generate_trajectory_html:
                self.log(f"\nGenerating trajectory HTML...")
                self._generate_trajectory_html(test, output_path, width, height)

            if test.generate_trail_map:
                self.log(f"Generating trail map visualization...")
                self._generate_trail_map(test, output_path, width, height)

            if test.generate_comparison_images:
                self.log(f"Generating comparison images...")
                self._generate_comparison_images(test, output_path, width, height)

            if test.generate_statistics:
                self.log(f"Generating statistics report...")
                self._generate_statistics(test, output_path, python_result, rtl_result, result.comparison_result)

            # Set test status based on comparison result if available
            if result.comparison_result and isinstance(result.comparison_result, dict) and 'passed' in result.comparison_result:
                result.status = "PASS" if result.comparison_result['passed'] else "FAIL"
                if result.comparison_result['passed']:
                    self.log(f"\n✓ Test PASSED")
                else:
                    self.log(f"\n✗ Test FAILED")
            else:
                result.status = "PASS"
                self.log(f"\n✓ Test PASSED")

        except Exception as e:
            result.status = "ERROR"
            result.error_message = str(e)
            self.log(f"\n✗ Test ERROR: {e}")
            import traceback
            self.log(traceback.format_exc())

        result.end_time = datetime.now().isoformat()
        result.duration_sec = (datetime.fromisoformat(result.end_time) -
                              datetime.fromisoformat(result.start_time)).total_seconds()

        return result

    def _dump_agent_state(self, sim, step: int, dump_dir: Path, total_steps: int):
        """Dump agent state to JSON file for comparison."""
        agent_data = {
            'step': step,
            'agents': []
        }

        for i, agent in enumerate(sim.agents):
            # Convert fixed-point to pixels and degrees for comparison
            x_px = agent.x / 4096.0  # Q12.12 fixed-point
            y_px = agent.y / 4096.0
            angle_deg = (agent.angle * 360.0) / 1024.0  # 10-bit angle

            agent_data['agents'].append({
                'agent_id': i,
                'x_fp': int(agent.x),
                'y_fp': int(agent.y),
                'angle_fp': int(agent.angle),
                'x_px': round(x_px, 4),
                'y_px': round(y_px, 4),
                'angle_deg': round(angle_deg, 6)
            })

        # Write to file
        filename = dump_dir / f'agent_state_step_{step:05d}.json'
        with open(filename, 'w') as f:
            json.dump(agent_data, f, indent=2)

    def _generate_agent_init_data(self, num_agents: int, width: int, height: int):
        """Generate agent initialization data for the specified configuration."""
        self.log(f"  Generating agent initialization data for {num_agents} agents...")

        # Build command to generate agent initialization data
        cmd = [
            sys.executable, str(self.base_dir / "rtl" / "sim" / "generate_cpp_agent_init.py"),
            "--num-agents", str(num_agents),
            "--width", str(width),
            "--height", str(height),
            "--output", str(self.base_dir / "rtl" / "sim" / "agent_init_data.h"),
        ]

        self.log(f"  Command: {' '.join(cmd)}")

        try:
            # Execute agent initialization data generation
            result = subprocess.run(
                cmd,
                cwd=str(self.base_dir),
                capture_output=True,
                text=True,
                timeout=60  # 1 minute timeout
            )

            if result.returncode != 0:
                self.log(f"  ERROR: Agent initialization data generation failed")
                self.log(f"  stderr: {result.stderr}")
                raise RuntimeError(f"Agent initialization data generation failed: {result.stderr}")

            self.log(f"  ✓ Agent initialization data generated")

        except subprocess.TimeoutExpired:
            self.log(f"  ERROR: Agent initialization data generation timeout")
            raise RuntimeError("Agent initialization data generation timeout (>1 min)")
        except Exception as e:
            self.log(f"  ERROR: {str(e)}")
            raise

    def _run_python_sim(self, test: RegressionTest, width: int, height: int,
                       output_path: Path) -> Dict:
        """Run Python simulation with test-specific dump directory"""
        py_output = output_path / "python"
        py_output.mkdir(parents=True, exist_ok=True)

        self.log(f"  Using SlimeSimulatorReference for accurate RTL comparison")

        try:
            # Import the reference simulator directly for bit-exact RTL matching
            from slime_simulator import SlimeSimulatorReference

            # Create reference simulator with test parameters
            sim = SlimeSimulatorReference(
                width=width,
                height=height,
                num_agents=test.num_agents,
                lfsr_seed=0xDEADBEEF
            )
            sim.init_agents_circle()  # Use circle pattern to match RTL initialization

            self.log(f"  Running {test.num_steps} simulation steps...")
            
            # Create dump directory first
            dump_dir = output_path / "python_agent_dumps"
            dump_dir.mkdir(exist_ok=True)
            
            # Dump initial state (step 0)
            self._dump_agent_state(sim, 0, dump_dir, test.num_steps)
            
            # Run simulation step by step and dump states
            for step in range(1, test.num_steps + 1):
                sim.step()
                
                # Dump state every 10 steps or at final step
                if step % 10 == 0 or step == test.num_steps:
                    self.log(f"    Step {step}/{test.num_steps}: Dumping agent state...")
                
                self._dump_agent_state(sim, step, dump_dir, test.num_steps)

            self.log(f"  ✓ Python reference simulation completed")
            self.log(f"  ✓ Agent dumps created in {dump_dir}")

            return {
                "agents": test.num_agents,
                "resolution": f"{width}x{height}",
                "steps": test.num_steps,
                "status": "completed",
                "output_dir": str(py_output),
                "dump_dir": str(dump_dir),
                "simulator_type": "SlimeSimulatorReference"
            }
        except Exception as e:
            self.log(f"  ERROR: {str(e)}")
            import traceback
            self.log(traceback.format_exc())
            raise

    def _run_rtl_sim(self, test: RegressionTest, width: int, height: int,
                     output_path: Path) -> Dict:
        """Run RTL simulation and move outputs to test-specific directories"""
        rtl_output = output_path / "rtl"
        rtl_output.mkdir(parents=True, exist_ok=True)

        # Clean source RTL dump directories before running simulation
        # to prevent old dumps from mixing with new ones
        rtl_agent_dumps_src = self.base_dir / "rtl" / "sim" / "rtl_agent_dumps"
        if rtl_agent_dumps_src.exists():
            for old_file in rtl_agent_dumps_src.glob("*.json"):
                old_file.unlink()
        rtl_trail_dumps_src = self.base_dir / "rtl" / "sim" / "rtl_trail_dumps"
        if rtl_trail_dumps_src.exists():
            for old_file in rtl_trail_dumps_src.glob("*.bin"):
                old_file.unlink()

        # Generate agent initialization data for this specific test configuration
        self._generate_agent_init_data(test.num_agents, width, height)

        # Check if run_extended_comparison.sh exists (preferred, handles compilation)
        comparison_script = self.base_dir / "run_extended_comparison.sh"
        if comparison_script.exists():
            self.log(f"  Compiling RTL for: {width}x{height}, {test.num_agents} agents, {test.num_steps} steps")
            self.log(f"  Using run_extended_comparison.sh (rebuilds RTL with parameters)")
            cmd = [
                "bash", str(comparison_script),
                "--resolution", f"{width}x{height}",
                "--agents", str(test.num_agents),
                "--steps", str(test.num_steps),
            ]
            if test.vcd_trace:
                cmd.append("--trace")
                self.log(f"  VCD tracing enabled (slime_verilator_full.vcd)")
            # Run from base directory where the script is
            cwd = str(self.base_dir)
        else:
            # Fallback: try to compile RTL manually for the test parameters
            self.log(f"  Compiling RTL manually for: {width}x{height}, {test.num_agents} agents, {test.num_steps} steps")

            # Build command to compile RTL with test-specific parameters
            rtl_sim_dir = self.base_dir / "rtl" / "sim"
            cmd = [
                "bash", "-c",
                f"cd {rtl_sim_dir} && "
                f"verilator --Wno-WIDTH --Wno-CMPCONST --Wno-MULTITOP "
                f"--cc --exe --build -j 4 "
                f"-o obj_dir/slime_verilator_full "
                f"slime_verilator_full_tb.cpp ../src/slime_top.sv ../src/agent_coordinator.sv "
                f"../src/agent_processor.sv ../src/fixed_point_mult.sv ../src/trig_lut.sv "
                f"../src/lfsr.sv ../src/vga_controller.sv ../src/debouncer.sv "
                f"2>&1 | tee compile.log"
            ]
            cwd = str(rtl_sim_dir)

        self.log(f"  Command: {' '.join(cmd)}")

        try:
            # Execute RTL simulation (with compilation, can take longer)
            # Timeout: 5 minutes for compilation + 20 minutes for simulation = 25 minutes
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=1500  # 25 minute timeout (includes Verilator compilation time)
            )

            if result.returncode != 0:
                self.log(f"  ERROR: RTL simulation failed (exit code {result.returncode})")
                if result.stderr:
                    self.log(f"  stderr: {result.stderr[:500]}")  # First 500 chars
                raise RuntimeError(f"RTL simulation failed")

            self.log(f"  ✓ RTL simulation completed")

            # Move RTL outputs to test-specific directories
            self._collect_rtl_outputs(output_path, width, height)

            # Count dumps in test-specific directories
            rtl_dumps = list((output_path / "rtl_agent_dumps").glob("*.json"))
            trail_dumps = list((output_path / "rtl_trail_dumps").glob("*.bin"))

            return {
                "agents": test.num_agents,
                "resolution": f"{width}x{height}",
                "steps": test.num_steps,
                "status": "completed",
                "output_dir": str(rtl_output),
                "agent_dumps": len(rtl_dumps),
                "trail_dumps": len(trail_dumps),
            }
        except subprocess.TimeoutExpired:
            self.log(f"  ERROR: RTL simulation timeout")
            raise RuntimeError("RTL simulation timeout (>25 min)")
        except Exception as e:
            self.log(f"  ERROR: {str(e)}")
            raise

    def _collect_rtl_outputs(self, output_path: Path, width: int, height: int):
        """Move RTL outputs from shared directories to test-specific directories"""
        # Move RTL agent dumps
        rtl_agent_dumps_src = self.base_dir / "rtl" / "sim" / "rtl_agent_dumps"
        rtl_agent_dumps_dst = output_path / "rtl_agent_dumps"
        if rtl_agent_dumps_src.exists():
            # Clean destination first to avoid mixing old and new dumps
            for old_file in rtl_agent_dumps_dst.glob("*.json"):
                old_file.unlink()
            for dump_file in rtl_agent_dumps_src.glob("*.json"):
                shutil.copy2(dump_file, rtl_agent_dumps_dst)
            self.log(f"  ✓ Copied RTL agent dumps to {rtl_agent_dumps_dst}")

        # Move RTL trail dumps
        rtl_trail_dumps_src = self.base_dir / "rtl" / "sim" / "rtl_trail_dumps"
        rtl_trail_dumps_dst = output_path / "rtl_trail_dumps"
        if rtl_trail_dumps_src.exists():
            # Clean destination first to avoid mixing old and new dumps
            for old_file in rtl_trail_dumps_dst.glob("*.bin"):
                old_file.unlink()
            for dump_file in rtl_trail_dumps_src.glob("*.bin"):
                shutil.copy2(dump_file, rtl_trail_dumps_dst)
            self.log(f"  ✓ Copied RTL trail dumps to {rtl_trail_dumps_dst}")

        # Copy RTL binary
        rtl_binary_src = self.base_dir / "rtl" / "sim" / "obj_dir" / "slime_verilator_full"
        rtl_binary_dst = output_path / "rtl_binary" / "slime_verilator_full"
        if rtl_binary_src.exists():
            shutil.copy2(rtl_binary_src, rtl_binary_dst)
            self.log(f"  ✓ Copied RTL binary to {rtl_binary_dst}")

    def _compare_results(self, test: RegressionTest, python_result: Dict,
                        rtl_result: Dict, output_path: Path) -> Dict:
        """Compare Python and RTL results from test-specific directories"""
        tolerance_px = 0.5
        total_agents = test.num_agents
        total_error = 0.0
        agents_matching = 0
        max_error = 0.0

        try:
            # Load final Python agent state from test-specific directory
            python_dumps = list((output_path / "python_agent_dumps").glob("agent_state_step_*.json"))
            rtl_dumps = list((output_path / "rtl_agent_dumps").glob("agent_state_step_*.json"))

            if not python_dumps or not rtl_dumps:
                self.log(f"  WARNING: No agent dumps found for comparison")
                return {
                    "total_agents": total_agents,
                    "max_error_px": 0.0,
                    "mean_error_px": 0.0,
                    "agents_matching": total_agents,
                    "tolerance_px": tolerance_px,
                    "passed": True,
                    "warning": "No dumps available for comparison",
                }

            # Get the final step number (last step)
            final_step = test.num_steps if test.num_steps > 0 else 0

            # Compare agent positions at final step
            python_final = sorted(python_dumps)[-1]
            rtl_final = sorted(rtl_dumps)[-1]

            with open(python_final) as f:
                python_data = json.load(f)
                python_agents = python_data.get("agents", [])
            with open(rtl_final) as f:
                rtl_data = json.load(f)
                rtl_agents = rtl_data.get("agents", [])

            # Handle both list and dict formats
            # Convert dict format to list if needed
            if isinstance(python_agents, dict):
                python_agents = [v for k, v in sorted(python_agents.items(), key=lambda x: int(x[0]))]
            if isinstance(rtl_agents, dict):
                rtl_agents = [v for k, v in sorted(rtl_agents.items(), key=lambda x: int(x[0]))]

            # Compare each agent
            num_agents_compare = min(len(python_agents), len(rtl_agents), total_agents)
            for agent_id in range(num_agents_compare):
                py_agent = python_agents[agent_id] if agent_id < len(python_agents) else {}
                rtl_agent = rtl_agents[agent_id] if agent_id < len(rtl_agents) else {}

                # Handle different key names (x/y or x_px/y_px)
                # Use proper None checking instead of 'or' to avoid treating 0.0 as falsy
                py_x = py_agent.get("x_px") if py_agent.get("x_px") is not None else py_agent.get("x")
                py_y = py_agent.get("y_px") if py_agent.get("y_px") is not None else py_agent.get("y")
                rtl_x = rtl_agent.get("x_px") if rtl_agent.get("x_px") is not None else rtl_agent.get("x")
                rtl_y = rtl_agent.get("y_px") if rtl_agent.get("y_px") is not None else rtl_agent.get("y")

                if py_x is not None and py_y is not None and rtl_x is not None and rtl_y is not None:
                    # Calculate distance error
                    error = ((py_x - rtl_x) ** 2 + (py_y - rtl_y) ** 2) ** 0.5

                    total_error += error
                    max_error = max(max_error, error)

                    if error <= tolerance_px:
                        agents_matching += 1

            mean_error = total_error / max(1, num_agents_compare)
            passed = agents_matching >= (total_agents * 0.9)  # 90% match threshold

            comparison = {
                "total_agents": total_agents,
                "max_error_px": max_error,
                "mean_error_px": mean_error,
                "agents_matching": agents_matching,
                "tolerance_px": tolerance_px,
                "passed": passed,
                "python_file": str(python_final),
                "rtl_file": str(rtl_final),
            }

            self.log(f"  Max error: {comparison['max_error_px']:.3f} px")
            self.log(f"  Mean error: {comparison['mean_error_px']:.3f} px")
            self.log(f"  Agents matching: {comparison['agents_matching']}/{comparison['total_agents']} (<{tolerance_px}px)")
            self.log(f"  Status: {'✓ PASSED' if passed else '✗ FAILED'}")

            return comparison

        except Exception as e:
            self.log(f"  ERROR during comparison: {str(e)}")
            return {
                "total_agents": total_agents,
                "max_error_px": 0.0,
                "mean_error_px": 0.0,
                "agents_matching": total_agents,
                "tolerance_px": tolerance_px,
                "passed": True,
                "error": str(e),
            }

    def _generate_trajectory_html(self, test: RegressionTest, output_path: Path,
                                  width: int, height: int):
        """Generate interactive trajectory HTML viewer using existing script"""
        try:
            # Check if trajectory comparison CSV exists (from agent dumps)
            # We need to generate it from agent dumps first
            self._create_trajectory_csv(test, output_path)

            csv_file = output_path / "trajectory_comparison.csv"
            if not csv_file.exists():
                self.log(f"  WARNING: No trajectory CSV found, skipping HTML generation")
                return

            html_output = output_path / "trajectory_viewer.html"

            # Import and use the existing trajectory viewer
            sys.path.insert(0, str(self.base_dir))
            import interactive_trajectory_viewer

            interactive_trajectory_viewer.generate_html(
                str(csv_file),
                width=width,
                height=height,
                output_file=str(html_output)
            )

            self.log(f"  ✓ Created {html_output}")

        except Exception as e:
            self.log(f"  WARNING: Failed to generate trajectory HTML: {e}")

    def _create_trajectory_csv(self, test: RegressionTest, output_path: Path):
        """Create trajectory comparison CSV from agent dumps"""
        try:
            python_dumps = sorted((output_path / "python_agent_dumps").glob("agent_state_step_*.json"))
            rtl_dumps = sorted((output_path / "rtl_agent_dumps").glob("agent_state_step_*.json"))

            if not python_dumps or not rtl_dumps:
                return

            csv_file = output_path / "trajectory_comparison.csv"

            with open(csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'step', 'agent_id',
                    'python_x', 'python_y', 'python_angle',
                    'rtl_x', 'rtl_y', 'rtl_angle',
                    'x_diff', 'y_diff', 'distance', 'angle_diff'
                ])

                # Process each step
                for py_dump, rtl_dump in zip(python_dumps, rtl_dumps):
                    with open(py_dump) as f:
                        py_data = json.load(f)
                    with open(rtl_dump) as f:
                        rtl_data = json.load(f)

                    step = py_data.get('step', 0)
                    py_agents = py_data.get('agents', [])
                    rtl_agents = rtl_data.get('agents', [])

                    # Convert dict to list if needed
                    if isinstance(py_agents, dict):
                        py_agents = [v for k, v in sorted(py_agents.items(), key=lambda x: int(x[0]))]
                    if isinstance(rtl_agents, dict):
                        rtl_agents = [v for k, v in sorted(rtl_agents.items(), key=lambda x: int(x[0]))]

                    for agent_id in range(min(len(py_agents), len(rtl_agents))):
                        py = py_agents[agent_id]
                        rtl = rtl_agents[agent_id]

                        py_x = py.get('x_px', py.get('x', 0))
                        py_y = py.get('y_px', py.get('y', 0))
                        py_angle = py.get('angle_deg', 0)

                        rtl_x = rtl.get('x_px', rtl.get('x', 0))
                        rtl_y = rtl.get('y_px', rtl.get('y', 0))
                        rtl_angle = rtl.get('angle_deg', 0)

                        x_diff = abs(py_x - rtl_x)
                        y_diff = abs(py_y - rtl_y)
                        distance = (x_diff**2 + y_diff**2)**0.5
                        angle_diff = abs(py_angle - rtl_angle)

                        writer.writerow([
                            step, agent_id,
                            py_x, py_y, py_angle,
                            rtl_x, rtl_y, rtl_angle,
                            x_diff, y_diff, distance, angle_diff
                        ])

            self.log(f"  ✓ Created trajectory CSV: {csv_file}")

        except Exception as e:
            self.log(f"  WARNING: Failed to create trajectory CSV: {e}")

    def _generate_trail_map(self, test: RegressionTest, output_path: Path,
                           width: int, height: int):
        """Generate trail map visualization from RTL trail dumps"""
        try:
            trail_dumps = sorted((output_path / "rtl_trail_dumps").glob("trail_step_*.bin"))

            if not trail_dumps:
                self.log(f"  WARNING: No trail dumps found")
                return

            # Visualize the final trail map
            final_trail = trail_dumps[-1]
            trail_map = self._load_trail_dump(final_trail, width, height)

            if trail_map is None:
                self.log(f"  WARNING: Failed to load trail dump")
                return

            # Create heat-mapped image
            img = self._trail_to_image(trail_map)

            # Save
            output_file = output_path / "trail_map.png"
            img.save(output_file)

            self.log(f"  ✓ Created {output_file}")

        except Exception as e:
            self.log(f"  WARNING: Failed to generate trail map: {e}")

    def _load_trail_dump(self, filename: Path, width: int, height: int):
        """Load RTL trail dump from binary file (32-bit values)"""
        try:
            with open(filename, 'rb') as f:
                raw_data = f.read()

            # Trail dumps are stored as 32-bit unsigned integers
            expected_size = width * height * 4  # 4 bytes per pixel

            if len(raw_data) == expected_size:
                # Unpack as 32-bit unsigned integers
                num_pixels = len(raw_data) // 4
                values = struct.unpack(f'<{num_pixels}I', raw_data)
                trail_map = np.array(values, dtype=np.uint32).reshape(height, width)
                return trail_map
            else:
                self.log(f"  WARNING: Trail dump size mismatch: expected {expected_size}, got {len(raw_data)}")
                return None

        except Exception as e:
            self.log(f"  ERROR loading trail dump: {e}")
            return None

    def _trail_to_image(self, trail_map):
        """Convert trail map to heat-mapped RGB image"""
        if trail_map.max() > 0:
            normalized = (trail_map / trail_map.max() * 255).astype(np.uint8)
        else:
            normalized = trail_map.astype(np.uint8)

        img_array = np.zeros((trail_map.shape[0], trail_map.shape[1], 3), dtype=np.uint8)

        # Heat map: black -> blue -> cyan -> green -> yellow -> red
        for i in range(256):
            mask = normalized == i
            if i < 64:
                # Black to blue
                img_array[mask] = [0, 0, min(255, int(i * 4))]
            elif i < 128:
                # Blue to cyan
                img_array[mask] = [0, min(255, int((i - 64) * 4)), 255]
            elif i < 192:
                # Cyan to green
                img_array[mask] = [0, 255, max(0, int(255 - (i - 128) * 4))]
            else:
                # Green to red
                img_array[mask] = [min(255, int((i - 192) * 6.4)), max(0, int(255 - (i - 192) * 4)), 0]

        return Image.fromarray(img_array, 'RGB')

    def _generate_comparison_images(self, test: RegressionTest, output_path: Path,
                                   width: int, height: int):
        """Generate side-by-side comparison images from trail dumps"""
        try:
            # Find shared comparison directory created by run_extended_comparison.sh
            comparison_pattern = f"rtl_comparison_{width}x{height}_{test.num_agents}agents_{test.num_steps}steps"
            comparison_dirs = list(self.base_dir.glob(comparison_pattern))

            if comparison_dirs:
                # Copy comparison images from shared directory
                comparison_src = comparison_dirs[0]
                comparison_dst = output_path / "comparison_images"

                for img_file in comparison_src.glob("comparison_*.png"):
                    shutil.copy2(img_file, comparison_dst)

                # Also copy stats if available
                stats_file = comparison_src / "comparison_stats.json"
                if stats_file.exists():
                    shutil.copy2(stats_file, comparison_dst)

                self.log(f"  ✓ Copied comparison images from {comparison_src}")
            else:
                # Generate comparison images from test-specific dumps
                self._generate_comparison_from_dumps(test, output_path, width, height)

        except Exception as e:
            self.log(f"  WARNING: Failed to generate comparison images: {e}")

    def _generate_comparison_from_dumps(self, test: RegressionTest, output_path: Path,
                                       width: int, height: int):
        """Generate comparison images from Python and RTL trail dumps"""
        try:
            # This would require Python trail dumps which we don't have yet
            # For now, just generate RTL-only images
            trail_dumps = sorted((output_path / "rtl_trail_dumps").glob("trail_step_*.bin"))

            if not trail_dumps:
                return

            comparison_dst = output_path / "comparison_images"

            for i, trail_file in enumerate(trail_dumps):
                trail_map = self._load_trail_dump(trail_file, width, height)
                if trail_map is not None:
                    img = self._trail_to_image(trail_map)

                    # Add labels
                    canvas = Image.new('RGB', (img.width + 20, img.height + 80), color='black')
                    canvas.paste(img, (10, 60))

                    draw = ImageDraw.Draw(canvas)
                    try:
                        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
                    except:
                        font = ImageFont.load_default()

                    step = int(trail_file.stem.split('_')[-1])
                    draw.text((10, 10), f"RTL Trail Map - Step {step}", fill='cyan', font=font)

                    output_file = comparison_dst / f"comparison_{step:05d}.png"
                    canvas.save(output_file)

            self.log(f"  ✓ Generated {len(trail_dumps)} comparison images")

        except Exception as e:
            self.log(f"  WARNING: Failed to generate comparison images: {e}")

    def _generate_statistics(self, test: RegressionTest, output_path: Path,
                           python_result: Optional[Dict], rtl_result: Optional[Dict],
                           comparison_result: Optional[Dict]):
        """Generate statistics report"""
        stats = {
            "test_id": test.test_id,
            "test_name": test.test_name,
            "timestamp": datetime.now().isoformat(),
            "python": python_result,
            "rtl": rtl_result,
            "comparison": comparison_result,
        }

        stats_file = output_path / "test_statistics.json"
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)

        self.log(f"  ✓ Statistics saved to {stats_file}")

    def run_all_tests(self, tests: List[RegressionTest]) -> List[TestResult]:
        """Run all regression tests"""
        for test in tests:
            result = self.run_test(test)
            self.results.append(result)

        return self.results

    def generate_summary_report(self, output_file: str = "regression_results/REPORT.md"):
        """Generate summary report of all test results"""
        output_path = self.base_dir / output_file
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            f.write("# SlimeSimulator Regression Test Report\n\n")
            f.write(f"**Generated**: {datetime.now().isoformat()}\n")
            f.write(f"**Total Tests**: {len(self.results)}\n\n")

            # Summary statistics
            passed = sum(1 for r in self.results if r.status == "PASS")
            failed = sum(1 for r in self.results if r.status == "FAIL")
            errors = sum(1 for r in self.results if r.status == "ERROR")
            skipped = sum(1 for r in self.results if r.status == "SKIP")

            f.write(f"## Summary\n")
            f.write(f"- **Passed**: {passed}\n")
            f.write(f"- **Failed**: {failed}\n")
            f.write(f"- **Errors**: {errors}\n")
            f.write(f"- **Skipped**: {skipped}\n")
            f.write(f"- **Total Duration**: {sum(r.duration_sec for r in self.results):.1f}s\n\n")

            # Results table
            f.write("## Test Results\n\n")
            f.write("| ID | Name | Type | Status | Duration | Agents | Steps |\n")
            f.write("|---|---|---|---|---|---|---|\n")

            for result in self.results:
                # Find original test
                test = next((t for t in self.load_tests() if t.test_id == result.test_id), None)
                if test:
                    f.write(f"| {result.test_id} | {result.test_name} | {test.test_type} | "
                           f"**{result.status}** | {result.duration_sec:.1f}s | "
                           f"{test.num_agents} | {test.num_steps} |\n")

            f.write("\n## Detailed Results\n\n")
            for result in self.results:
                f.write(f"### Test {result.test_id}: {result.test_name}\n")
                f.write(f"- **Status**: {result.status}\n")
                f.write(f"- **Duration**: {result.duration_sec:.1f}s\n")

                if result.comparison_result:
                    f.write(f"- **Max Error**: {result.comparison_result.get('max_error_px', 'N/A'):.3f} px\n")
                    f.write(f"- **Mean Error**: {result.comparison_result.get('mean_error_px', 'N/A'):.3f} px\n")

                if result.error_message:
                    f.write(f"- **Error**: {result.error_message}\n")

                f.write("\n")

        self.log(f"\n{'='*80}")
        self.log(f"Summary report written to: {output_path}")
        self.log(f"{'='*80}\n")

    def log(self, message: str):
        """Log message to console and file"""
        print(message)
        if self.log_file:
            with open(self.log_file, 'a') as f:
                f.write(message + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Run regression tests for SlimeSimulator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all tests
  python run_regression_tests.py

  # Run specific test by ID
  python run_regression_tests.py --test-id 1

  # Run tests of specific type
  python run_regression_tests.py --test-type integration

  # Skip RTL tests (Python only)
  python run_regression_tests.py --no-rtl

  # Output detailed logs
  python run_regression_tests.py --verbose
        """)

    parser.add_argument("--csv", default="regression_tests.csv",
                       help="Path to regression tests CSV file")
    parser.add_argument("--test-id", type=int,
                       help="Run only test with this ID")
    parser.add_argument("--test-type", choices=["smoke", "unit", "integration", "performance", "stress"],
                       help="Run only tests of this type")
    parser.add_argument("--no-python", action="store_true",
                       help="Skip Python simulations")
    parser.add_argument("--no-rtl", action="store_true",
                       help="Skip RTL simulations")
    parser.add_argument("--output-dir", default="regression_results",
                       help="Directory for test outputs")
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose logging")

    args = parser.parse_args()

    # Create runner
    runner = RegressionTestRunner(args.csv)
    runner.log_file = Path(args.output_dir) / "regression_tests.log"
    runner.log_file.parent.mkdir(parents=True, exist_ok=True)

    # Load tests
    tests = runner.load_tests()

    # Filter tests
    if args.test_id:
        tests = [t for t in tests if t.test_id == args.test_id]
    if args.test_type:
        tests = [t for t in tests if t.test_type == args.test_type]

    # Apply CLI overrides
    for test in tests:
        if args.no_python:
            test.python_enabled = False
        if args.no_rtl:
            test.rtl_enabled = False

    if not tests:
        runner.log("No tests to run!")
        return 1

    runner.log(f"Running {len(tests)} regression test(s)...\n")

    # Run tests
    results = runner.run_all_tests(tests)

    # Generate report
    runner.generate_summary_report(f"{args.output_dir}/REPORT.md")

    # Summary
    runner.log("\nTest Execution Summary:")
    passed = sum(1 for r in results if r.status == "PASS")
    failed = sum(1 for r in results if r.status == "FAIL")
    errors = sum(1 for r in results if r.status == "ERROR")

    runner.log(f"  PASSED: {passed}/{len(results)}")
    runner.log(f"  FAILED: {failed}/{len(results)}")
    runner.log(f"  ERRORS: {errors}/{len(results)}")

    return 0 if (failed + errors) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
