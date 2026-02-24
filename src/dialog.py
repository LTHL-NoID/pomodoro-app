import threading
import pygame as pg
import random
from src.config import *
import tkinter as tk
from tkinter import simpledialog

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
            text=random.choice(WH40K_QUOTES),
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
