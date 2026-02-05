#!/usr/bin/env python3
# Focus Flow - Pomodoro App with To-Do List
# Req: pip install pygame-ce==2.5.6
"""Required imports"""
import os
import sys
import json
import random
import threading
import tkinter as tk
from enum import Enum
from typing import List
from datetime import datetime, timedelta
from dataclasses import dataclass
from tkinter import simpledialog, messagebox
import pygame as pg

# Set working directory
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

# Config
APP_TITLE = "Focus Flow - Pomodoro To-Do App"
APP_ICON = "media/images/to-do-list2.png"
SAVE_PATH = "cfg/state.json"
CONFIG_PATH = "cfg/config.json"
STATS_PATH = "cfg/stats.json"
SOUND_DIR = "media/alarms/"
BASE_W, BASE_H = 560, 720
FPS = 60
DEFAULT_POMODORO = 25 * 60

# Colors
COLOR_BG = (40, 40, 40)
COLOR_TEXT = (220, 220, 220)
COLOR_TEXTDARK = (240, 240, 240)
COLOR_DIM = (150, 150, 150)
COLOR_TASK_HIGHLIGHT = (70, 140, 80)
COLOR_DONE = (90, 160, 90)
COLOR_WARN = (200, 80, 80)
COLOR_BREAK = (100, 150, 200)
COLOR_BTN = (70, 70, 70)
COLOR_BTN_HOVER = (100, 100, 100)
COLOR_BOX = (120, 120, 120)

# Motivational Quotes
QUOTES = [
    "Great work, take a breath.",
    "Stop, stretch, get a glass of water, you earned it!",
    "Consistency beats intensity every time.",
    "Level up complete.",
    "It's not about perfect. It's about effort.",
    "Progress, not perfection.",
    "Small wins build empires.",
    "Keep the streak.",
    "Discipline is choosing between what you want now and what you want most.",
    "You don't have to be great to start, but you have to start to be great.",
    "Task crushed. Next.",
    "Success is the sum of small efforts repeated day in and day out.",
    "Great things never come from comfort zones.",
    "You don't find the time to do it. You make the time.",
    "Another commit pushed.",
    "Success is going from failure to failure without loss of enthusiasm.",
    "The successful warrior is the average man, with laser-like focus.",
    "Do not let what you cannot do interfere with what you can do.",
]

# Models
class AppMode(Enum):
    """Application modes/screens"""
    SPLASH = 1
    MAIN = 2
    INSTRUCTIONS = 3
    STATS = 4

@dataclass
class Task:
    """A task item"""
    text: str
    complete: bool = False
    score: int = 10

class PomodoroTimer:
    """Manages the Pomodoro timer state and logic"""
    def __init__(self):
        self.total = DEFAULT_POMODORO
        self.remaining = self.total
        self.running = False
        self.session_count = 1
        self.is_break = False
        self.sessions_completed = 0
        self.custom_break = 5
        self.default_session = DEFAULT_POMODORO

    def start(self) -> None:
        """Start timer"""
        self.running = True

    def stop(self) -> None:
        """Stop timer"""
        self.running = False

    def reset(self, total=None) -> None:
        """Reset timer"""
        self.total = total if total is not None else self.total
        self.remaining = self.total
        self.running = False

    def reset_full(self) -> None:
        """Full reset to default pomodoro"""
        self.total = self.default_session
        self.remaining = self.total
        self.running = False
        self.is_break = False
        self.session_count = 1

    def update(self, dt) -> bool:
        """Update dt"""
        if not self.running:
            return False
        self.remaining -= dt
        if self.remaining <= 0:
            self.remaining = 0
            self.running = False
            return True
        return False

    def display(self) -> str:
        """Display definition"""
        m, s = divmod(int(self.remaining), 60)
        return f"{m:02}:{s:02}"

    def get_status(self) -> str:
        """Status display"""
        if not self.running and self.remaining == self.total:
            return "Waiting to start"
        if self.is_break:
            return "Take a break"
        return "Focusing"

    def complete_session(self) -> None:
        """Session completion"""
        self.sessions_completed += 1
        if self.session_count >= 4:
            self.total = 30*60
            self.session_count = 1
        else:
            self.total = self.custom_break * 60
            self.session_count += 1
        self.is_break = True
        self.remaining = self.total
        self.running = False
        self.total = self.custom_break * 60

    def start_focus_session(self) -> None:
        """Enter pomodoro session"""
        self.total = self.default_session
        self.is_break = False
        self.remaining = self.total
        self.running = False

class TaskStore:
    """Manages loading and saving tasks"""
    def __init__(self):
        self.tasks: List[Task] = []

    def load(self) -> None:
        """Load tasks"""
        if os.path.exists(SAVE_PATH):
            with open(SAVE_PATH, "r", encoding="utf-8") as f:
                self.tasks = [Task(**t) for t in json.load(f).get("tasks", [])]

    def save(self) -> None:
        "Save tasks"
        os.makedirs("cfg", exist_ok=True)
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump({"tasks": [t.__dict__ for t in self.tasks]}, f, indent=2)

class StatsStore:
    """Manages loading, saving, and updating user statistics"""
    def __init__(self):
        self.stats = {
            "total_focus_time": 0,
            "total_sessions": 0,
            "longest_streak": 0,
            "current_streak": 0,
            "daily_records": {},
            "daily_task_scores": {}
        }

    def load(self) -> None:
        """Load daily task scores"""
        if os.path.exists(STATS_PATH):
            with open(STATS_PATH, "r", encoding="utf-8") as f:
                self.stats = json.load(f)
                self.stats.setdefault("daily_task_scores", {})
        self.save()

    def save(self) -> None:
        """Save daily task scores"""
        os.makedirs("cfg", exist_ok=True)
        with open(STATS_PATH, "w", encoding="utf-8") as f:
            json.dump(self.stats, f, indent=2)

    def record_session(self, duration_seconds: int) -> None:
        """Save current session"""
        self.stats["total_focus_time"] += duration_seconds
        self.stats["total_sessions"] += 1
        self.stats["current_streak"] += 1
        if self.stats["current_streak"] > self.stats["longest_streak"]:
            self.stats["longest_streak"] = self.stats["current_streak"]
        today = datetime.now().strftime("%Y-%m-%d")
        self.stats["daily_records"][today] = self.stats["daily_records"].get(today, 0) + 1
        self.save()

    def record_task_completion(self, score: int) -> None:
        """Record complete tasks"""
        today = datetime.now().strftime("%Y-%m-%d")
        self.stats[
            "daily_task_scores"][today] = self.stats[
                "daily_task_scores"].get(today, 0) + score
        self.save()

    def deduct_task_score(self, score: int) -> None:
        """Remove pts if task unticked"""
        today = datetime.now().strftime("%Y-%m-%d")
        if today in self.stats["daily_task_scores"]:
            self.stats["daily_task_scores"][today] = max(
                0, self.stats["daily_task_scores"][today] - score
                )
        self.save()

# Dialog helper
def threaded_dialog(func, *args, **kwargs):
    """Run a Tkinter dialog in a separate thread and return the result."""
    result = {"value": None}
    def target():
        result["value"] = func(*args, **kwargs)
    thread = threading.Thread(target=target)
    thread.start()
    while thread.is_alive():
        pg.event.pump()
        pg.time.wait(10)
    return result["value"]

# Dialogs
class Dialogs:
    """Handles all user interaction dialogs"""
    @staticmethod
    def minutes() -> int:
        """Custom timer def"""
        root = tk.Tk()
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        Dialogs._center(root, 1, 1)
        root.update()
        value = simpledialog.askinteger("Settings", "Minutes:", minvalue=1, parent=root)
        root.destroy()
        return value

    @staticmethod
    def custom_session_break() -> tuple[int, int] | None:
        """Prompt user for custom Pomodoro and break times in minutes."""
        root = tk.Tk()
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        w, h = 450, 180
        root.geometry(f"{w}x{h}")
        Dialogs._center(root, w, h)
        root.resizable(False, False)
        # Input vars
        session_var = tk.IntVar(value=25)
        break_var = tk.IntVar(value=5)
        # Lables and entries
        tk.Label(root, text="Focus Session (minutes):", font=("Consolas", 12)).pack(pady=(15, 0))
        tk.Entry(root, textvariable=session_var, width=15, font=("Consolas", 12)).pack(pady=(0, 10))
        tk.Label(root, text="Break (minutes):", font=("Consolas", 12)).pack()
        tk.Entry(root, textvariable=break_var, width=15, font=("Consolas", 12)).pack(pady=(0, 15))
        result = {"value": None}

        def ok():
            result["value"] = (session_var.get(), break_var.get())
            root.destroy()

        def cancel():
            root.destroy()

        # Buttons frame
        btns = tk.Frame(root)
        btns.pack(pady=5)
        tk.Button(btns, text="OK", width=12, command=ok).pack(side="left", padx=10, pady=5)
        tk.Button(btns, text="Cancel", width=12, command=cancel).pack(side="left", padx=10, pady=5)
        root.update()
        root.lift()
        root.focus_force()
        root.mainloop()

        return result["value"]

    @staticmethod
    def text(title: str, prompt: str, initial="") -> str:
        """Text dialog"""
        root = tk.Tk()
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        Dialogs._center(root, 1, 1)
        root.update()
        value = simpledialog.askstring(title, prompt, initialvalue=initial, parent=root)
        root.destroy()
        return value

    @staticmethod
    def finished() -> None:
        """Session finished, Alarm and reset"""
        root = tk.Tk()
        root.title("Session Complete")
        w, h = 400, 150
        root.geometry(f"{w}x{h}")
        root.attributes("-topmost", True)
        tk.Label(
            root,
            text=random.choice(QUOTES),
            wraplength=w-20,
            font=("Consolas", 12)).pack(
                expand=True, fill="both", padx=10, pady=10
                )
        tk.Button(root, text="OK", width=10, command=root.destroy).pack(pady=10)
        try:
            wx, wy = pg.display.get_window_position()
            sw, sh = pg.display.get_window_size()
        except Exception:
            wx, wy, sw, sh = 0, 0, root.winfo_screenwidth(), root.winfo_screenheight()
        root.geometry(f"{w}x{h}+{wx + (sw - w)//2}+{wy + (sh - h)//2}")
        root.update()
        root.lift()
        root.focus_force()
        root.mainloop()

    @staticmethod
    def multiline_task_with_score(
        initial_text: str = "",
        initial_score: int = 10) -> tuple[str, int] | None:
        """Prompt user for multi-line task description and point value in a single modal."""
        root = tk.Tk()
        root.withdraw()  # hide until we get window position
        root.title("New Task / Edit Task")
        root.attributes("-topmost", True)
        w, h = 450, 250
        root.geometry(f"{w}x{h}")
        Dialogs._center(root, w, h)
        root.resizable(False, False)

        # Multi-line text
        tk.Label(root, text="Task Description:", font=("Consolas", 12)).pack(pady=(10, 0))
        text_widget = tk.Text(root, wrap="word", height=6, font=("Consolas", 12))
        text_widget.pack(padx=10, pady=(0, 10), fill="both", expand=True)
        text_widget.insert("1.0", initial_text)

        # Points input
        points_var = tk.IntVar(value=initial_score)
        tk.Label(root, text="Task Points:", font=("Consolas", 12)).pack()
        tk.Entry(root, textvariable=points_var, width=10, font=("Consolas", 12)).pack(pady=(0, 10))
        result = {"value": None}

        def ok():
            task_text = text_widget.get("1.0", "end").strip()
            task_score = points_var.get()
            if task_text:  # only return if text is not empty
                result["value"] = (task_text, task_score)
            root.destroy()

        def cancel():
            root.destroy()

        # Buttons
        btns = tk.Frame(root)
        btns.pack(pady=5)
        tk.Button(btns, text="OK", width=12, command=ok).pack(side="left", padx=10)
        tk.Button(btns, text="Cancel", width=12, command=cancel).pack(side="left", padx=10)
        root.update()
        root.deiconify()   # show the window now that it's positioned
        root.lift()
        root.focus_force()
        root.mainloop()

        return result["value"]

    @staticmethod
    def _center(root, w, h):
        root.update_idletasks()
        try:
            wx, wy = pg.display.get_window_position()
            sw, sh = pg.display.get_window_size()
        except Exception:
            wx, wy, sw, sh = 0, 0,root.winfo_screenwidth(),root.winfo_screenheight()
        root.geometry(f"{w}x{h}+{wx + (sw - w)//2}+{wy + (sh - h)//2}")

    @staticmethod
    def task_score(initial: str="10") -> int:
        """Task score tracking"""
        root = tk.Tk()
        root.withdraw()
        Dialogs._center(root, 300, 120)
        value = simpledialog.askinteger(
            "Task Score", "Points for this task:",
            minvalue=1,
            initialvalue=int(initial),
            parent=root)
        root.destroy()
        return value

@dataclass
class Button:
    """A simple button UI component"""
    rect: pg.Rect
    label: str

    def draw(self, screen, font, mouse) -> None:
        """Draw logic"""
        color = COLOR_BTN_HOVER if self.rect.collidepoint(mouse) else COLOR_BTN
        pg.draw.rect(screen, color, self.rect, border_radius=6)
        words = self.label.split()
        lines, line = [], ""
        for w in words:
            test = f"{line} {w}".strip()
            if font.size(test)[0] <= self.rect.width - 10:
                line = test
            else:
                lines.append(line)
                line = w
        if line:
            lines.append(line)
        start_y = self.rect.centery - len(lines)*font.get_height()//2
        for l in lines:
            surf = font.render(l, True, COLOR_TEXT)
            screen.blit(surf, (self.rect.centerx - surf.get_width()//2, start_y))
            start_y += font.get_height()

class FocusApp:
    """Focus application main class"""
    def __init__(self):
        self.m_screen_width = BASE_W
        self.m_screen_height = BASE_H
        pg.init()
        pg.mixer.init()
        self._load_config()
        self.screen = pg.display.set_mode((BASE_W, BASE_H), pg.RESIZABLE)
        pg.display.set_caption(APP_TITLE)
        pg.display.set_icon(pg.image.load(os.path.abspath(APP_ICON)))

        # Fonts
        self.font_s = pg.font.SysFont("consolas", 14)
        self.font_m = pg.font.SysFont("consolas", 20)
        self.font_l = pg.font.SysFont("consolas", 44)

        # App state
        self.mode = AppMode.SPLASH
        self.timer = PomodoroTimer()
        self.timer.default_session = self.custom_pomodoro * 60
        self.timer.custom_break = self.custom_break
        self.timer.reset(total=self.custom_pomodoro * 60)
        self.timer.custom_break = self.custom_break
        self.timer.reset(total=self.custom_pomodoro*60)
        self.tasks = TaskStore()
        self.tasks.load()
        self.stats = StatsStore()
        self.stats.load()
        self.hover = None
        self.sounds = self._load_sounds()
        self._undo_cache = []

        # Dragging / click
        self.dragging_task = None
        self.mouse_down_pos = None
        self.last_click_time = 0
        self.last_click_pos = None
        self.skip_next_click = False
        self.double_click_threshold = 300
        self.task_padding = 10  # Space between tasks adjustment

        # Buttons
        self.btn_start = Button(pg.Rect(20, 100, 80, 40), "Start")
        self.btn_add = Button(pg.Rect(110, 100, 80, 40), "Add Task")
        self.btn_custom = Button(pg.Rect(200, 100, 80, 40), "Settings")
        self.btn_instructions = Button(pg.Rect(290, 100, 115, 40), "Instructions")
        self.btn_stats = Button(pg.Rect(415, 100, 60, 40), "Stats")
        self.btn_reset = Button(pg.Rect(485, 100, 60, 40), "Reset")
        self.btn_back = Button(pg.Rect(BASE_W - 120, 20, 100, 40), "← Back")
        self.clock = pg.time.Clock()

    def get_task_y(self, idx):
        """Return the y position of a task given its index"""
        y = 220
        for i, t in enumerate(self.tasks.tasks):
            row_h = max(28, len(self._wrap(t.text, self.screen.get_width()-150))*18)
            if i == idx:
                return y
            y += row_h + self.task_padding
        return y

    def _load_config(self):
        """Load custom session/break times if they exist"""
        self.custom_pomodoro = DEFAULT_POMODORO // 60
        self.custom_break = 5
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.custom_pomodoro = data.get("session_minutes", self.custom_pomodoro)
                    self.custom_break = data.get("break_minutes", self.custom_break)
            except Exception as e:
                print(e)

    def _save_config(self):
        """Save custom session/break times"""
        os.makedirs("cfg", exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump({"session_minutes": self.custom_pomodoro,
                    "break_minutes": self.custom_break}, f, indent=2)

    def _load_sounds(self) -> List[str]:
        if not os.path.exists(SOUND_DIR):
            return []
        return [os.path.join(SOUND_DIR, f) for f in os.listdir(SOUND_DIR)
                if f.endswith((".wav", ".mp3", ".ogg"))]

    def _play_alarm(self) -> None:
        if self.sounds:
            pg.mixer.Sound(random.choice(self.sounds)).play()

    def _get_today_score(self) -> int:
        today = datetime.now().strftime("%Y-%m-%d")
        return self.stats.stats["daily_task_scores"].get(today, 0)

    def _wrap(self, text: str, width: int) -> List[str]:
        """Wrap text while preserving newlines"""
        lines = []
        for line in text.split('\n'):
            words, cur = line.split(), ""
            if not words:
                lines.append("")
                continue
            for w in words:
                t = f"{cur} {w}".strip()
                if self.font_s.size(t)[0] <= width:
                    cur = t
                else:
                    lines.append(cur)
                    cur = w
            if cur:
                lines.append(cur)
        return lines or [""]

    def task_at(self, pos) -> int | None:
        """Task location"""
        y = 220
        for i, t in enumerate(self.tasks.tasks):
            row_h = max(28, len(self._wrap(t.text, self.screen.get_width()-150))*18)
            if y <= pos[1] <= y + row_h:
                return i
            y += row_h + self.task_padding
        return None

    def _resize_for_tasks(self) -> None:
        new_h = max(BASE_H, min(1200, 260 + len(self.tasks.tasks)*40))
        pg.display.set_mode((self.screen.get_width(), new_h), pg.RESIZABLE)

    def edit_or_toggle(self, mouse) -> None:
        """Edit or tick the box depending on mouse location"""
        idx = self.hover
        if idx is None:
            return
        t = self.tasks.tasks[idx]
        y = 220
        for i, task in enumerate(self.tasks.tasks):
            lines = self._wrap(task.text, self.screen.get_width()-150)
            row_h = max(28, len(lines)*18)
            if i == idx:
                # Place checkbox at top line of the task
                box_size = 20
                box_y = y
                box = pg.Rect(30, box_y, box_size, box_size)
                if box.collidepoint(mouse):
                    if not t.complete:
                        self.stats.record_task_completion(t.score)
                    else:
                        self.stats.deduct_task_score(t.score)
                    t.complete ^= True
                    self.tasks.save()
                return
            y += row_h + self.task_padding

    # Drawing functions
    def draw_splash(self) -> None:
        """Splash screen"""
        self.screen.fill(COLOR_BG)
        lines = [
            "Pomodoro Technique","","25 minutes focused work","5 minute break","Repeat",
            "","","","","App by LTHL-NoID","","Click anywhere to start"
        ]
        y = 200
        for l in lines:
            surf = self.font_m.render(l, True, COLOR_TEXT)
            self.screen.blit(surf, (self.screen.get_width()//2 - surf.get_width()//2, y))
            y += 30

    def draw_main(self) -> None:
        """Draw main application"""
        self.screen.fill(COLOR_BG)
        self.btn_start.label = "Stop" if self.timer.running else "Start"
        mouse = pg.mouse.get_pos()
        date_surf = self.font_s.render(
            datetime.now().strftime("%A %d %B %Y %I:%M %p"),
            True,
            COLOR_TEXT
            )
        self.screen.blit(date_surf, (20, 20))

        # Status and sessions
        self.screen.blit(self.font_s.render(
            f"Status: {self.timer.get_status()}", True, COLOR_DIM), (20, 40))
        self.screen.blit(self.font_s.render(
            f"Sessions Completed: {self.timer.sessions_completed}", True, COLOR_DIM), (20, 60))
        self.screen.blit(self.font_s.render(
            f"Today's Score: {self._get_today_score()}pts", True, COLOR_DONE),
            (self.screen.get_width()-170, 60))

        # Timer
        if self.timer.is_break:
            color = COLOR_BREAK
        elif self.timer.remaining < 120:
            color = COLOR_WARN
        else:
            color = COLOR_DONE
        timer_surf = self.font_l.render(self.timer.display(), True, color)
        self.screen.blit(timer_surf, (self.screen.get_width()-timer_surf.get_width()-20, 20))

        # Buttons
        for b in (
            self.btn_start,
            self.btn_custom,
            self.btn_add,
            self.btn_instructions,
            self.btn_stats,
            self.btn_reset
            ):
            b.draw(self.screen, self.font_s, mouse)

        # Task header
        self.screen.blit(self.font_m.render("Task List", True, COLOR_TEXT), (20, 180))
        y = 220
        for i, task in enumerate(self.tasks.tasks):
            lines = self._wrap(task.text, self.screen.get_width()-150)
            row_h = max(28, len(lines)*18)
            total_h = row_h + self.task_padding

            # Hover highlight
            extra_bottom = 4 if len(lines) > 1 else 0  # extra space for multi-line tasks
            if i == self.hover:
                pg.draw.rect(
                    self.screen,
                    COLOR_TASK_HIGHLIGHT,
                    (20, y -4, self.screen.get_width()-85, row_h + extra_bottom)
                )

            # Dragging highlight (dimmed)
            if self.dragging_task == i:
                extra_bottom = 4 if len(lines) > 1 else 0  # same as hover
                surf = pg.Surface((self.screen.get_width()-85, row_h + extra_bottom), pg.SRCALPHA)
                surf.fill((70, 140, 80, 100))  # RGBA for dim
                self.screen.blit(surf, (20, y - 4))   # match hover y offset

            # Checkbox
            box_size = 20
            box_y = y
            box = pg.Rect(30, box_y, box_size, box_size)
            pg.draw.rect(self.screen, COLOR_BOX, box, 2)
            if task.complete:
                pg.draw.line(
                    self.screen,
                    COLOR_DONE,
                    (box.left+4, box.centery),
                    (box.centerx-2, box.bottom-4),3)
                pg.draw.line(
                    self.screen,
                    COLOR_DONE,
                    (box.centerx-2, box.bottom-4),
                    (box.right-4, box.top+4),3)

            # Task text
            line_height = 18
            text_y = box_y + (box_size - line_height)//2 
            for li, line in enumerate(lines):
                surf = self.font_s.render(line, True, COLOR_DIM if task.complete else COLOR_TEXT)
                self.screen.blit(surf, (60, text_y + li*line_height))

            # Strike-through for completed tasks
            if task.complete:
                ystrike = text_y + li*line_height + surf.get_height()//2 - 2
                pg.draw.line(
                    self.screen,
                    COLOR_DIM,
                    (60, ystrike),
                    (60+surf.get_width(),
                    ystrike),1)

            # Task score
            score_surf = self.font_s.render(
                f"+{task.score}pts",
                True, COLOR_DONE if task.complete else COLOR_DIM
                )
            self.screen.blit(score_surf, (self.screen.get_width()-60, text_y))
            y += total_h


    def draw_instructions(self) -> None:
        """Instructions screen"""
        self.screen.fill(COLOR_BG)
        self.btn_back.draw(self.screen, self.font_s, pg.mouse.get_pos())
        self.screen.blit(self.font_m.render("How to Use Focus Flow", True, COLOR_TEXT), (20, 20))
        instructions = [
            "App Overview:", "• Focus Flow combines Pomodoro Technique with a to-do list",
            "• Designed to help manage your time and tasks effectively", "", "Timer:",
            "• Click 'Start/Stop' to begin your focus session/break",
            "• Click 'Custom Timer' to set custom durations", "", "Tasks:",
            "• Click 'Add Task' to create a new task",
            "• Click and drag to re-arrange task order",
            "• Click checkbox to mark task complete (earn points/xp!)",
            "• Double click task text to edit it (and to adjust points)",
            "• Right-click task to delete it","• CTRL + Z to undo task deletion", "", "Scoring:",
            "• Each task has a point value (default 10 pts)",
            "• Earn points when you complete tasks",
            "• Lose points when you untick completed tasks",
            "• Track daily scores on the Statistics page", "", "Sessions:",
            "• 25 mins focus, 5 mins break (standard or set custom times)",
            "• After 4 sessions, take a 30 min break","• Track your progress in Stats!", "",
            "Known Bugs:",
            "• After setting custom time, need to click on 'Start'\n twice before counter is active"
        ]
        y = 60
        for line in instructions:
            color = COLOR_DIM if line.startswith("•") else COLOR_TEXT
            surf = self.font_s.render(line, True, color if line else COLOR_DIM)
            self.screen.blit(surf, (20, y))
            y += 22

    def draw_stats(self) -> None:
        """Stats screen"""
        self.screen.fill(COLOR_BG)
        self.btn_back.draw(self.screen, self.font_s, pg.mouse.get_pos())
        self.screen.blit(self.font_m.render("Your Statistics", True, COLOR_TEXT), (20, 20))
        total_hours, total_mins = divmod(self.stats.stats["total_focus_time"], 3600)
        total_mins //= 60
        stats_lines = [
            f"Total Focus Time: {total_hours}h {total_mins}m",
            f"Total Sessions: {self.stats.stats['total_sessions']}",
            f"Longest Streak: {self.stats.stats['longest_streak']} sessions",
            f"Current Streak: {self.stats.stats['current_streak']} sessions",
            "", "Daily Performance:"
        ]

        today = datetime.now()
        for i in range(6,-1,-1):
            day = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            day_name = (today - timedelta(days=i)).strftime("%a")
            stats_lines.append(
                f"  {day_name}: {self.stats.stats['daily_records'].get(day,0)} sessions | {self.stats.stats['daily_task_scores'].get(day,0)} pts"
                )

        y = 50
        for line in stats_lines:
            color = COLOR_DIM if line.startswith(" ") else COLOR_TEXT
            self.screen.blit(self.font_s.render(line, True, color), (20, y))
            y += 25

    def run(self) -> None:
        """Main loop"""
        while True:
            dt = self.clock.tick(FPS)/1000
            for e in pg.event.get():
                if e.type == pg.QUIT:
                    self.tasks.save()
                    self._resize_for_tasks()
                    self.stats.save()
                    return

                if e.type == pg.VIDEORESIZE:
                    if e.w < BASE_W or e.h < BASE_H:
                        pg.display.set_mode((BASE_W, BASE_H), pg.RESIZABLE)

                if self.mode == AppMode.SPLASH and e.type == pg.MOUSEBUTTONDOWN:
                    self.mode = AppMode.MAIN
                    continue

                if e.type == pg.KEYDOWN and e.key == pg.K_z and pg.key.get_mods() & pg.KMOD_CTRL:
                    if self._undo_cache:
                        self.tasks.tasks.append(self._undo_cache.pop())
                        self.tasks.save()
                        self._resize_for_tasks()

                if e.type == pg.MOUSEMOTION:
                    self.hover = self.task_at(e.pos) if self.mode == AppMode.MAIN else None
                    if self.mouse_down_pos and self.hover is not None:
                        if abs(
                            e.pos[0]-self.mouse_down_pos[0])>5 or abs(
                            e.pos[1]-self.mouse_down_pos[1])>5:
                            self.dragging_task = self.task_at(self.mouse_down_pos)

                if e.type == pg.MOUSEBUTTONDOWN and e.button == 1:
                    if self.skip_next_click:
                        self.skip_next_click = False
                        continue  # ignore this click entirely
                    self.mouse_down_pos = e.pos
                    idx = self.task_at(e.pos)
                    now = pg.time.get_ticks()
                    self.skip_next_click = False

                    if idx is not None:
                        if self.last_click_pos == idx and now - self.last_click_time <= self.double_click_threshold:
                            t = self.tasks.tasks[idx]
                            res = threaded_dialog(Dialogs.multiline_task_with_score, initial_text=t.text, initial_score=t.score)

                            if res:
                                txt, score = res
                                t.text = txt
                                t.score = score
                                self.tasks.save()
                                self._resize_for_tasks()
                                self.dragging_task = None
                                self.mouse_down_pos = None

                            self.last_click_time = 0
                            self.last_click_pos = None
                            self.skip_next_click = True

                        else: 
                            self.last_click_time = now
                            self.last_click_pos = idx

                    if self.mode == AppMode.MAIN:
                        idx = self.task_at(e.pos)
                        if idx is not None and not self.skip_next_click:
                            y = self.get_task_y(idx)
                            box = pg.Rect(30, y, 20, 20)
                            if not box.collidepoint(e.pos):
                                self.dragging_task = idx
                                self.drag_offset_y = e.pos[1] - y

                        elif self.btn_start.rect.collidepoint(e.pos):
                            if self.timer.running:
                                self.timer.stop()
                            else:
                                self.timer.start()

                        elif self.btn_custom.rect.collidepoint(e.pos):
                            # Custom Timer button
                            res = threaded_dialog(Dialogs.custom_session_break)

                            if res:
                                session_min, break_min = res
                                self.custom_pomodoro = session_min
                                self.custom_break = break_min
                                self._save_config()
                                self.timer.default_session = self.custom_pomodoro * 60
                                self.timer.reset(total=self.custom_pomodoro*60)
                                self.timer.custom_break = self.custom_break

                        elif self.btn_add.rect.collidepoint(e.pos):
                            res = threaded_dialog(Dialogs.multiline_task_with_score)
                            if res:
                                txt, score = res
                                self.tasks.tasks.append(Task(text=txt, score=score))
                                self.tasks.save()
                                self._resize_for_tasks()

                        elif self.btn_instructions.rect.collidepoint(e.pos):
                            self.mode=AppMode.INSTRUCTIONS
                        elif self.btn_stats.rect.collidepoint(e.pos):
                            self.mode=AppMode.STATS
                        elif self.btn_reset.rect.collidepoint(e.pos):
                            self.timer.reset_full()

                if e.type==pg.MOUSEBUTTONUP and e.button==1:
                    idx = self.task_at(e.pos)
                    if self.dragging_task is not None and idx is not None and self.dragging_task != idx:
                        task_to_move = self.tasks.tasks.pop(self.dragging_task)
                        self.tasks.tasks.insert(idx, task_to_move)
                        self.tasks.save()

                        self.dragging_task = None
                        self.mouse_down_pos = None

                    elif self.dragging_task is None and idx is not None and self.mode==AppMode.MAIN:
                        self.edit_or_toggle(e.pos)
                    self.dragging_task = None
                    self.mouse_down_pos = None

                if e.type==pg.MOUSEBUTTONDOWN and e.button==3 and self.hover is not None and self.mode==AppMode.MAIN:
                    root = tk.Tk()
                    root.withdraw() # hide until we get window position
                    root.title("Delete Task?")
                    root.attributes("-topmost", True)
                    w, h = 350, 140
                    root.geometry(f"{w}x{h}")
                    Dialogs._center(root, w, h)
                    root.resizable(False, False)
                    result = {"value": False}
                    tk.Label(root, text="Are you sure you want to delete this task?",font=("Consolas", 11), wraplength=w-20).pack(pady=20)
                    btns = tk.Frame(root)
                    btns.pack(pady=10)
                    def yes():
                        result["value"] = True
                        root.destroy()
                    def no():
                        root.destroy()
                    tk.Button(btns, text="Yes", width=10, command=yes).pack(side="left", padx=10)
                    tk.Button(btns, text="No", width=10, command=no).pack(side="left", padx=10)
                    root.update()
                    root.deiconify() # show the window now that it's positioned
                    root.lift()
                    root.focus_force()
                    root.mainloop()

                    if result["value"]:
                        self._undo_cache.append(self.tasks.tasks.pop(self.hover))
                        self.tasks.save()
                        self._resize_for_tasks()

                if e.type==pg.MOUSEBUTTONDOWN and e.button==1:
                    if self.mode in (
                        AppMode.INSTRUCTIONS, AppMode.STATS
                        ) and self.btn_back.rect.collidepoint(e.pos):
                        self.mode=AppMode.MAIN

            # Timer update
            if self.mode==AppMode.MAIN and self.timer.update(dt):
                self._play_alarm()
                threaded_dialog(Dialogs.finished)
                pg.mixer.stop()
                self.stats.record_session(int(self.timer.total))  # Record session length

                if self.timer.is_break:
                    self.timer.start_focus_session()
                    self.timer.total = self.custom_pomodoro*60
                    self.timer.remaining = self.timer.total
                else:
                    self.timer.complete_session()
                    self.timer.total = self.custom_break*60
                    self.timer.remaining = self.timer.total

            if self.mode==AppMode.SPLASH:
                self.draw_splash()
            elif self.mode==AppMode.MAIN:
                self.draw_main()
            elif self.mode==AppMode.INSTRUCTIONS:
                self.draw_instructions()
            elif self.mode==AppMode.STATS:
                self.draw_stats()
            pg.display.flip()

if __name__ == "__main__":
    FocusApp().run()
