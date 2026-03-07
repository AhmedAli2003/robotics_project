# Virtual Autonomous Robot Simulation (Python)

A structured Python project for simulating a **virtual autonomous robot** in a **2D coordinate-based environment**.

This project was built to satisfy the requirements of a Robotics Programming final project using only student-implemented logic. It includes a **simple GUI**, **BFS path planning**, **Finite State Machine (FSM) behavior**, and **reactive obstacle avoidance**.

---

## 1. Project Summary

The program simulates a robot moving inside a 2D map.

- The robot has a position `(x, y)` and a facing direction.
- Obstacles are stored separately as a **set of coordinates**.
- The environment has boundaries and a target goal.
- The robot plans a path to the goal using **Breadth-First Search (BFS)**.
- The robot changes behavior using **FSM states** such as planning, moving, avoiding, and finished.
- If the path becomes blocked, the robot reacts by entering obstacle-avoidance mode and re-planning.
- A **Tkinter GUI** visualizes the environment, robot, path, metrics, and event log.

This is a **software-only simulation**. No hardware or external robotics libraries are used.

---

## 2. Main Features

### Mandatory Requirements Implemented

#### 2.1 2D Environment
- Coordinate-based environment using `(x, y)` points
- Adjustable grid size through code
- Environment boundaries
- Obstacles stored as a `set[Point]`
- Goal location stored as a `Point`

#### 2.2 Robot Model
- Robot position
- Robot orientation (`NORTH`, `EAST`, `SOUTH`, `WEST`)
- Internal state represented by FSM
- Path memory and last sensor reading

#### 2.3 Movement System
- Move forward
- Turn implicitly by changing facing direction toward the next planned node
- Collision prevention before movement
- Boundary checking

#### 2.4 Decision-Making Logic
- Rule-based decision making
- Decisions based on environment state and virtual sensing
- Dynamic re-planning when an obstacle blocks the next step

#### 2.5 Simulation Loop
- Step-by-step execution
- Automatic run mode and manual step mode
- Continuous state refresh in the GUI
- Maximum step limit to prevent infinite execution

---

## 3. Extension Tracks Implemented

This project includes more than the minimum required two extension tracks.

### 3.1 Path Planning — BFS
- A BFS planner computes the shortest path in an unweighted 2D grid.
- The robot uses the planned route to travel from start to goal.

### 3.2 Finite State Machine (FSM)
The robot behavior is controlled by these states:
- `IDLE`
- `PLANNING`
- `MOVING`
- `AVOIDING`
- `FINISHED`
- `FAILED`

### 3.3 Obstacle Avoidance
- The robot senses the cell ahead.
- If an obstacle or wall blocks the next step, it switches to `AVOIDING`.
- It then re-plans a new path from the current position.
- The GUI also allows the user to add or remove obstacles during the simulation, which triggers reactive re-planning.

### 3.4 User Interface
- Built with **Tkinter**
- Visual simulation board
- Control dashboard
- Event log
- Live metrics
- Manual and automatic execution

---

## 4. Algorithms and Design

### 4.1 Coordinate-Based Environment
Instead of storing the map as a 2D matrix of cell types, this project stores only important spatial data:

- `width`, `height`
- `goal: Point`
- `obstacles: set[Point]`

This makes the representation simple and matches the assignment request for a coordinate-based design.

### 4.2 BFS Path Planning
The planner uses **Breadth-First Search** because the environment is an unweighted grid.

Why BFS is appropriate here:
- every move has the same cost
- BFS guarantees the shortest path in number of steps
- it is simple and easy to explain
- it is suitable for an educational robotics simulation

High-level BFS process:
1. Start from the robot's current position.
2. Explore all reachable neighboring cells level by level.
3. Track each node's predecessor using `came_from`.
4. Once the goal is found, reconstruct the path.
5. Return the shortest path as a list of `Point` objects.

### 4.3 FSM Behavior
The robot behavior is intentionally state-based.

Typical transitions:
- `IDLE -> PLANNING`
- `PLANNING -> MOVING`
- `MOVING -> AVOIDING`
- `AVOIDING -> PLANNING`
- `MOVING -> FINISHED`
- `PLANNING -> FAILED`

This makes the robot behavior clear, structured, and easier to debug.

### 4.4 Virtual Sensor Logic
The robot senses only the cell directly in front of it.

Possible sensor readings:
- `CLEAR`
- `OBSTACLE`
- `WALL`
- `GOAL`

This sensor information helps the robot decide whether to move or switch to obstacle avoidance.

### 4.5 Obstacle Avoidance Strategy
Obstacle avoidance is implemented reactively.

Behavior:
- The robot follows the BFS path.
- Before moving, it checks the next cell ahead.
- If the next cell is blocked or outside bounds, the robot enters `AVOIDING`.
- The old path is invalidated.
- The robot computes a fresh BFS path from its current position.

This strategy is simple and effective for a student project.

---

## 5. Project Structure

```text
virtual_robot_project/
├── main.py
├── README.md
└── robot_sim/
    ├── __init__.py
    ├── environment.py
    ├── gui.py
    ├── models.py
    ├── planner.py
    ├── robot.py
    └── simulation.py
```

### File Descriptions

#### `main.py`
- Builds the demo environment
- Creates the robot
- Starts the Tkinter application

#### `robot_sim/models.py`
Contains core data models and enums:
- `Point`
- `Direction`
- `RobotState`

#### `robot_sim/environment.py`
Implements the environment:
- bounds checking
- obstacle handling
- goal checking
- free-cell checking
- neighbor generation for BFS

#### `robot_sim/planner.py`
Contains the `BFSPlanner` class:
- shortest-path search
- path reconstruction

#### `robot_sim/robot.py`
Implements robot behavior:
- sensing
- movement
- turning/orientation updates
- path planning integration
- FSM-driven decision making

#### `robot_sim/simulation.py`
Controls execution:
- simulation stepping
- max-step handling
- reset behavior
- run/stop state

#### `robot_sim/gui.py`
Implements the GUI:
- visualization board
- status cards
- controls
- obstacle interaction
- event log
- speed control

---

## 6. GUI Overview

The GUI is intentionally simple but more polished than a basic classroom demo.

### Main GUI Features
- visual grid board
- colored start cell
- colored goal cell
- red obstacle cells
- robot shown as a directional marker
- drawn BFS path
- control buttons
- event log
- hover cell information
- speed slider
- status metrics panel

### Controls
- **Start**: run the simulation automatically
- **Pause**: stop automatic execution
- **Step**: execute one simulation step manually
- **Reset**: restore the original map and initial robot state

### Mouse Interaction
- **Left click on a cell**: add or remove an obstacle
- the robot will re-plan if the change affects its route

---

## 7. How the Simulation Works

At each simulation step:
1. The simulation checks whether the robot is already finished or failed.
2. The robot decides what to do.
3. If needed, it plans a path using BFS.
4. It faces the next target node in the path.
5. It senses the cell ahead.
6. If clear, it moves forward.
7. If blocked, it enters `AVOIDING` and re-plans.
8. If it reaches the goal, the state becomes `FINISHED`.
9. If no path exists or max steps are exceeded, the state becomes `FAILED`.

---

## 8. Requirements

### Python Version
Recommended:
- **Python 3.11+**

The project uses only the Python standard library:
- `tkinter`
- `dataclasses`
- `enum`
- `collections`
- `copy`

No external packages are required.

---

## 9. How to Run

### Option 1: Run from terminal
```bash
cd virtual_robot_project
python main.py
```

### Option 2: Run from an IDE
Open the project folder in your IDE and run:
- `main.py`

---

## 10. Demo Scenario Included

The provided demo starts with:
- a predefined environment size
- a predefined start position
- a predefined goal
- several static obstacles already placed

This lets the program show BFS planning and movement immediately after launch.

You can also interactively modify the obstacle map during execution from the GUI.

---

## 11. Sample Behavior

A typical run looks like this:
- the robot starts in `IDLE`
- it enters `PLANNING`
- BFS computes a shortest path to the goal
- the robot switches to `MOVING`
- if the user adds an obstacle on the route, the robot switches to `AVOIDING`
- it re-plans around the obstacle
- it continues moving
- once it reaches the goal, it enters `FINISHED`

---

## 12. Mapping to Assignment Requirements

### Core Requirements
| Requirement | Implemented | Notes |
|---|---|---|
| 2D environment | Yes | Coordinate-based `(x, y)` world |
| Boundaries and obstacles | Yes | Boundaries checked, obstacles stored as coordinates |
| Robot position and orientation | Yes | `Point` + `Direction` |
| Internal state | Yes | FSM states implemented |
| Movement commands | Yes | Forward movement with directional updates |
| Collision prevention | Yes | Checks before movement |
| Decision-making logic | Yes | Rule-based robot control |
| Virtual sensing | Yes | Front-cell sensing |
| Simulation loop | Yes | Manual and automatic stepping |
| Clear state updates | Yes | GUI status + event log |

### Extension Tracks
| Extension Track | Implemented | Notes |
|---|---|---|
| Path Planning | Yes | BFS shortest path |
| Obstacle Avoidance | Yes | Reactive re-planning |
| FSM | Yes | Clear robot states and transitions |
| User Interface | Yes | Tkinter GUI |

---

## 13. Design Choices

This project intentionally chooses the simplest reliable solutions that still satisfy the assignment strongly.

### Why coordinate-based storage?
It directly matches the project request and keeps the environment logic clean.

### Why BFS instead of A* or Dijkstra?
Because the grid is unweighted, BFS is sufficient and guarantees the shortest path with simpler code.

### Why Tkinter?
It is built into Python, lightweight, and appropriate for a simple GUI.

### Why reactive obstacle avoidance?
It is easier to explain and implement than predictive avoidance while still demonstrating intelligent behavior.

---

## 14. Limitations

This is an educational simulation, so some simplifications were made:
- only one robot is simulated
- the robot senses only the cell ahead
- movement is grid-based, not continuous physics-based motion
- all moves have equal cost
- obstacle avoidance is reactive rather than predictive
- no advanced machine learning or robotics frameworks are used

These limitations are acceptable for the scope of the assignment.

---

## 15. Possible Future Improvements

Possible extensions for future work:
- multiple robots
- A* path planning for heuristic-based search
- replay system for finished simulations
- save/load map layouts
- random map generation
- different terrain costs with Dijkstra
- richer sensor model
- animated robot transitions

---

## 16. Conclusion

This project demonstrates how a virtual robot can be modeled and controlled using clean Python code, classic algorithms, and state-based behavior.

It fulfills the mandatory assignment requirements and includes multiple extension tracks:
- **BFS path planning**
- **FSM-controlled behavior**
- **Obstacle avoidance**
- **Simple GUI visualization**

The result is a complete, understandable, and presentation-ready robotics programming project.
