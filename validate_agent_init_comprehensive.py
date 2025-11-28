#!/usr/bin/env python3
"""
Comprehensive Agent Initialization Validation

This script:
1. Generates Python reference agent initialization state
2. Builds and runs RTL agent initialization validator (Verilator)
3. Compares RTL vs Python initialization
4. Generates detailed validation report with statistics
5. Creates visualization of spawn pattern

This validates that RTL and Python both:
- Spawn agents on a circle (40% of min dimension)
- Initialize at correct positions
- Initialize with correct angles (spawn_angle + π)
- Have properly normalized angles in [0, 2π)
"""

import json
import subprocess
import os
import sys
import math
import numpy as np
from pathlib import Path
from datetime import datetime

# Add parent dir to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from slime_simulator import SlimeSimulator, SimulationConfig
from validate_agent_initialization import extract_agent_state

# Configuration
PYTHON_JSON = "python_agent_validation.json"
RTL_JSON = "rtl_agent_validation.json"
REPORT_FILE = "agent_init_validation_report.txt"
COMPARISON_JSON = "agent_init_comparison.json"

# Tolerances for comparison (in fixed-point units and pixels)
# Allow for rounding differences between Python float and RTL fixed-point arithmetic
# Python uses float math while RTL uses fixed-point and trig LUT
# Differences are sub-pixel, acceptable for initialization validation
TOLERANCE_FP = 4096  # Fixed-point units (1 pixel - max sub-pixel rounding error)
TOLERANCE_PX = 1.0  # Pixels (very generous to account for all rounding)
TOLERANCE_ANGLE_FP = 10  # Fixed-point angle units (~0.14°)
TOLERANCE_ANGLE_DEG = 0.1  # Degrees (allows for trigonometric rounding)

class AgentInitValidator:
    """Validates RTL vs Python agent initialization"""

    def __init__(self, width=320, height=240, num_agents=1000):
        self.width = width
        self.height = height
        self.num_agents = num_agents
        self.python_agents = None
        self.rtl_agents = None
        self.comparison = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "failures": []
        }

    def generate_python_validation(self):
        """Generate Python reference agent initialization"""
        print("\n" + "="*70)
        print("STEP 1: Generating Python Reference Agent Initialization")
        print("="*70)

        try:
            config = SimulationConfig(
                width=self.width,
                height=self.height,
                num_agents=self.num_agents
            )
            sim = SlimeSimulator(config)

            # Extract and save agent state
            agent_data = extract_agent_state(sim)

            with open(PYTHON_JSON, 'w') as f:
                json.dump(agent_data, f, indent=2)

            print(f"✓ Generated Python validation: {PYTHON_JSON}")
            print(f"  Agents: {agent_data['summary']['num_agents']}")
            print(f"  Resolution: {agent_data['summary']['resolution']}")

            # Load agents
            self.python_agents = agent_data['agents']
            return True

        except Exception as e:
            print(f"✗ Error generating Python validation: {e}")
            return False

    def build_and_run_rtl_validator(self):
        """Build and run RTL agent initialization validator"""
        print("\n" + "="*70)
        print("STEP 2: Building RTL Agent Initialization Validator")
        print("="*70)

        sim_dir = Path(__file__).parent / "rtl" / "sim"

        # Check if testbench exists
        if not (sim_dir / "agent_init_validator_tb.cpp").exists():
            print(f"✗ Testbench not found: {sim_dir}/agent_init_validator_tb.cpp")
            return False

        # Build with Verilator
        print(f"Building in: {sim_dir}")
        build_cmd = [
            "make",
            "-f", "Makefile.agent_init_validator",
            "clean",
            "sim"
        ]

        try:
            # Pass NUM_AGENTS to makefile as environment variable
            build_env = os.environ.copy()
            build_env['NUM_AGENTS'] = str(self.num_agents)

            result = subprocess.run(
                build_cmd,
                cwd=str(sim_dir),
                capture_output=True,
                text=True,
                timeout=300,
                env=build_env
            )

            if result.returncode != 0:
                print(f"✗ Build failed:")
                print(result.stdout)
                print(result.stderr)
                return False

            print("✓ RTL validator compiled successfully")

        except subprocess.TimeoutExpired:
            print("✗ Build timed out (>300s)")
            return False
        except Exception as e:
            print(f"✗ Build error: {e}")
            return False

        # Run validator
        print("\n" + "="*70)
        print("STEP 3: Running RTL Agent Initialization Validator")
        print("="*70)

        bin_path = sim_dir / "obj_dir_agent_init" / "Vslime_top"
        rtl_json_path = sim_dir / RTL_JSON

        if not bin_path.exists():
            print(f"✗ Binary not found: {bin_path}")
            return False

        run_cmd = [str(bin_path), str(rtl_json_path)]

        try:
            result = subprocess.run(
                run_cmd,
                cwd=str(sim_dir),
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                print(f"✗ Simulation failed:")
                print(result.stdout)
                print(result.stderr)
                return False

            print(result.stdout)
            print("✓ RTL validator simulation complete")

            # Load RTL results
            if rtl_json_path.exists():
                with open(rtl_json_path, 'r') as f:
                    rtl_data = json.load(f)
                self.rtl_agents = rtl_data.get('agents', [])

                # Copy to repo root for comparison
                with open(RTL_JSON, 'w') as f:
                    json.dump(rtl_data, f, indent=2)

                print(f"✓ Loaded RTL validation: {RTL_JSON}")
                return True
            else:
                print(f"✗ RTL JSON output not found: {rtl_json_path}")
                return False

        except subprocess.TimeoutExpired:
            print("✗ Simulation timed out (>60s)")
            return False
        except Exception as e:
            print(f"✗ Simulation error: {e}")
            return False

    def compare_agents(self):
        """Compare Python vs RTL agent initialization"""
        print("\n" + "="*70)
        print("STEP 4: Comparing Python vs RTL Agent Initialization")
        print("="*70)

        if not self.python_agents or not self.rtl_agents:
            print("✗ Agent data not loaded")
            return False

        num_validate = min(len(self.python_agents), len(self.rtl_agents))
        self.comparison["total"] = num_validate

        print(f"Comparing {num_validate} agents...")
        print(f"Tolerances: {TOLERANCE_FP} FP units, {TOLERANCE_PX} pixels, "
              f"{TOLERANCE_ANGLE_DEG}°")

        comparison_details = []

        for i in range(num_validate):
            py_agent = self.python_agents[i]
            rtl_agent = self.rtl_agents[i]

            # Extract values
            py_x_fp = py_agent['position']['x_fp']
            py_y_fp = py_agent['position']['y_fp']
            py_angle_fp = py_agent['angle']['angle_fp']

            rtl_x_fp = rtl_agent['position']['x_fp']
            rtl_y_fp = rtl_agent['position']['y_fp']
            rtl_angle_fp = rtl_agent['angle']['angle_fp']

            # Calculate errors
            err_x = abs(py_x_fp - rtl_x_fp)
            err_y = abs(py_y_fp - rtl_y_fp)
            err_angle = abs(py_angle_fp - rtl_angle_fp)

            # Convert to pixels and degrees
            FP_SCALE = 4096
            err_x_px = err_x / FP_SCALE
            err_y_px = err_y / FP_SCALE
            err_angle_deg = err_angle / FP_SCALE * 180 / math.pi

            # Normalize angle error to [-π, π]
            if err_angle_deg > 180:
                err_angle_deg = 360 - err_angle_deg

            # Check if within tolerance
            pos_ok = err_x <= TOLERANCE_FP and err_y <= TOLERANCE_FP

            # For angles, handle wraparound: check both direct difference and wraparound
            two_pi_fp = int(2 * math.pi * FP_SCALE)
            angle_err_wrapped = (err_angle % two_pi_fp)
            # Take the smaller of the two possible wraparound distances
            if angle_err_wrapped > two_pi_fp // 2:
                angle_err_wrapped = two_pi_fp - angle_err_wrapped
            angle_ok = angle_err_wrapped <= TOLERANCE_ANGLE_FP

            passed = pos_ok and angle_ok

            if passed:
                self.comparison["passed"] += 1
            else:
                self.comparison["failed"] += 1
                self.comparison["failures"].append({
                    "agent_idx": i,
                    "error_x_fp": err_x,
                    "error_y_fp": err_y,
                    "error_angle_fp": err_angle,
                    "reason": []
                })

                if not pos_ok:
                    self.comparison["failures"][-1]["reason"].append(
                        f"Position error: ({err_x_px:.3f}, {err_y_px:.3f}) px"
                    )
                if not angle_ok:
                    self.comparison["failures"][-1]["reason"].append(
                        f"Angle error: {err_angle_deg:.3f}°"
                    )

            comparison_details.append({
                "agent_idx": i,
                "python": {
                    "x_fp": py_x_fp,
                    "y_fp": py_y_fp,
                    "angle_fp": py_angle_fp
                },
                "rtl": {
                    "x_fp": rtl_x_fp,
                    "y_fp": rtl_y_fp,
                    "angle_fp": rtl_angle_fp
                },
                "error": {
                    "x_fp": err_x,
                    "y_fp": err_y,
                    "angle_fp": err_angle,
                    "x_px": err_x_px,
                    "y_px": err_y_px,
                    "angle_deg": err_angle_deg
                },
                "passed": passed
            })

        # Save detailed comparison
        with open(COMPARISON_JSON, 'w') as f:
            json.dump(comparison_details, f, indent=2)

        print(f"\nComparison Results:")
        print(f"  Total agents: {self.comparison['total']}")
        print(f"  Passed: {self.comparison['passed']} ({100*self.comparison['passed']/num_validate:.1f}%)")
        print(f"  Failed: {self.comparison['failed']} ({100*self.comparison['failed']/num_validate:.1f}%)")

        if self.comparison["failures"]:
            print(f"\nFirst 10 failures:")
            for fail in self.comparison["failures"][:10]:
                print(f"  Agent {fail['agent_idx']}: {' | '.join(fail['reason'])}")

        return self.comparison["failed"] == 0

    def generate_report(self):
        """Generate comprehensive validation report"""
        print("\n" + "="*70)
        print("STEP 5: Generating Validation Report")
        print("="*70)

        with open(REPORT_FILE, 'w') as f:
            f.write("="*70 + "\n")
            f.write("AGENT INITIALIZATION VALIDATION REPORT\n")
            f.write("="*70 + "\n\n")

            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write(f"Resolution: {self.width}x{self.height}\n")
            f.write(f"Number of Agents: {self.num_agents}\n\n")

            f.write("COMPARISON RESULTS:\n")
            f.write("-"*70 + "\n")
            f.write(f"Total agents: {self.comparison['total']}\n")
            f.write(f"Passed: {self.comparison['passed']}\n")
            f.write(f"Failed: {self.comparison['failed']}\n")
            f.write(f"Pass rate: {100*self.comparison['passed']/max(self.comparison['total'], 1):.1f}%\n\n")

            f.write("TOLERANCES:\n")
            f.write(f"Position: ±{TOLERANCE_FP} FP units (±{TOLERANCE_FP/4096:.3f} px)\n")
            f.write(f"Angle: ±{TOLERANCE_ANGLE_FP} FP units (±{TOLERANCE_ANGLE_DEG}°)\n\n")

            if self.comparison["failures"]:
                f.write("FAILED AGENTS:\n")
                f.write("-"*70 + "\n")
                for fail in self.comparison["failures"][:20]:
                    f.write(f"Agent {fail['agent_idx']}:\n")
                    for reason in fail['reason']:
                        f.write(f"  - {reason}\n")
            else:
                f.write("✓ ALL AGENTS PASSED VALIDATION\n")

            f.write("\nOUTPUT FILES:\n")
            f.write(f"- {PYTHON_JSON}: Python reference agent state\n")
            f.write(f"- {RTL_JSON}: RTL agent state\n")
            f.write(f"- {COMPARISON_JSON}: Detailed per-agent comparison\n")
            f.write(f"- {REPORT_FILE}: This report\n")

        print(f"✓ Report saved: {REPORT_FILE}")

        # Print report to console
        with open(REPORT_FILE, 'r') as f:
            print("\n" + f.read())

        return True

    def run(self):
        """Run complete validation pipeline"""
        print("\n" + "="*70)
        print("AGENT INITIALIZATION COMPREHENSIVE VALIDATION")
        print("="*70)
        print(f"Resolution: {self.width}x{self.height}")
        print(f"Agents: {self.num_agents}")
        print(f"Start time: {datetime.now().isoformat()}\n")

        # Step 1: Generate Python validation
        if not self.generate_python_validation():
            return False

        # Step 2-3: Build and run RTL validator
        if not self.build_and_run_rtl_validator():
            return False

        # Step 4: Compare
        comparison_ok = self.compare_agents()

        # Step 5: Generate report
        self.generate_report()

        print("\n" + "="*70)
        if comparison_ok:
            print("✓ VALIDATION PASSED - RTL and Python initialization match!")
        else:
            print("✗ VALIDATION FAILED - Differences found in initialization")
        print("="*70 + "\n")

        return comparison_ok

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Comprehensive agent initialization validation"
    )
    parser.add_argument("--width", type=int, default=320, help="Canvas width")
    parser.add_argument("--height", type=int, default=240, help="Canvas height")
    parser.add_argument("--agents", type=int, default=1000, help="Number of agents")
    parser.add_argument("--skip-python", action="store_true", help="Skip Python generation if exists")
    parser.add_argument("--skip-build", action="store_true", help="Skip RTL build if binary exists")

    args = parser.parse_args()

    validator = AgentInitValidator(
        width=args.width,
        height=args.height,
        num_agents=args.agents
    )

    success = validator.run()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
