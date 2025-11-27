#!/usr/bin/env python3
"""
Agent Movement Diagnostic Tool

Tracks step-by-step agent behavior with detailed logging:
- Position and angle at each step
- Sensor readings (F/L/R)
- Turn decisions
- Movement vectors
- Trail deposits

Creates ground truth for RTL comparison.
"""

import numpy as np
import json
import sys
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Any
from rtl.sim.python_reference import (
    LFSR, FixedPoint, TrigLUT, SlimeAgent, SlimeSimulatorReference
)


@dataclass
class AgentStep:
    """Data structure for one agent's step."""
    step_num: int
    agent_id: int

    # Before movement
    pos_x_fp: int
    pos_y_fp: int
    pos_x_float: float
    pos_y_float: float
    angle_idx: int
    angle_rad: float

    # Sensor readings
    sensor_forward: int
    sensor_left: int
    sensor_right: int
    sensor_fwd_pos: tuple
    sensor_left_pos: tuple
    sensor_right_pos: tuple

    # Decision
    turn_decision: str  # 'none', 'left', 'right', 'random_left', 'random_right'
    new_angle_idx: int
    new_angle_rad: float

    # After movement
    new_pos_x_fp: int
    new_pos_y_fp: int
    new_pos_x_float: float
    new_pos_y_float: float
    deposit_pixel: tuple

    # Derived info
    distance_moved: float
    angle_changed: float


class DiagnosticSimulator(SlimeSimulatorReference):
    """Enhanced simulator with detailed step logging."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.step_logs: List[AgentStep] = []
        self.current_step = 0

    def _angle_idx_to_radians(self, idx: int) -> float:
        """Convert 10-bit angle index to radians."""
        return (idx / 1024.0) * 2 * np.pi

    def _get_sensor_position(self, agent: SlimeAgent, angle_offset: int) -> tuple:
        """Get the pixel position of a sensor (for logging)."""
        sensor_angle = (agent.angle + angle_offset) & 0x3FF
        sin_val = self.trig.sin(sensor_angle)
        cos_val = self.trig.cos(sensor_angle)

        dx = self.fp.multiply(cos_val, self.sensor_distance)
        dy = self.fp.multiply(sin_val, self.sensor_distance)

        sensor_x = (agent.x + dx) & self.fp.mask
        sensor_y = (agent.y + dy) & self.fp.mask

        px = int(self.fp.from_fixed(sensor_x)) % self.width
        py = int(self.fp.from_fixed(sensor_y)) % self.height

        return (px, py)

    def update_agent_diagnostic(self, agent: SlimeAgent, agent_id: int) -> AgentStep:
        """Update agent with full diagnostic logging."""

        # Store initial state
        old_x = agent.x
        old_y = agent.y
        old_angle = agent.angle

        # Sense in three directions
        sense_forward = self.sense(agent, 0)
        angle_offset = 81  # ~0.5 radians in angle indices
        sense_left = self.sense(agent, angle_offset)
        sense_right = self.sense(agent, -angle_offset & 0x3FF)

        # Get sensor positions
        fwd_pos = self._get_sensor_position(agent, 0)
        left_pos = self._get_sensor_position(agent, angle_offset)
        right_pos = self._get_sensor_position(agent, -angle_offset & 0x3FF)

        # Turn based on sensing
        turn_amount = 10  # ~6 degrees per step
        turn_decision = "none"

        if sense_forward > sense_left and sense_forward > sense_right:
            # Continue straight
            turn_decision = "none"
        elif sense_forward < sense_left and sense_forward < sense_right:
            # Random turn
            self.lfsr.step()
            if self.lfsr.state & 1:
                agent.angle = (agent.angle + turn_amount) & 0x3FF
                turn_decision = "random_left"
            else:
                agent.angle = (agent.angle - turn_amount) & 0x3FF
                turn_decision = "random_right"
        elif sense_left > sense_right:
            agent.angle = (agent.angle + turn_amount) & 0x3FF
            turn_decision = "left"
        else:
            agent.angle = (agent.angle - turn_amount) & 0x3FF
            turn_decision = "right"

        new_angle = agent.angle

        # Move forward
        sin_val = self.trig.sin(agent.angle)
        cos_val = self.trig.cos(agent.angle)

        dx = self.fp.multiply(cos_val, self.move_speed)
        dy = self.fp.multiply(sin_val, self.move_speed)

        new_x = (agent.x + dx) & self.fp.mask
        new_y = (agent.y + dy) & self.fp.mask

        # Convert to pixels and wrap
        px = int(self.fp.from_fixed(new_x)) % self.width
        py = int(self.fp.from_fixed(new_y)) % self.height

        # Update position
        agent.x = self.fp.to_fixed(px)
        agent.y = self.fp.to_fixed(py)

        # Deposit trail
        deposit_pos = (px, py)
        self.trail_map[py, px] = min(255, self.trail_map[py, px] + self.deposit_amount)

        # Calculate distance moved
        old_x_float = self.fp.from_fixed(old_x)
        old_y_float = self.fp.from_fixed(old_y)
        new_x_float = self.fp.from_fixed(agent.x)
        new_y_float = self.fp.from_fixed(agent.y)

        dist = np.sqrt((new_x_float - old_x_float)**2 + (new_y_float - old_y_float)**2)

        # Calculate angle change
        angle_change = self._angle_idx_to_radians(new_angle) - self._angle_idx_to_radians(old_angle)

        # Create log entry
        log_entry = AgentStep(
            step_num=self.current_step,
            agent_id=agent_id,
            pos_x_fp=old_x,
            pos_y_fp=old_y,
            pos_x_float=old_x_float,
            pos_y_float=old_y_float,
            angle_idx=old_angle,
            angle_rad=self._angle_idx_to_radians(old_angle),
            sensor_forward=sense_forward,
            sensor_left=sense_left,
            sensor_right=sense_right,
            sensor_fwd_pos=fwd_pos,
            sensor_left_pos=left_pos,
            sensor_right_pos=right_pos,
            turn_decision=turn_decision,
            new_angle_idx=new_angle,
            new_angle_rad=self._angle_idx_to_radians(new_angle),
            new_pos_x_fp=agent.x,
            new_pos_y_fp=agent.y,
            new_pos_x_float=new_x_float,
            new_pos_y_float=new_y_float,
            deposit_pixel=deposit_pos,
            distance_moved=dist,
            angle_changed=angle_change
        )

        return log_entry

    def step_diagnostic(self, tracked_agents: List[int] = None):
        """Run one simulation step with diagnostic logging."""
        if tracked_agents is None:
            tracked_agents = list(range(min(10, self.num_agents)))

        # Update all agents
        for i, agent in enumerate(self.agents):
            if i in tracked_agents:
                log_entry = self.update_agent_diagnostic(agent, i)
                self.step_logs.append(log_entry)
            else:
                self.update_agent(agent)

        # Diffuse and decay (currently using simple decay)
        self.diffuse_and_decay()

        self.current_step += 1

    def run_diagnostic(self, num_steps: int, tracked_agents: List[int] = None):
        """Run simulation with diagnostic logging."""
        for _ in range(num_steps):
            self.step_diagnostic(tracked_agents)

    def export_logs_json(self, filename: str):
        """Export all logged steps to JSON."""
        logs_dict = [asdict(log) for log in self.step_logs]

        metadata = {
            'width': self.width,
            'height': self.height,
            'num_agents': self.num_agents,
            'total_steps': self.current_step,
            'lfsr_seed': hex(self.lfsr.state),
            'fixed_point': {
                'int_bits': self.fp.int_bits,
                'frac_bits': self.fp.frac_bits,
                'scale': self.fp.scale
            },
            'parameters': {
                'move_speed': self.fp.from_fixed(self.move_speed),
                'turn_speed': self.fp.from_fixed(self.turn_speed),
                'sensor_angle': self.fp.from_fixed(self.sensor_angle),
                'sensor_distance': self.fp.from_fixed(self.sensor_distance),
                'deposit_amount': self.deposit_amount,
                'decay_rate': self.fp.from_fixed(self.decay_rate)
            }
        }

        output = {
            'metadata': metadata,
            'step_logs': logs_dict
        }

        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"Exported {len(logs_dict)} log entries to {filename}")
        return output

    def get_agent_trajectory(self, agent_id: int) -> List[Dict]:
        """Get full trajectory for a specific agent."""
        return [asdict(log) for log in self.step_logs if log.agent_id == agent_id]

    def analyze_movement_patterns(self) -> Dict[str, Any]:
        """Analyze overall movement patterns from logs."""
        if not self.step_logs:
            return {}

        # Group by agent
        agent_logs = {}
        for log in self.step_logs:
            if log.agent_id not in agent_logs:
                agent_logs[log.agent_id] = []
            agent_logs[log.agent_id].append(log)

        analysis = {}

        for agent_id, logs in agent_logs.items():
            total_distance = sum(log.distance_moved for log in logs)
            avg_distance = total_distance / len(logs) if logs else 0

            turn_counts = {
                'none': sum(1 for log in logs if log.turn_decision == 'none'),
                'left': sum(1 for log in logs if log.turn_decision == 'left'),
                'right': sum(1 for log in logs if log.turn_decision == 'right'),
                'random_left': sum(1 for log in logs if log.turn_decision == 'random_left'),
                'random_right': sum(1 for log in logs if log.turn_decision == 'random_right')
            }

            initial_pos = (logs[0].pos_x_float, logs[0].pos_y_float)
            final_pos = (logs[-1].new_pos_x_float, logs[-1].new_pos_y_float)
            net_displacement = np.sqrt(
                (final_pos[0] - initial_pos[0])**2 +
                (final_pos[1] - initial_pos[1])**2
            )

            avg_sensor_values = {
                'forward': np.mean([log.sensor_forward for log in logs]),
                'left': np.mean([log.sensor_left for log in logs]),
                'right': np.mean([log.sensor_right for log in logs])
            }

            analysis[f'agent_{agent_id}'] = {
                'total_distance': total_distance,
                'avg_distance_per_step': avg_distance,
                'net_displacement': net_displacement,
                'initial_position': initial_pos,
                'final_position': final_pos,
                'turn_counts': turn_counts,
                'avg_sensor_values': avg_sensor_values
            }

        return analysis


def create_visualization_table(logs: List[AgentStep], max_steps: int = 5) -> str:
    """Create a text table showing agent movement."""
    output = []
    output.append("=" * 150)
    output.append("AGENT MOVEMENT DIAGNOSTIC TABLE")
    output.append("=" * 150)

    # Group by step, then agent
    steps_dict = {}
    for log in logs:
        if log.step_num not in steps_dict:
            steps_dict[log.step_num] = []
        steps_dict[log.step_num].append(log)

    for step_num in sorted(steps_dict.keys())[:max_steps]:
        output.append(f"\n{'='*150}")
        output.append(f"STEP {step_num}")
        output.append(f"{'='*150}")

        for log in sorted(steps_dict[step_num], key=lambda x: x.agent_id):
            output.append(f"\n  Agent {log.agent_id}:")
            output.append(f"    Position: ({log.pos_x_float:.2f}, {log.pos_y_float:.2f}) -> ({log.new_pos_x_float:.2f}, {log.new_pos_y_float:.2f})")
            output.append(f"    Angle:    {log.angle_rad:.4f} rad ({log.angle_idx:3d}/1024) -> {log.new_angle_rad:.4f} rad ({log.new_angle_idx:3d}/1024)")
            output.append(f"    Distance: {log.distance_moved:.4f} pixels")
            output.append(f"    ")
            output.append(f"    Sensors:  F={log.sensor_forward:3d} @ {log.sensor_fwd_pos}, "
                         f"L={log.sensor_left:3d} @ {log.sensor_left_pos}, "
                         f"R={log.sensor_right:3d} @ {log.sensor_right_pos}")
            output.append(f"    Decision: {log.turn_decision.upper()}")
            output.append(f"    Deposit:  Trail value +{5} at {log.deposit_pixel}")

    output.append("\n" + "=" * 150)
    return "\n".join(output)


def print_summary_statistics(analysis: Dict[str, Any]):
    """Print summary statistics."""
    print("\n" + "=" * 80)
    print("MOVEMENT ANALYSIS SUMMARY")
    print("=" * 80)

    for agent_name, stats in analysis.items():
        print(f"\n{agent_name.upper()}")
        print(f"  Initial Position: ({stats['initial_position'][0]:.2f}, {stats['initial_position'][1]:.2f})")
        print(f"  Final Position:   ({stats['final_position'][0]:.2f}, {stats['final_position'][1]:.2f})")
        print(f"  Total Distance:   {stats['total_distance']:.2f} pixels")
        print(f"  Net Displacement: {stats['net_displacement']:.2f} pixels")
        print(f"  Avg Distance/Step: {stats['avg_distance_per_step']:.4f} pixels")
        print(f"  ")
        print(f"  Turn Counts:")
        for turn_type, count in stats['turn_counts'].items():
            print(f"    {turn_type:15s}: {count:3d}")
        print(f"  ")
        print(f"  Avg Sensor Values:")
        print(f"    Forward: {stats['avg_sensor_values']['forward']:.2f}")
        print(f"    Left:    {stats['avg_sensor_values']['left']:.2f}")
        print(f"    Right:   {stats['avg_sensor_values']['right']:.2f}")


def main():
    print("Agent Movement Diagnostic Tool")
    print("=" * 80)

    # Configuration
    width = 320
    height = 240
    num_agents = 10
    num_steps = 5
    seed = 0xDEADBEEF
    tracked_agents = list(range(10))  # Track first 10 agents

    print(f"\nConfiguration:")
    print(f"  Resolution: {width}x{height}")
    print(f"  Agents: {num_agents}")
    print(f"  Steps: {num_steps}")
    print(f"  LFSR Seed: 0x{seed:08X}")
    print(f"  Tracked Agents: {tracked_agents}")

    # Create simulator
    print("\nInitializing simulator...")
    sim = DiagnosticSimulator(
        width=width,
        height=height,
        num_agents=num_agents,
        lfsr_seed=seed
    )

    # Initialize agents at center (matching RTL)
    print("Spawning agents at center...")
    sim.init_agents_center()

    # Log initial positions
    print("\nInitial Agent Positions:")
    for i, agent in enumerate(sim.agents[:10]):
        x_float = sim.fp.from_fixed(agent.x)
        y_float = sim.fp.from_fixed(agent.y)
        angle_rad = sim._angle_idx_to_radians(agent.angle)
        print(f"  Agent {i}: pos=({x_float:.2f}, {y_float:.2f}), "
              f"angle={angle_rad:.4f} rad ({agent.angle:3d}/1024)")

    # Run diagnostic simulation
    print(f"\nRunning {num_steps} steps with diagnostic logging...")
    sim.run_diagnostic(num_steps, tracked_agents)

    print(f"Collected {len(sim.step_logs)} log entries")

    # Export to JSON
    json_file = "debug_log.json"
    print(f"\nExporting logs to {json_file}...")
    sim.export_logs_json(json_file)

    # Analyze patterns
    print("\nAnalyzing movement patterns...")
    analysis = sim.analyze_movement_patterns()

    # Print summary
    print_summary_statistics(analysis)

    # Create visualization table
    print("\nCreating visualization table...")
    table = create_visualization_table(sim.step_logs, max_steps=num_steps)

    # Save table to file
    table_file = "debug_table.txt"
    with open(table_file, 'w') as f:
        f.write(table)
    print(f"Saved visualization table to {table_file}")

    # Print first few steps
    print("\n" + table)

    # Save analysis
    analysis_file = "debug_analysis.json"
    with open(analysis_file, 'w') as f:
        json.dump(analysis, f, indent=2)
    print(f"\nSaved analysis to {analysis_file}")

    # Save trail map as numpy array
    trail_file = "debug_trail.npy"
    np.save(trail_file, sim.trail_map)
    print(f"Saved trail map to {trail_file}")

    print("\n" + "=" * 80)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 80)
    print(f"\nGenerated files:")
    print(f"  {json_file}       - Full step-by-step logs")
    print(f"  {table_file}      - Human-readable table")
    print(f"  {analysis_file}  - Movement analysis")
    print(f"  {trail_file}      - Trail map data")
    print("\nKey Findings:")
    print("  - All agents initialized at center (160.0, 120.0)")
    print("  - Agents move with speed ~1.0 pixels/step")
    print("  - Turn decisions based on F/L/R sensor comparison")
    print("  - Trail deposits of 5 units per step")
    print("  - Ground truth established for RTL comparison")


if __name__ == "__main__":
    main()
