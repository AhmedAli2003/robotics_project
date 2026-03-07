from __future__ import annotations

from dataclasses import dataclass, field

from .environment import Environment
from .models import Direction, Point, RobotState
from .planner import BFSPlanner


@dataclass
class Robot:
    position: Point
    direction: Direction = Direction.EAST
    state: RobotState = RobotState.IDLE
    path: list[Point] = field(default_factory=list)
    last_sensor: str = "UNKNOWN"

    def sense_ahead(self, environment: Environment) -> str:
        next_point = self.forward_point()
        if not environment.is_within_bounds(next_point):
            self.last_sensor = "WALL"
        elif environment.is_goal(next_point):
            self.last_sensor = "GOAL"
        elif environment.is_obstacle(next_point):
            self.last_sensor = "OBSTACLE"
        else:
            self.last_sensor = "CLEAR"
        return self.last_sensor

    def forward_point(self) -> Point:
        dx, dy = self.direction.delta()
        return Point(self.position.x + dx, self.position.y + dy)

    def turn_left(self) -> None:
        self.direction = self.direction.turn_left()

    def turn_right(self) -> None:
        self.direction = self.direction.turn_right()

    def _face_towards(self, target: Point) -> None:
        dx = target.x - self.position.x
        dy = target.y - self.position.y

        if dx == 1:
            self.direction = Direction.EAST
        elif dx == -1:
            self.direction = Direction.WEST
        elif dy == 1:
            self.direction = Direction.SOUTH
        elif dy == -1:
            self.direction = Direction.NORTH

    def move_forward(self, environment: Environment) -> bool:
        next_point = self.forward_point()
        if not environment.is_free(next_point) and not environment.is_goal(next_point):
            return False
        self.position = next_point
        return True

    def plan_path(self, environment: Environment, planner: BFSPlanner) -> bool:
        self.state = RobotState.PLANNING
        new_path = planner.find_path(environment, self.position, environment.goal)
        if not new_path:
            self.path = []
            self.state = RobotState.FAILED
            return False
        self.path = new_path
        self.state = RobotState.MOVING
        return True

    def decide_and_act(self, environment: Environment, planner: BFSPlanner) -> None:
        if environment.is_goal(self.position):
            self.state = RobotState.FINISHED
            return

        if not self.path or self.path[0] != self.position:
            if not self.plan_path(environment, planner):
                return

        if len(self.path) == 1:
            self.state = RobotState.FINISHED
            return

        next_target = self.path[1]
        self._face_towards(next_target)
        sensor = self.sense_ahead(environment)

        if sensor in {"OBSTACLE", "WALL"}:
            # Reactive obstacle avoidance through replanning.
            self.state = RobotState.AVOIDING
            if self.plan_path(environment, planner):
                # If we found a new path, wait until next step to follow it.
                return
            self.state = RobotState.FAILED
            return

        moved = self.move_forward(environment)
        if not moved:
            self.state = RobotState.AVOIDING
            self.plan_path(environment, planner)
            return

        # Drop the old current node from the planned path.
        if len(self.path) >= 2 and self.path[1] == self.position:
            self.path = self.path[1:]
        else:
            # Fallback if the path was externally invalidated.
            self.plan_path(environment, planner)
            return

        if environment.is_goal(self.position):
            self.state = RobotState.FINISHED
        else:
            self.state = RobotState.MOVING
