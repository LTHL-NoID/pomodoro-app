#!/usr/bin/env python3
# Focus Flow - Pomodoro App with To-Do List
# Req: pip install pygame-ce==2.5.6
import os
import json
import random
import tkinter as tk

from enum import Enum
from typing import Dict, Any
from typing import List
from datetime import datetime
from dataclasses import dataclass
from tkinter import simpledialog, messagebox
import pygame as pg

# Config
APP_TITLE = "Focus Flow - Pomodoro To-Do App"
APP_ICON = "media/images/6194029.png"
SAVE_PATH = "cfg/state.json"
STATS_PATH = "cfg/stats.json"
SOUND_DIR = "media/alarms"
BASE_W, BASE_H = 560, 720
FPS = 60
DEFAULT_POMODORO = 25 * 60
# Colors RGB tuples
COLOR_BG = (40, 40, 40)
COLOR_TEXT = (220, 220, 220)
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
    score: int = 10 # Default score per task

class PomodoroTimer:
    """Manages the Pomodoro timer state and logic"""
    def __init__(self):
        self.total = DEFAULT_POMODORO
        self.remaining = self.total
        self.running = False
        self.session_count = 1
        self.is_break = False
        self.sessions_completed = 0

    def start(self) -> None:
        """Start the timer"""
        self.running = True

    def stop(self)-> None:
        """Stop/pause the timer"""
        self.running = False

    def reset(self, total=None) -> None:
        """Reset the timer to default or custom total"""
        if total is not None:
            self.total = total
        self.remaining = self.total
        self.running = False

    def update(self, dt) -> bool:
        """ Update timer by dt seconds """
        if not self.running:
            return False
        self.remaining -= dt
        if self.remaining <= 0:
            self.remaining = 0
            self.running = False
            return True
        return False

    def display(self) -> str:
        """Return formatted time string MM:SS"""
        m, s = divmod(int(self.remaining), 60)
        return f"{m:02}:{s:02}"

    def get_status(self) -> str:
        """Return current status string"""
        if not self.running and self.remaining == self.total:
            return "Waiting to start"
        elif self.is_break:
            return "Take a break"
        elif self.running or self.remaining < self.total:
            return "Focusing"
        return "Waiting to start"

    def complete_session(self) -> None:
        """Handle session completion logic"""
        self.sessions_completed += 1

        if self.session_count >= 4:
            # Long break after 4 sessions
            self.total = 30 * 60
            self.session_count = 1
        else:
            # Short break
            self.total = 5 * 60
            self.session_count += 1

        self.is_break = True
        self.remaining = self.total
        self.running = False

    def start_focus_session(self) -> None:
        """Transition from break back to focus"""
        self.total = DEFAULT_POMODORO
        self.is_break = False
        self.remaining = self.total
        self.running = False

class TaskStore:
    """Manages loading and saving tasks"""
    def __init__(self):
        self.tasks: List[Task] = []

    def load(self) -> json:
        """Load tasks from file"""
        if os.path.exists(SAVE_PATH):
            with open(SAVE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.tasks = [Task(**t) for t in data.get("tasks", [])]

    def save(self) -> None:
        """Save tasks to file"""
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

    def load(self) -> json:
        """Load statistics from file"""
        if os.path.exists(STATS_PATH):
            with open(STATS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.stats = data
                if "daily_task_scores" not in self.stats:
                    self.stats["daily_task_scores"] = {}
                self.save()
        else:
            self.save()

    def save(self) -> None:
        """Save statistics to file"""
        os.makedirs("cfg", exist_ok=True)
        with open(STATS_PATH, "w", encoding="utf-8") as f:
            json.dump(self.stats, f, indent=2)

    def record_session(self, duration_seconds: int) -> None:
        """Record a completed focus session"""
        self.stats["total_focus_time"] += duration_seconds
        self.stats["total_sessions"] += 1
        self.stats["current_streak"] += 1
        if self.stats["current_streak"] > self.stats["longest_streak"]:
            self.stats["longest_streak"] = self.stats["current_streak"]

        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self.stats["daily_records"]:
            self.stats["daily_records"][today] = 0
        self.stats["daily_records"][today] += 1
        self.save()

    def record_task_completion(self, score: int) -> None:
        """Record task completion and update daily score"""
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self.stats["daily_task_scores"]:
            self.stats["daily_task_scores"][today] = 0
        self.stats["daily_task_scores"][today] += score
        self.save()

    def deduct_task_score(self, score: int):
        """Deduct score when a task is uncompleted"""
        today = datetime.now().strftime("%Y-%m-%d")
        if today in self.stats["daily_task_scores"]:
            self.stats["daily_task_scores"][today] -= score
            if self.stats["daily_task_scores"][today] < 0:
                self.stats["daily_task_scores"][today] = 0
        self.save()

# Dialogs
class Dialogs:
    """Handles all user interaction dialogs"""

    @staticmethod
    def minutes() -> int:
        """Prompt user for custom timer minutes"""
        root = tk.Tk()
        root.withdraw()
        Dialogs._center(root, 300, 120)
        input_value = simpledialog.askinteger("Custom Timer", "Minutes:", minvalue=1, parent=root)
        root.destroy()
        return input_value

    @staticmethod
    def text(title: str, prompt: str, initial="") -> str:
        """Prompt user for single line text input"""
        root = tk.Tk()
        root.withdraw()
        input_value = simpledialog.askstring(title, prompt, initialvalue=initial, parent=root)
        root.destroy()
        return input_value

    @staticmethod
    def finished() -> None:
        """Show session complete message with motivational quote"""
        root = tk.Tk(); root.withdraw()
        messagebox.showinfo("Session Complete", random.choice(QUOTES), parent=root)
        root.destroy()

    @staticmethod
    def multiline_text(title: str, initial: str="") -> Dict:
        """Prompt user for multi-line text input"""
        root = tk.Tk()
        root.title(title)
        root.geometry("420x180")
        Dialogs._center(root, 420, 180)
        root.resizable(False, False)
        text = tk.Text(root, wrap="word", height=6)
        text.pack(padx=10, pady=10, fill="both", expand=True)
        text.insert("1.0", initial)
        result = {"value": None}

        def ok():
            result["value"] = text.get("1.0", "end").strip()
            root.destroy()

        def cancel():
            root.destroy()

        btns = tk.Frame(root)
        btns.pack(pady=5)
        tk.Button(btns, text="OK", width=10, command=ok).pack(side="left", padx=5)
        tk.Button(btns, text="Cancel", width=10, command=cancel).pack(side="left", padx=5)
        root.mainloop()
        return result["value"]
    
    @staticmethod
    def _center(root, w, h) -> None:
        """Centres tk popup windows"""
        root.update_idletasks()
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        root.geometry(f"{w}x{h}+{x}+{y}")

    @staticmethod
    def task_score(initial: str="10") -> int:
        """Prompt user for task score input"""
        root = tk.Tk()
        root.withdraw()
        Dialogs._center(root, 300, 120)
        input_value = simpledialog.askinteger(
            "Task Score", "Points for this task:",
            minvalue=1,
            initialvalue=int(initial),
            parent=root
            )
        root.destroy()
        return input_value

# UI Components
@dataclass
class Button:
    """A simple button UI component"""
    rect: pg.Rect
    label: str

    def draw(self, screen, font: str, mouse) -> None:
        """Draw the button"""
        color = COLOR_BTN_HOVER if self.rect.collidepoint(mouse) else COLOR_BTN
        pg.draw.rect(screen, color, self.rect, border_radius=6)
        words = self.label.split()
        lines = []
        line = ""
        for w in words:
            test = f"{line} {w}".strip()
            if font.size(test)[0] <= self.rect.width - 10:
                line = test
            else:
                lines.append(line)
                line = w
        if line:
            lines.append(line)

        total_h = len(lines) * font.get_height()
        start_y_pos = self.rect.centery - total_h // 2

        for l in lines:
            surf = font.render(l, True, COLOR_TEXT)
            screen.blit(
                surf,
                (self.rect.centerx - surf.get_width() // 2, start_y_pos)
            )
            start_y_pos += font.get_height()

# Application
class FocusApp:
    """Focus application"""
    def __init__(self):
        self.m_screen_width = BASE_W
        self.m_screen_height = BASE_H
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((BASE_W, BASE_H), pg.RESIZABLE)
        pg.display.set_caption(APP_TITLE)
        pg.display.set_icon(
            pg.image.load(
                os.path.abspath(APP_ICON)))

        self.clock = pg.time.Clock()
        self.font_s = pg.font.SysFont("consolas", 14)
        self.font_m = pg.font.SysFont("consolas", 20)
        self.font_l = pg.font.SysFont("consolas", 44)

        self.mode = AppMode.SPLASH
        self.timer = PomodoroTimer()
        self.tasks = TaskStore()
        self.tasks.load()
        self.stats = StatsStore()
        self.stats.load()
        self.hover = None
        self.sounds = self._load_sounds()
        # Undo delete cache
        self._undo_cache = []
        # Task dragging
        self.dragging_task = None
        self.mouse_down_pos = None
        self.last_click_time = 0
        self.last_click_pos = None
        self.double_click_threshold = 300  # milliseconds
        # CUSTOMISATION: Task display padding (in pixels)
        self.task_padding = 10  # Space between tasks - edit this value
        # Button config
        #self.btn_start = Button(pg.Rect(20, 100, 80, 40), "Start / Stop")
        self.btn_start = Button(pg.Rect(20, 100, 80, 40), "Start")
        self.btn_custom = Button(pg.Rect(110, 100, 80, 40), "Custom Timer")
        self.btn_add = Button(pg.Rect(200, 100, 80, 40), "Add Task")
        self.btn_instructions = Button(pg.Rect(290, 100, 115, 40), "Instructions")
        self.btn_stats = Button(pg.Rect(415, 100, 115, 40), "Statistics")
        self.btn_back = Button(pg.Rect(BASE_W - 120, 20, 100, 40), "← Back")

    def _load_sounds(self) -> Any:
        if not os.path.exists(SOUND_DIR): return []
        return [os.path.join(SOUND_DIR, f) for f in os.listdir(SOUND_DIR)
                if f.endswith((".wav", ".mp3", ".ogg"))]

    def _play_alarm(self) -> None:
        """Play a random alarm sound"""
        if self.sounds:
            pg.mixer.Sound(random.choice(self.sounds)).play()

    def _get_today_score(self) -> Dict:
        """Get today's accumulated task score"""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.stats.stats["daily_task_scores"].get(today, 0)

    # Task text wrapping function
    def _wrap(self, text: str, width: int) -> List:
        """Wrap text while preserving newlines"""
        original_lines = text.split('\n')
        all_lines = []
        for original_line in original_lines:
            words = original_line.split()
            if not words:  # Preserve empty lines
                all_lines.append("")
                continue
            line = ""
            for w in words:
                t = f"{line} {w}".strip()
                if self.font_s.size(t)[0] <= width:
                    line = t
                else:
                    if line:
                        all_lines.append(line)
                    line = w
            if line:
                all_lines.append(line)

        return all_lines if all_lines else [""]

    def task_at(self, pos: int) -> int | None:
        """Get task index at mouse position"""
        start_y_pos = 220
        for i, t in enumerate(self.tasks.tasks):
            lines = self._wrap(t.text, self.screen.get_width()-150)
            text_height = len(lines)*18
            row_height = max(28, text_height)
            total_row_height = row_height + self.task_padding

            if start_y_pos <= pos[1] <= start_y_pos + row_height:
                return i
            start_y_pos += total_row_height
        return None
    
    def _resize_for_tasks(self) -> None:
        base_height = 260
        per_task = 40
        new_height = max(
            BASE_H,
            min(1200, base_height + len(self.tasks.tasks) * per_task)
        )
        pg.display.set_mode((self.screen.get_width(), new_height), pg.RESIZABLE)

    def edit_or_toggle(self, mouse) -> None:
        """Toggle checkbox of a task at mouse position"""
        idx = self.hover
        if idx is None: return
        t = self.tasks.tasks[idx]
        # Only toggle if mouse is inside the checkbox rect
        start_y_pos = 220
        for i, task in enumerate(self.tasks.tasks):
            lines = self._wrap(task.text, self.screen.get_width()-150)
            text_height = len(lines)*18
            row_height = max(28, text_height)
            total_row_height = row_height + self.task_padding

            if i == idx:
                box = pg.Rect(30, start_y_pos + row_height//2 - 10, 20, 20)
                if box.collidepoint(mouse):
                    if not t.complete:
                        self.stats.record_task_completion(t.score)
                    else:
                        self.stats.deduct_task_score(t.score)
                    t.complete ^= True
                    self.tasks.save()
                return  # Never open edit dialog here
            start_y_pos += total_row_height

    # Draw
    def draw_splash(self) -> None:
        """Draw splash screen for application"""
        self.screen.fill(COLOR_BG)
        lines = [
            "Pomodoro Technique",
            "",
            "25 minutes focused work",
            "5 minute break",
            "Repeat",
            "",
            "",
            "",
            "",
            "App by LTHL-NoID",
            "",
            "Click anywhere to start"
        ]
        start_y_pos = 200
        for l in lines:
            s = self.font_m.render(l, True, COLOR_TEXT)
            self.screen.blit(s, (self.screen.get_width()//2 - s.get_width()//2, start_y_pos))
            start_y_pos += 30

    def draw_main(self) -> None:
        """Draw main working screen"""
        self.screen.fill(COLOR_BG)
        self.btn_start.label = "Stop" if self.timer.running else "Start"
        mouse = pg.mouse.get_pos()
        date = datetime.now().strftime("%A %d %B %Y %I:%M %p")
        self.screen.blit(self.font_s.render(date, True, COLOR_TEXT), (20, 20))
        # Display status and session count
        status = self.timer.get_status()
        status_text = f"Status: {status}"
        self.screen.blit(self.font_s.render(status_text, True, COLOR_DIM), (20, 40))
        session_text = f"Sessions Completed: {self.timer.sessions_completed}"
        self.screen.blit(self.font_s.render(session_text, True, COLOR_DIM), (20, 60))
        # Display today's score
        today_score = self._get_today_score()
        score_text = f"Today's Score: {today_score}pts"# Count tasks to give total"
        self.screen.blit(self.font_s.render(score_text, True, COLOR_DONE), (self.screen.get_width()-170, 60))
        # Timer color changes based on state
        if self.timer.is_break:
            timer_color = COLOR_BREAK
        elif self.timer.remaining < 120:
            timer_color = COLOR_WARN
        else:
            timer_color = COLOR_DONE
        timer = self.font_l.render(self.timer.display(), True, timer_color)
        self.screen.blit(timer, (self.screen.get_width()-timer.get_width()-20, 20))

        for b in (
            self.btn_start, self.btn_custom, self.btn_add, self.btn_instructions, self.btn_stats
            ):
            b.draw(self.screen, self.font_s, mouse)

        # Task list header
        header = self.font_m.render("Task List", True, COLOR_TEXT)
        self.screen.blit(header, (20, 180))
        start_y_pos = 220
        for i, task in enumerate(self.tasks.tasks):
            # Wrap width for tasks - reduce 150 if you want more text space
            lines = self._wrap(task.text, self.screen.get_width()-150)
            text_height = len(lines)*18
            row_height = max(28, text_height)
            total_row_height = row_height + self.task_padding
            box_y = start_y_pos + row_height//2 - 10
            text_y = start_y_pos + (row_height - text_height)// 2 + 2.5  # fine-tune here
            if i == self.hover:
                pg.draw.rect(self.screen, COLOR_TASK_HIGHLIGHT,
                             (20, start_y_pos, self.screen.get_width()-85, row_height))

            box = pg.Rect(30, box_y, 20, 20)
            pg.draw.rect(self.screen, COLOR_BOX, box, 2)
            if task.complete:
                pg.draw.line(self.screen, COLOR_DONE, (box.left+4, box.centery),
                             (box.centerx-2, box.bottom-4), 3)
                pg.draw.line(self.screen, COLOR_DONE, (box.centerx-2, box.bottom-4),
                             (box.right-4, box.top+4), 3)

            for li, line in enumerate(lines):
                surf = self.font_s.render(line, True, COLOR_DIM if task.complete else COLOR_TEXT)
                self.screen.blit(surf, (60, text_y + li*18))
                if task.complete:
                    ystrike = text_y + li*18 + surf.get_height()//2 -2 # Edit strike out pos
                    pg.draw.line(self.screen, COLOR_DIM,
                                 (60, ystrike), (60+surf.get_width(), ystrike), 1)

            # Draw task score
            score_text = f"+{task.score}pts"
            score_surf = self.font_s.render(score_text, True, COLOR_DONE if task.complete else COLOR_DIM)
            self.screen.blit(score_surf, (self.screen.get_width() - 60, text_y))
            start_y_pos += total_row_height

    def draw_instructions(self) -> None:
        """Draw instructions page"""
        self.screen.fill(COLOR_BG)
        mouse = pg.mouse.get_pos()
        self.btn_back.draw(self.screen, self.font_s, mouse)

        title = self.font_m.render("How to Use Focus Flow", True, COLOR_TEXT)
        self.screen.blit(title, (20, 20))

        instructions = [
            "App Overview:",
            "• Focus Flow combines Pomodoro Technique with a to-do list",
            "• Designed to help manage your time and tasks effectively",
            "",
            "Timer:",
            "• Click 'Start/Stop' to begin your focus session/break",
            "• Click 'Custom Timer' to set custom durations",
            "",
            "Tasks:",
            "• Click 'Add Task' to create a new task",
            "• Click and drag to re-arrange task order",
            "• Click checkbox to mark task complete (earn points/xp!)",
            "• Double click task text to edit it (and to adjust points)",
            "• Right-click task to delete it",
            "• CTRL + Z to undo task deletion",
            "",
            "Scoring:",
            "• Each task has a point value (default 10 pts)",
            "• Earn points when you complete tasks",
            "• Lose points when you untick completed tasks",
            "• Track daily scores on the Statistics page",
            "",
            "Sessions:",
            "• 25 mins focus, 5 mins break (standard or set custom times)",
            "• After 4 sessions, take a 30 min break",
            "• Track your progress in Stats!"
            "",
            "",
            "Known Bugs:",
            "• After setting custom time, need to click on 'Start'\n twice before counter is active"
        ]

        start_y_pos = 60
        for line in instructions:
            if line:
                color = COLOR_DIM if line.startswith("•") else COLOR_TEXT
                surf = self.font_s.render(line, True, color)
            else:
                surf = self.font_s.render(line, True, COLOR_DIM)
            self.screen.blit(surf, (20, start_y_pos))
            start_y_pos += 22

    def draw_stats(self) -> None:
        """Draw stats page tallys"""
        self.screen.fill(COLOR_BG)
        mouse = pg.mouse.get_pos()
        self.btn_back.draw(self.screen, self.font_s, mouse)
        title = self.font_m.render("Your Statistics", True, COLOR_TEXT)
        self.screen.blit(title, (20, 20))
        total_hours = self.stats.stats["total_focus_time"] // 3600
        total_mins = (self.stats.stats["total_focus_time"] % 3600) // 60

        stats_lines = [
            f"Total Focus Time: {total_hours}h {total_mins}m",
            f"Total Sessions: {self.stats.stats['total_sessions']}",
            f"Longest Streak: {self.stats.stats['longest_streak']} sessions",
            f"Current Streak: {self.stats.stats['current_streak']} sessions",
            "",
            "Daily Performance:",
        ]

        today = datetime.now()
        for i in range(6, -1, -1):
            day = (today - __import__('datetime').timedelta(days=i)).strftime("%Y-%m-%d")
            sessions = self.stats.stats["daily_records"].get(day, 0)
            task_score = self.stats.stats["daily_task_scores"].get(day, 0)
            day_name = (today - __import__('datetime').timedelta(days=i)).strftime("%a")
            stats_lines.append(f"  {day_name}: {sessions} sessions | {task_score} pts")

        start_y_pos = 50
        for line in stats_lines:
            if line and not line.startswith(" "):
                color = COLOR_TEXT
            else:
                color = COLOR_DIM
            surf = self.font_s.render(line, True, color)
            self.screen.blit(surf, (20, start_y_pos))
            start_y_pos += 25

    # Main Loop
    def run(self) -> None:
        """Main application loop"""
        while True:
            dt = self.clock.tick(FPS)/1000

            for e in pg.event.get():
                # Exit and resizing
                if e.type == pg.QUIT:
                    self.tasks.save()
                    self._resize_for_tasks()
                    self.stats.save()
                    return
                elif e.type == pg.VIDEORESIZE:
                    if e.w < BASE_W or e.h < BASE_H:
                        #self._resize_for_tasks()
                        pg.display.set_mode((BASE_W, BASE_H), pg.RESIZABLE)

                # Splash screen
                if self.mode == AppMode.SPLASH:
                    if e.type == pg.MOUSEBUTTONDOWN:
                        self.mode = AppMode.MAIN
                    continue

                # Undo deleted item
                if e.type == pg.KEYDOWN and e.key == pg.K_z and pg.key.get_mods() & pg.KMOD_CTRL:
                    if self._undo_cache:
                        self.tasks.tasks.append(self._undo_cache.pop())
                        self.tasks.save()
                        self._resize_for_tasks()

                # Hover update
                if e.type == pg.MOUSEMOTION:
                    self.hover = self.task_at(e.pos) if self.mode == AppMode.MAIN else None
                    # Dragging logic
                    if self.mouse_down_pos and self.hover is not None:
                        dx = abs(e.pos[0] - self.mouse_down_pos[0])
                        dy = abs(e.pos[1] - self.mouse_down_pos[1])
                        if dx > 5 or dy > 5:
                            self.dragging_task = self.task_at(self.mouse_down_pos)

                # Left mouse button down
                if e.type == pg.MOUSEBUTTONDOWN and e.button == 1:
                    self.mouse_down_pos = e.pos
                    # Double click detection
                    idx = self.task_at(e.pos)
                    now = pg.time.get_ticks()
                    if idx is not None:
                        if self.last_click_pos == idx and now - self.last_click_time <= self.double_click_threshold:
                            # DOUBLE CLICK: edit task
                            t = self.tasks.tasks[idx]
                            txt = Dialogs.multiline_text("Edit Task", t.text)
                            if txt:
                                t.text = txt
                                score = Dialogs.task_score(str(t.score))
                                if score:
                                    t.score = score
                                self.tasks.save()
                                self._resize_for_tasks()
                            self.last_click_time = 0
                            self.last_click_pos = None
                        else:
                            self.last_click_time = now
                            self.last_click_pos = idx

                    # Handle main screen buttons
                    if self.mode == AppMode.MAIN:
                        if self.btn_start.rect.collidepoint(e.pos):
                            self.timer.start() if not self.timer.running else self.timer.stop()
                        elif self.btn_custom.rect.collidepoint(e.pos):
                            mins = Dialogs.minutes()
                            try: pg.display.set_mode((BASE_W, BASE_H), pg.RESIZABLE)
                            except: pass
                            if mins: self.timer.reset(total=mins*60)
                        elif self.btn_add.rect.collidepoint(e.pos):
                            txt = Dialogs.multiline_text("New Task")
                            try: pg.display.set_mode((BASE_W, BASE_H), pg.RESIZABLE)
                            except: pass
                            if txt:
                                score = Dialogs.task_score()
                                if score: self.tasks.tasks.append(Task(txt, score=score))
                                else: self.tasks.tasks.append(Task(txt))
                                self.tasks.save()
                                self._resize_for_tasks()
                        elif self.btn_instructions.rect.collidepoint(e.pos):
                            self.mode = AppMode.INSTRUCTIONS
                        elif self.btn_stats.rect.collidepoint(e.pos):
                            self.mode = AppMode.STATS

                # Left mouse button up
                if e.type == pg.MOUSEBUTTONUP and e.button == 1:
                    idx = self.task_at(e.pos)
                    # Dragging: reorder tasks
                    if self.dragging_task is not None and idx is not None and self.dragging_task != idx:
                        task = self.tasks.tasks.pop(self.dragging_task)
                        self.tasks.tasks.insert(idx, task)
                        self.tasks.save()
                    # Single click toggle (only if no drag)
                    elif self.dragging_task is None and idx is not None and self.mode == AppMode.MAIN:
                        self.edit_or_toggle(e.pos)
                    self.dragging_task = None
                    self.mouse_down_pos = None

                # Right click delete
                if e.type == pg.MOUSEBUTTONDOWN and e.button == 3 and self.hover is not None and self.mode == AppMode.MAIN:
                    root = tk.Tk()
                    root.withdraw()
                    confirm = messagebox.askyesno("Delete Task?", "Are you sure you want to delete this task?", parent=root)
                    root.destroy()
                    if confirm:
                        self._undo_cache.append(self.tasks.tasks.pop(self.hover))
                        self.tasks.save()
                        self._resize_for_tasks()

                # Back button
                if e.type == pg.MOUSEBUTTONDOWN and e.button == 1:
                    if self.mode in (AppMode.INSTRUCTIONS, AppMode.STATS):
                        if self.btn_back.rect.collidepoint(e.pos):
                            self.mode = AppMode.MAIN
                            continue

            # Timer update
            if self.mode == AppMode.MAIN:
                if self.timer.update(dt):
                    self._play_alarm()
                    Dialogs.finished()
                    pg.mixer.stop()
                    self.stats.record_session(DEFAULT_POMODORO)
                    if self.timer.is_break:
                        self.timer.start_focus_session()
                    else:
                        self.timer.complete_session()

            # Drawing
            if self.mode == AppMode.SPLASH:
                self.draw_splash()
            elif self.mode == AppMode.MAIN:
                self.draw_main()
            elif self.mode == AppMode.INSTRUCTIONS:
                self.draw_instructions()
            elif self.mode == AppMode.STATS:
                self.draw_stats()

            pg.display.flip()

if __name__ == "__main__":
    FocusApp().run()
