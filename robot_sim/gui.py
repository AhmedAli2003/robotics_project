from __future__ import annotations

import tkinter as tk
from copy import deepcopy
from dataclasses import dataclass

from .models import Direction, Point, RobotState
from .robot import Robot
from .simulation import Simulation


@dataclass
class AppConfig:
    cell_size: int = 40
    panel_width: int = 320
    delay_ms: int = 220
    min_delay_ms: int = 60
    max_delay_ms: int = 900


class RobotApp:
    def __init__(self, root: tk.Tk, simulation: Simulation, start_robot: Robot, config: AppConfig | None = None):
        self.root = root
        self.root.title("Virtual Robot Control Center")
        self.root.configure(bg="#0b1220")

        self.simulation = simulation
        self.start_robot = deepcopy(start_robot)
        self.initial_obstacles = set(simulation.environment.obstacles)
        self.config = config or AppConfig()
        self._after_id: str | None = None
        self._last_status_key: tuple | None = None

        self.status_var = tk.StringVar()
        self.sensor_var = tk.StringVar()
        self.steps_var = tk.StringVar()
        self.position_var = tk.StringVar()
        self.direction_var = tk.StringVar()
        self.path_var = tk.StringVar()
        self.hover_var = tk.StringVar(value="Hover a cell to inspect it")
        self.mode_var = tk.StringVar(value="Paused")
        self.speed_var = tk.IntVar(value=self.config.delay_ms)
        self.obstacles_var = tk.StringVar()

        self._build_layout()
        self.refresh(full=True)
        self._log("Interface ready. You can start the simulation or edit obstacles.")

    # =========================
    # Layout
    # =========================
    def _build_layout(self) -> None:
        env = self.simulation.environment
        canvas_width = env.width * self.config.cell_size
        canvas_height = env.height * self.config.cell_size

        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=0)

        header = tk.Frame(self.root, bg="#111827", height=70)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=14, pady=(14, 10))
        header.grid_columnconfigure(0, weight=1)

        tk.Label(
            header,
            text="Virtual Robot Control Center",
            font=("Segoe UI", 18, "bold"),
            fg="#f8fafc",
            bg="#111827",
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 0))
        tk.Label(
            header,
            text="BFS path planning • FSM robot states • reactive obstacle avoidance",
            font=("Segoe UI", 10),
            fg="#94a3b8",
            bg="#111827",
        ).grid(row=1, column=0, sticky="w", padx=16, pady=(2, 12))

        board = tk.Frame(self.root, bg="#0b1220")
        board.grid(row=1, column=0, sticky="nsew", padx=(14, 10), pady=(0, 14))
        board.rowconfigure(0, weight=1)
        board.columnconfigure(0, weight=1)

        canvas_card = tk.Frame(board, bg="#111827", bd=0, highlightthickness=1, highlightbackground="#1f2937")
        canvas_card.grid(row=0, column=0, sticky="nsew")
        canvas_card.rowconfigure(1, weight=1)
        canvas_card.columnconfigure(0, weight=1)

        top_strip = tk.Frame(canvas_card, bg="#0f172a", height=36)
        top_strip.grid(row=0, column=0, sticky="ew")
        top_strip.grid_columnconfigure(0, weight=1)
        tk.Label(
            top_strip,
            textvariable=self.hover_var,
            fg="#cbd5e1",
            bg="#0f172a",
            font=("Consolas", 10),
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=12, pady=8)

        self.canvas = tk.Canvas(
            canvas_card,
            width=canvas_width,
            height=canvas_height,
            bg="#0b1020",
            highlightthickness=0,
            bd=0,
        )
        self.canvas.grid(row=1, column=0, padx=14, pady=14)
        self.canvas.bind("<Button-1>", self.on_left_click)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Leave>", lambda _e: self.hover_var.set("Hover a cell to inspect it"))

        side = tk.Frame(self.root, bg="#0b1220", width=self.config.panel_width)
        side.grid(row=1, column=1, sticky="ns", padx=(0, 14), pady=(0, 14))
        side.grid_propagate(False)
        side.columnconfigure(0, weight=1)

        controls_card, controls = self._section(side, "Controls")
        controls_card.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        controls.columnconfigure((0, 1), weight=1)

        self._make_button(controls, "Start", self.start, "#16a34a").grid(row=0, column=0, sticky="ew", padx=(0, 6), pady=(0, 8))
        self._make_button(controls, "Pause", self.pause, "#b45309").grid(row=0, column=1, sticky="ew", padx=(6, 0), pady=(0, 8))
        self._make_button(controls, "Step", self.step_once, "#2563eb").grid(row=1, column=0, sticky="ew", padx=(0, 6))
        self._make_button(controls, "Reset", self.reset, "#7c3aed").grid(row=1, column=1, sticky="ew", padx=(6, 0))

        tk.Label(
            controls,
            text="Simulation speed (milliseconds per step)",
            bg="#111827",
            fg="#cbd5e1",
            font=("Segoe UI", 9),
            anchor="w",
        ).grid(row=2, column=0, columnspan=2, sticky="ew", pady=(12, 4))

        scale = tk.Scale(
            controls,
            from_=self.config.max_delay_ms,
            to=self.config.min_delay_ms,
            orient="horizontal",
            variable=self.speed_var,
            command=self.on_speed_change,
            showvalue=True,
            troughcolor="#1f2937",
            bg="#111827",
            fg="#e5e7eb",
            highlightthickness=0,
            activebackground="#38bdf8",
            font=("Segoe UI", 9),
        )
        scale.grid(row=3, column=0, columnspan=2, sticky="ew")

        status_card, status = self._section(side, "Live Status")
        status_card.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        self._make_metric(status, "Mode", self.mode_var).grid(row=0, column=0, sticky="ew")
        self._make_metric(status, "State", self.status_var).grid(row=1, column=0, sticky="ew")
        self._make_metric(status, "Sensor", self.sensor_var).grid(row=2, column=0, sticky="ew")
        self._make_metric(status, "Direction", self.direction_var).grid(row=3, column=0, sticky="ew")
        self._make_metric(status, "Position", self.position_var).grid(row=4, column=0, sticky="ew")
        self._make_metric(status, "Path Nodes", self.path_var).grid(row=5, column=0, sticky="ew")
        self._make_metric(status, "Steps", self.steps_var).grid(row=6, column=0, sticky="ew")
        self._make_metric(status, "Obstacles", self.obstacles_var).grid(row=7, column=0, sticky="ew")

        legend_card, legend = self._section(side, "Legend")
        legend_card.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        legend.columnconfigure(1, weight=1)
        legend_items = [
            ("#1d4ed8", "Planned BFS path"),
            ("#22c55e", "Goal"),
            ("#ef4444", "Obstacle"),
            ("#38bdf8", "Robot"),
            ("#f59e0b", "Start position"),
        ]
        for idx, (color, text) in enumerate(legend_items):
            swatch = tk.Canvas(legend, width=18, height=18, bg="#111827", highlightthickness=0)
            swatch.grid(row=idx, column=0, sticky="w", pady=4)
            swatch.create_rectangle(2, 2, 16, 16, fill=color, outline="")
            tk.Label(legend, text=text, bg="#111827", fg="#cbd5e1", font=("Segoe UI", 9)).grid(
                row=idx, column=1, sticky="w", padx=8, pady=4
            )

        log_card, log_section = self._section(side, "Event Log")
        log_card.grid(row=3, column=0, sticky="nsew")
        side.rowconfigure(3, weight=1)

        self.log_list = tk.Listbox(
            log_section,
            height=10,
            bg="#0f172a",
            fg="#dbeafe",
            selectbackground="#1d4ed8",
            selectforeground="#ffffff",
            activestyle="none",
            borderwidth=0,
            highlightthickness=0,
            font=("Consolas", 9),
        )
        self.log_list.grid(row=0, column=0, sticky="nsew")
        scrollbar = tk.Scrollbar(log_section, orient="vertical", command=self.log_list.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.log_list.configure(yscrollcommand=scrollbar.set)
        log_section.rowconfigure(0, weight=1)
        log_section.columnconfigure(0, weight=1)

    def _section(self, parent: tk.Widget, title: str) -> tuple[tk.Frame, tk.Frame]:
        frame = tk.Frame(parent, bg="#111827", highlightthickness=1, highlightbackground="#1f2937")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        tk.Label(
            frame,
            text=title,
            bg="#111827",
            fg="#f8fafc",
            font=("Segoe UI", 11, "bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 8))
        content = tk.Frame(frame, bg="#111827")
        content.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        return frame, content

    def _make_button(self, parent: tk.Widget, text: str, command, color: str) -> tk.Button:
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg="#ffffff",
            activebackground=color,
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            padx=12,
            pady=10,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
        )

    def _make_metric(self, parent: tk.Widget, label: str, variable: tk.StringVar) -> tk.Frame:
        frame = tk.Frame(parent, bg="#0f172a")
        tk.Label(frame, text=label, bg="#0f172a", fg="#93c5fd", font=("Segoe UI", 9, "bold"), width=10, anchor="w").pack(
            side="left", padx=(10, 8), pady=6
        )
        tk.Label(frame, textvariable=variable, bg="#0f172a", fg="#e5e7eb", font=("Consolas", 10), anchor="w").pack(
            side="left", fill="x", expand=True, padx=(0, 10), pady=6
        )
        return frame

    # =========================
    # Drawing
    # =========================
    def grid_to_pixel(self, point: Point) -> tuple[int, int, int, int]:
        x1 = point.x * self.config.cell_size
        y1 = point.y * self.config.cell_size
        x2 = x1 + self.config.cell_size
        y2 = y1 + self.config.cell_size
        return x1, y1, x2, y2

    def draw_grid(self) -> None:
        env = self.simulation.environment
        self.canvas.delete("all")

        # Outer board background.
        self.canvas.create_rectangle(
            0,
            0,
            env.width * self.config.cell_size,
            env.height * self.config.cell_size,
            fill="#0b1020",
            outline="",
        )

        for y in range(env.height):
            for x in range(env.width):
                point = Point(x, y)
                x1, y1, x2, y2 = self.grid_to_pixel(point)
                fill = "#111827"
                outline = "#243041"

                if point in env.obstacles:
                    fill = "#ef4444"
                    outline = "#b91c1c"
                elif point == env.goal:
                    fill = "#22c55e"
                    outline = "#15803d"
                elif point == self.start_robot.position:
                    fill = "#f59e0b"
                    outline = "#b45309"

                self.canvas.create_rectangle(x1 + 1, y1 + 1, x2 - 1, y2 - 1, fill=fill, outline=outline, width=1)

                if point == env.goal:
                    self.canvas.create_text(
                        (x1 + x2) / 2,
                        (y1 + y2) / 2,
                        text="GOAL",
                        fill="#052e16",
                        font=("Segoe UI", 9, "bold"),
                    )
                elif point == self.start_robot.position:
                    self.canvas.create_text(
                        (x1 + x2) / 2,
                        (y1 + y2) / 2,
                        text="START",
                        fill="#3b1d00",
                        font=("Segoe UI", 8, "bold"),
                    )
                elif point in env.obstacles:
                    self.canvas.create_line(x1 + 8, y1 + 8, x2 - 8, y2 - 8, fill="#fee2e2", width=2)
                    self.canvas.create_line(x2 - 8, y1 + 8, x1 + 8, y2 - 8, fill="#fee2e2", width=2)

        self.draw_path()
        self.draw_robot()
        self.draw_coordinates()

    def draw_coordinates(self) -> None:
        env = self.simulation.environment
        for x in range(env.width):
            self.canvas.create_text(
                x * self.config.cell_size + self.config.cell_size / 2,
                10,
                text=str(x),
                fill="#475569",
                font=("Consolas", 8),
            )
        for y in range(env.height):
            self.canvas.create_text(
                10,
                y * self.config.cell_size + self.config.cell_size / 2,
                text=str(y),
                fill="#475569",
                font=("Consolas", 8),
            )

    def draw_path(self) -> None:
        robot = self.simulation.robot
        if len(robot.path) < 2:
            return

        points: list[int] = []
        for node in robot.path:
            center_x = node.x * self.config.cell_size + self.config.cell_size // 2
            center_y = node.y * self.config.cell_size + self.config.cell_size // 2
            points.extend([center_x, center_y])

        self.canvas.create_line(*points, fill="#1d4ed8", width=4, smooth=True)
        for node in robot.path[1:-1]:
            cx = node.x * self.config.cell_size + self.config.cell_size // 2
            cy = node.y * self.config.cell_size + self.config.cell_size // 2
            self.canvas.create_oval(cx - 4, cy - 4, cx + 4, cy + 4, fill="#93c5fd", outline="")

    def draw_robot(self) -> None:
        robot = self.simulation.robot
        x1, y1, x2, y2 = self.grid_to_pixel(robot.position)
        pad = 8

        # Cell glow / focus ring.
        self.canvas.create_rectangle(x1 + 2, y1 + 2, x2 - 2, y2 - 2, outline="#67e8f9", width=2)

        if robot.direction == Direction.NORTH:
            points = [(x1 + x2) / 2, y1 + pad, x1 + pad, y2 - pad, x2 - pad, y2 - pad]
        elif robot.direction == Direction.SOUTH:
            points = [x1 + pad, y1 + pad, x2 - pad, y1 + pad, (x1 + x2) / 2, y2 - pad]
        elif robot.direction == Direction.EAST:
            points = [x1 + pad, y1 + pad, x2 - pad, (y1 + y2) / 2, x1 + pad, y2 - pad]
        else:
            points = [x2 - pad, y1 + pad, x2 - pad, y2 - pad, x1 + pad, (y1 + y2) / 2]

        color = {
            RobotState.IDLE: "#f59e0b",
            RobotState.PLANNING: "#a855f7",
            RobotState.MOVING: "#38bdf8",
            RobotState.AVOIDING: "#fb7185",
            RobotState.FINISHED: "#22c55e",
            RobotState.FAILED: "#111827",
        }[robot.state]

        self.canvas.create_oval(x1 + 7, y1 + 7, x2 - 7, y2 - 7, fill="#082f49", outline="")
        self.canvas.create_polygon(points, fill=color, outline="#e2e8f0", width=2)

    # =========================
    # Refresh and state updates
    # =========================
    def refresh(self, full: bool = False) -> None:
        self.draw_grid()
        robot = self.simulation.robot
        self.status_var.set(robot.state.value)
        self.sensor_var.set(robot.last_sensor)
        self.steps_var.set(f"{self.simulation.step_count} / {self.simulation.max_steps}")
        self.position_var.set(f"({robot.position.x}, {robot.position.y})")
        self.direction_var.set(robot.direction.name)
        self.path_var.set(str(max(len(robot.path) - 1, 0)))
        self.obstacles_var.set(str(len(self.simulation.environment.obstacles)))
        self.mode_var.set("Running" if self.simulation.running else "Paused")

        status_key = (
            robot.state.value,
            robot.position,
            robot.direction.name,
            robot.last_sensor,
            len(robot.path),
            self.simulation.step_count,
        )
        if full or status_key != self._last_status_key:
            self._last_status_key = status_key
            self._log(
                f"step={self.simulation.step_count:03d}  state={robot.state.value:<8}  pos=({robot.position.x},{robot.position.y})  dir={robot.direction.name:<5}  sensor={robot.last_sensor}"
            )

    def _log(self, message: str) -> None:
        self.log_list.insert(tk.END, message)
        self.log_list.yview_moveto(1.0)
        if self.log_list.size() > 200:
            self.log_list.delete(0)

    # =========================
    # Controls
    # =========================
    def start(self) -> None:
        if self.simulation.robot.state in {RobotState.FINISHED, RobotState.FAILED}:
            self._log("Simulation cannot resume because it has already ended. Press Reset.")
            return
        self.simulation.running = True
        self.mode_var.set("Running")
        self._log("Simulation started.")
        self._schedule_next()

    def _schedule_next(self) -> None:
        if not self.simulation.running:
            return
        self.step_once(schedule_next=True)

    def pause(self) -> None:
        self.simulation.running = False
        self.mode_var.set("Paused")
        if self._after_id is not None:
            self.root.after_cancel(self._after_id)
            self._after_id = None
        self._log("Simulation paused.")

    def step_once(self, schedule_next: bool = False) -> None:
        active = self.simulation.step()
        self.refresh()

        if schedule_next and self.simulation.running and active:
            self._after_id = self.root.after(self.config.delay_ms, self._schedule_next)
        else:
            self.simulation.running = False if not active else self.simulation.running
            self.mode_var.set("Running" if self.simulation.running else "Paused")
            if not active:
                self._log(f"Simulation ended with state {self.simulation.robot.state.value}.")

    def reset(self) -> None:
        self.pause()
        self.simulation.environment.obstacles = set(self.initial_obstacles)
        self.simulation.reset(deepcopy(self.start_robot))
        self.simulation.robot.state = RobotState.IDLE
        self.simulation.robot.path = []
        self.simulation.robot.last_sensor = "UNKNOWN"
        self.refresh(full=True)
        self._log("Simulation reset to the initial map and robot position.")

    def on_speed_change(self, _value: str) -> None:
        self.config.delay_ms = int(self.speed_var.get())

    # =========================
    # Interaction
    # =========================
    def on_left_click(self, event: tk.Event) -> None:
        x = event.x // self.config.cell_size
        y = event.y // self.config.cell_size
        point = Point(x, y)
        env = self.simulation.environment

        blocked_points = {self.simulation.robot.position, self.start_robot.position}
        changed = env.toggle_obstacle(point, blocked_points=blocked_points)
        if not changed:
            self._log(f"Ignored obstacle toggle at ({x}, {y}).")
            return

        robot = self.simulation.robot
        if robot.state not in {RobotState.FINISHED, RobotState.FAILED}:
            robot.state = RobotState.AVOIDING
            robot.path = []
            self._log(f"Obstacle map updated at ({x}, {y}); robot will re-plan.")
        else:
            self._log(f"Obstacle map updated at ({x}, {y}).")
        self.refresh(full=True)

    def on_mouse_move(self, event: tk.Event) -> None:
        x = event.x // self.config.cell_size
        y = event.y // self.config.cell_size
        env = self.simulation.environment
        point = Point(x, y)
        if not env.is_within_bounds(point):
            self.hover_var.set("Outside the map")
            return

        tags: list[str] = []
        if point == self.simulation.robot.position:
            tags.append("robot")
        if point == self.start_robot.position:
            tags.append("start")
        if point == env.goal:
            tags.append("goal")
        if point in env.obstacles:
            tags.append("obstacle")
        if not tags:
            tags.append("free")
        self.hover_var.set(f"Cell ({x}, {y}) • {' • '.join(tags)}")
