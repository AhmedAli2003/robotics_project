from __future__ import annotations

import tkinter as tk

from robot_sim.environment import Environment
from robot_sim.gui import RobotApp
from robot_sim.models import Direction, Point
from robot_sim.robot import Robot
from robot_sim.simulation import Simulation


def build_demo_environment() -> tuple[Environment, Robot]:
    width, height = 12, 10
    goal = Point(10, 7)
    obstacles = {
        Point(3, 0), Point(3, 1), Point(3, 2), Point(3, 3), Point(3, 4),
        Point(6, 2), Point(7, 2), Point(8, 2),
        Point(6, 3),
        Point(6, 4), Point(7, 4), Point(8, 4),
        Point(1, 7), Point(2, 7), Point(3, 7), Point(4, 7),
        Point(8, 6), Point(8, 7), Point(8, 8),
    }
    environment = Environment(width=width, height=height, goal=goal, obstacles=obstacles)
    robot = Robot(position=Point(0, 0), direction=Direction.EAST)
    return environment, robot


def main() -> None:
    environment, robot = build_demo_environment()
    simulation = Simulation(environment=environment, robot=robot, max_steps=300)

    root = tk.Tk()
    root.geometry("1150x760")
    root.minsize(1050, 700)
    app = RobotApp(root=root, simulation=simulation, start_robot=robot)
    app.refresh()
    root.mainloop()


if __name__ == "__main__":
    main()
