from __future__ import annotations

from dataclasses import dataclass, field

from .models import Point


@dataclass
class Environment:
    width: int
    height: int
    goal: Point
    obstacles: set[Point] = field(default_factory=set)

    def is_within_bounds(self, point: Point) -> bool:
        return 0 <= point.x < self.width and 0 <= point.y < self.height

    def is_obstacle(self, point: Point) -> bool:
        return point in self.obstacles

    def is_goal(self, point: Point) -> bool:
        return point == self.goal

    def is_free(self, point: Point) -> bool:
        return self.is_within_bounds(point) and not self.is_obstacle(point)

    def add_obstacle(self, point: Point) -> bool:
        if point == self.goal:
            return False
        if not self.is_within_bounds(point):
            return False
        self.obstacles.add(point)
        return True

    def remove_obstacle(self, point: Point) -> bool:
        if point in self.obstacles:
            self.obstacles.remove(point)
            return True
        return False

    def toggle_obstacle(self, point: Point, blocked_points: set[Point] | None = None) -> bool:
        blocked_points = blocked_points or set()
        if point in blocked_points or point == self.goal:
            return False
        if point in self.obstacles:
            self.obstacles.remove(point)
        else:
            self.obstacles.add(point)
        return True

    def neighbors(self, point: Point) -> list[Point]:
        candidates = [
            Point(point.x, point.y - 1),
            Point(point.x + 1, point.y),
            Point(point.x, point.y + 1),
            Point(point.x - 1, point.y),
        ]
        return [candidate for candidate in candidates if self.is_free(candidate)]
