import os, json
from datetime import datetime
from typing import List
from src.models import Task
from src.config import *

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