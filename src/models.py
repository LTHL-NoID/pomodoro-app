from enum import Enum
from dataclasses import dataclass

import pygame as pg
from src.config import *

@dataclass
class Task:
    """A task item"""
    text: str
    complete: bool = False
    score: int = 10

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

# Models
class AppMode(Enum):
    """Application modes/screens"""
    SPLASH = 1
    MAIN = 2
    INSTRUCTIONS = 3
    STATS = 4

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