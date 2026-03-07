from __future__ import annotations

from collections import deque

from .environment import Environment
from .models import Point


class BFSPlanner:
    """Simple shortest-path planner for an unweighted grid."""

    def find_path(self, environment: Environment, start: Point, goal: Point) -> list[Point]:
        if start == goal:
            return [start]
        if not environment.is_free(start):
            return []
        if not environment.is_free(goal) and goal != environment.goal:
            return []

        frontier: deque[Point] = deque([start])
        came_from: dict[Point, Point | None] = {start: None}

        while frontier:
            current = frontier.popleft()
            if current == goal:
                return self._reconstruct_path(came_from, goal)

            for neighbor in environment.neighbors(current):
                if neighbor in came_from:
                    continue
                came_from[neighbor] = current
                frontier.append(neighbor)

        return []

    @staticmethod
    def _reconstruct_path(came_from: dict[Point, Point | None], goal: Point) -> list[Point]:
        path: list[Point] = []
        current: Point | None = goal
        while current is not None:
            path.append(current)
            current = came_from[current]
        path.reverse()
        return path
