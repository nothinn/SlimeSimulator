#!/usr/bin/env python3
"""
Agent Initialization Comparison Tool

Compares agent initialization state between Python reference and RTL implementation.

Generates:
- Per-agent comparison table
- Statistical summary
- Error metrics
- Visual ASCII circle diagram
- Pass/fail status

Output:
- agent_validation_report.txt (human-readable)
- agent_validation_report.json (machine-readable)
"""

import json
import argparse
import numpy as np
from typing import Dict, List, Tuple


class AgentComparisonReport:
    """Generate detailed comparison report between Python and RTL agents."""

    def __init__(self, python_data: Dict, rtl_data: Dict):
        self.python_data = python_data
        self.rtl_data = rtl_data
        self.errors = []
        self.warnings = []
        self.passed = True

        # Tolerances
        self.position_tolerance_fp = 2  # ±2 fixed-point units (rounding)
        self.angle_tolerance_fp = 2     # ±2 fixed-point units (rounding)
        self.distance_tolerance_px = 0.5  # ±0.5 pixels from expected radius

    def compare_agents(self) -> Dict:
        """
        Compare all agents and generate comparison metrics.

        Returns:
            dict with comparison results
        """
        python_agents = self.python_data['agents']
        rtl_agents = self.rtl_data['agents']

        num_agents = min(len(python_agents), len(rtl_agents))

        comparison_results = []
        position_errors = []
        angle_errors = []
        distance_errors = []

        for i in range(num_agents):
            py_agent = python_agents[i]
            rtl_agent = rtl_agents[i]

            # Position comparison (fixed-point)
            x_fp_err = abs(py_agent['position']['x_fp'] - rtl_agent['position']['x_fp'])
            y_fp_err = abs(py_agent['position']['y_fp'] - rtl_agent['position']['y_fp'])

            # Position comparison (pixels)
            x_px_py = py_agent['position']['x_px']
            y_px_py = py_agent['position']['y_px']
            x_px_rtl = rtl_agent['position']['x_px']
            y_px_rtl = rtl_agent['position']['y_px']

            position_err_px = np.sqrt((x_px_py - x_px_rtl)**2 + (y_px_py - y_px_rtl)**2)

            # Angle comparison (fixed-point)
            angle_fp_py = py_agent['angle']['angle_fp']
            angle_fp_rtl = rtl_agent['angle']['angle_fp']
            angle_fp_err = abs(angle_fp_py - angle_fp_rtl)

            # Angle comparison (degrees)
            angle_deg_py = py_agent['angle']['angle_deg']
            angle_deg_rtl = rtl_agent['angle']['angle_deg']
            angle_deg_err = abs(angle_deg_py - angle_deg_rtl)

            # Distance from center
            dist_py = py_agent['geometry']['distance_from_center']
            dist_rtl = rtl_agent['geometry']['distance_from_center']
            expected_radius = py_agent['expected']['radius_px']
            dist_err_from_expected_py = abs(dist_py - expected_radius)
            dist_err_from_expected_rtl = abs(dist_rtl - expected_radius)

            # Determine pass/fail for this agent
            agent_passed = True
            agent_issues = []

            if x_fp_err > self.position_tolerance_fp or y_fp_err > self.position_tolerance_fp:
                agent_passed = False
                agent_issues.append(f"Position error: x_err={x_fp_err} y_err={y_fp_err} (tolerance={self.position_tolerance_fp})")

            if angle_fp_err > self.angle_tolerance_fp:
                agent_passed = False
                agent_issues.append(f"Angle error: {angle_fp_err} fp units (tolerance={self.angle_tolerance_fp})")

            if dist_err_from_expected_rtl > self.distance_tolerance_px:
                agent_passed = False
                agent_issues.append(f"Distance from center: {dist_err_from_expected_rtl:.3f} px (tolerance={self.distance_tolerance_px})")

            # Store results
            result = {
                'index': i,
                'passed': agent_passed,
                'issues': agent_issues,
                'position': {
                    'x_fp_python': py_agent['position']['x_fp'],
                    'x_fp_rtl': rtl_agent['position']['x_fp'],
                    'x_fp_error': x_fp_err,
                    'y_fp_python': py_agent['position']['y_fp'],
                    'y_fp_rtl': rtl_agent['position']['y_fp'],
                    'y_fp_error': y_fp_err,
                    'position_error_px': position_err_px,
                },
                'angle': {
                    'angle_fp_python': angle_fp_py,
                    'angle_fp_rtl': angle_fp_rtl,
                    'angle_fp_error': angle_fp_err,
                    'angle_deg_python': angle_deg_py,
                    'angle_deg_rtl': angle_deg_rtl,
                    'angle_deg_error': angle_deg_err,
                },
                'geometry': {
                    'distance_python': dist_py,
                    'distance_rtl': dist_rtl,
                    'expected_radius': expected_radius,
                    'distance_error_python': dist_err_from_expected_py,
                    'distance_error_rtl': dist_err_from_expected_rtl,
                }
            }

            comparison_results.append(result)
            position_errors.append(position_err_px)
            angle_errors.append(angle_deg_err)
            distance_errors.append(dist_err_from_expected_rtl)

            if not agent_passed:
                self.passed = False
                self.errors.append(f"Agent {i}: " + ", ".join(agent_issues))

        # Calculate statistics
        statistics = {
            'num_compared': num_agents,
            'num_passed': sum(1 for r in comparison_results if r['passed']),
            'num_failed': sum(1 for r in comparison_results if not r['passed']),
            'position_error_px': {
                'min': float(np.min(position_errors)),
                'max': float(np.max(position_errors)),
                'mean': float(np.mean(position_errors)),
                'std': float(np.std(position_errors)),
            },
            'angle_error_deg': {
                'min': float(np.min(angle_errors)),
                'max': float(np.max(angle_errors)),
                'mean': float(np.mean(angle_errors)),
                'std': float(np.std(angle_errors)),
            },
            'distance_error_px': {
                'min': float(np.min(distance_errors)),
                'max': float(np.max(distance_errors)),
                'mean': float(np.mean(distance_errors)),
                'std': float(np.std(distance_errors)),
            }
        }

        return {
            'summary': {
                'overall_passed': self.passed,
                'num_agents_compared': num_agents,
                'num_agents_passed': statistics['num_passed'],
                'num_agents_failed': statistics['num_failed'],
            },
            'statistics': statistics,
            'agents': comparison_results,
            'errors': self.errors,
            'warnings': self.warnings,
        }

    def generate_text_report(self, comparison: Dict) -> str:
        """Generate human-readable text report."""

        lines = []
        lines.append("=" * 80)
        lines.append("AGENT INITIALIZATION VALIDATION REPORT")
        lines.append("=" * 80)
        lines.append("")

        # Summary
        summary = comparison['summary']
        status = "✓ PASSED" if summary['overall_passed'] else "✗ FAILED"
        lines.append(f"Overall Status: {status}")
        lines.append(f"Agents Compared: {summary['num_agents_compared']}")
        lines.append(f"Agents Passed:   {summary['num_agents_passed']}")
        lines.append(f"Agents Failed:   {summary['num_agents_failed']}")
        lines.append("")

        # Statistics
        stats = comparison['statistics']
        lines.append("-" * 80)
        lines.append("STATISTICS")
        lines.append("-" * 80)
        lines.append("")

        lines.append("Position Error (pixels):")
        lines.append(f"  Min:  {stats['position_error_px']['min']:.6f}")
        lines.append(f"  Max:  {stats['position_error_px']['max']:.6f}")
        lines.append(f"  Mean: {stats['position_error_px']['mean']:.6f}")
        lines.append(f"  Std:  {stats['position_error_px']['std']:.6f}")
        lines.append("")

        lines.append("Angle Error (degrees):")
        lines.append(f"  Min:  {stats['angle_error_deg']['min']:.6f}")
        lines.append(f"  Max:  {stats['angle_error_deg']['max']:.6f}")
        lines.append(f"  Mean: {stats['angle_error_deg']['mean']:.6f}")
        lines.append(f"  Std:  {stats['angle_error_deg']['std']:.6f}")
        lines.append("")

        lines.append("Distance from Center Error (pixels):")
        lines.append(f"  Min:  {stats['distance_error_px']['min']:.6f}")
        lines.append(f"  Max:  {stats['distance_error_px']['max']:.6f}")
        lines.append(f"  Mean: {stats['distance_error_px']['mean']:.6f}")
        lines.append(f"  Std:  {stats['distance_error_px']['std']:.6f}")
        lines.append("")

        # Failed agents (if any)
        failed_agents = [a for a in comparison['agents'] if not a['passed']]
        if failed_agents:
            lines.append("-" * 80)
            lines.append(f"FAILED AGENTS ({len(failed_agents)} total)")
            lines.append("-" * 80)
            lines.append("")

            for agent in failed_agents[:20]:  # Show first 20 failures
                lines.append(f"Agent {agent['index']}:")
                for issue in agent['issues']:
                    lines.append(f"  ✗ {issue}")
                lines.append(f"  Position (Python): ({agent['position']['x_fp_python']}, {agent['position']['y_fp_python']})")
                lines.append(f"  Position (RTL):    ({agent['position']['x_fp_rtl']}, {agent['position']['y_fp_rtl']})")
                lines.append(f"  Angle (Python):    {agent['angle']['angle_fp_python']} ({agent['angle']['angle_deg_python']:.1f}°)")
                lines.append(f"  Angle (RTL):       {agent['angle']['angle_fp_rtl']} ({agent['angle']['angle_deg_rtl']:.1f}°)")
                lines.append("")

            if len(failed_agents) > 20:
                lines.append(f"... and {len(failed_agents) - 20} more failures")
                lines.append("")

        # Sample of passed agents
        passed_agents = [a for a in comparison['agents'] if a['passed']]
        if passed_agents:
            lines.append("-" * 80)
            lines.append(f"SAMPLE PASSED AGENTS (showing first 10 of {len(passed_agents)})")
            lines.append("-" * 80)
            lines.append("")

            for agent in passed_agents[:10]:
                i = agent['index']
                pos_err = agent['position']['position_error_px']
                ang_err = agent['angle']['angle_deg_error']
                lines.append(f"Agent {i:4d}: ✓ pos_err={pos_err:.6f} px, ang_err={ang_err:.6f}°")

            lines.append("")

        # ASCII circle diagram
        lines.append("-" * 80)
        lines.append("AGENT DISTRIBUTION VISUALIZATION")
        lines.append("-" * 80)
        lines.append("")
        lines.extend(self.generate_ascii_circle_diagram(comparison))
        lines.append("")

        # Final summary
        lines.append("=" * 80)
        if summary['overall_passed']:
            lines.append("✓ VALIDATION PASSED - All agents within tolerance")
        else:
            lines.append(f"✗ VALIDATION FAILED - {summary['num_agents_failed']} agents outside tolerance")
        lines.append("=" * 80)

        return "\n".join(lines)

    def generate_ascii_circle_diagram(self, comparison: Dict, size: int = 40) -> List[str]:
        """
        Generate ASCII diagram showing agent positions on circle.

        Args:
            comparison: Comparison results
            size: Diagram size (width and height in characters)

        Returns:
            List of strings (lines of ASCII art)
        """
        lines = []

        # Create 2D grid
        grid = [[' ' for _ in range(size)] for _ in range(size)]

        # Center coordinates
        cx = size // 2
        cy = size // 2

        # Draw circle outline
        radius = size // 2 - 2
        for angle_deg in range(0, 360, 5):
            angle_rad = np.radians(angle_deg)
            x = int(cx + radius * np.cos(angle_rad))
            y = int(cy + radius * np.sin(angle_rad))
            if 0 <= x < size and 0 <= y < size:
                grid[y][x] = '·'

        # Plot agents
        num_agents = len(comparison['agents'])
        for i, agent in enumerate(comparison['agents']):
            # Calculate position on ASCII grid
            angle_rad = (2 * np.pi * i) / num_agents
            x = int(cx + radius * np.cos(angle_rad))
            y = int(cy + radius * np.sin(angle_rad))

            if 0 <= x < size and 0 <= y < size:
                if agent['passed']:
                    grid[y][x] = 'o'  # Passed agent
                else:
                    grid[y][x] = 'X'  # Failed agent

        # Draw center marker
        grid[cy][cx] = '+'

        # Convert grid to strings
        lines.append("Legend: o = passed, X = failed, · = expected circle, + = center")
        lines.append("")
        for row in grid:
            lines.append(''.join(row))

        return lines


def main():
    parser = argparse.ArgumentParser(description='Compare Python and RTL agent initialization')
    parser.add_argument('--python', type=str, default='python_agent_validation.json',
                       help='Python validation JSON file')
    parser.add_argument('--rtl', type=str, default='rtl_agent_validation.json',
                       help='RTL validation JSON file')
    parser.add_argument('--output-txt', type=str, default='agent_validation_report.txt',
                       help='Output text report file')
    parser.add_argument('--output-json', type=str, default='agent_validation_report.json',
                       help='Output JSON report file')
    parser.add_argument('--verbose', action='store_true',
                       help='Print verbose output')

    args = parser.parse_args()

    print(f"[Comparison] Loading Python validation data from {args.python}...")
    with open(args.python, 'r') as f:
        python_data = json.load(f)

    print(f"[Comparison] Loading RTL validation data from {args.rtl}...")
    with open(args.rtl, 'r') as f:
        rtl_data = json.load(f)

    print(f"[Comparison] Comparing agents...")

    # Create report generator
    report = AgentComparisonReport(python_data, rtl_data)

    # Compare agents
    comparison = report.compare_agents()

    # Generate text report
    print(f"[Comparison] Generating text report...")
    text_report = report.generate_text_report(comparison)

    # Save text report
    with open(args.output_txt, 'w') as f:
        f.write(text_report)
    print(f"[Comparison] ✓ Text report saved to {args.output_txt}")

    # Save JSON report
    with open(args.output_json, 'w') as f:
        json.dump(comparison, f, indent=2)
    print(f"[Comparison] ✓ JSON report saved to {args.output_json}")

    # Print summary
    summary = comparison['summary']
    print(f"\n[Comparison] Summary:")
    print(f"  Overall Status: {'✓ PASSED' if summary['overall_passed'] else '✗ FAILED'}")
    print(f"  Agents Compared: {summary['num_agents_compared']}")
    print(f"  Agents Passed: {summary['num_agents_passed']}")
    print(f"  Agents Failed: {summary['num_agents_failed']}")

    # Print first few errors
    if comparison['errors']:
        print(f"\n[Comparison] First errors:")
        for err in comparison['errors'][:5]:
            print(f"  ✗ {err}")
        if len(comparison['errors']) > 5:
            print(f"  ... and {len(comparison['errors']) - 5} more errors")

    # Return exit code
    return 0 if summary['overall_passed'] else 1


if __name__ == '__main__':
    exit(main())
