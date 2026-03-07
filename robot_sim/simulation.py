from __future__ import annotations

from dataclasses import dataclass, field

from .environment import Environment
from .models import RobotState
from .planner import BFSPlanner
from .robot import Robot


@dataclass
class Simulation:
    environment: Environment
    robot: Robot
    max_steps: int = 300
    planner: BFSPlanner = field(default_factory=BFSPlanner)
    step_count: int = 0
    running: bool = False

    def reset(self, robot: Robot) -> None:
        self.robot = robot
        self.step_count = 0
        self.running = False

    def step(self) -> bool:
        if self.robot.state in {RobotState.FINISHED, RobotState.FAILED}:
            return False
        if self.step_count >= self.max_steps:
            self.robot.state = RobotState.FAILED
            return False

        self.robot.decide_and_act(self.environment, self.planner)
        self.step_count += 1
        return self.robot.state not in {RobotState.FINISHED, RobotState.FAILED}
