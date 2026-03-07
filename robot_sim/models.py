from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True, slots=True)
class Point:
    x: int
    y: int


class Direction(Enum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

    def turn_left(self) -> "Direction":
        return Direction((self.value - 1) % 4)

    def turn_right(self) -> "Direction":
        return Direction((self.value + 1) % 4)

    def delta(self) -> tuple[int, int]:
        return {
            Direction.NORTH: (0, -1),
            Direction.EAST: (1, 0),
            Direction.SOUTH: (0, 1),
            Direction.WEST: (-1, 0),
        }[self]


class RobotState(Enum):
    IDLE = "IDLE"
    PLANNING = "PLANNING"
    MOVING = "MOVING"
    AVOIDING = "AVOIDING"
    FINISHED = "FINISHED"
    FAILED = "FAILED"
