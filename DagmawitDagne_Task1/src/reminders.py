"""Reminder helper functions for the voice assistant."""

from __future__ import annotations

import subprocess
import threading
from typing import Callable


def _send_desktop_notification(title: str, message: str) -> None:
    """Send a desktop notification using notify-send (Ubuntu/Linux)."""
    try:
        subprocess.run(
            ["notify-send", title, message],
            check=False,
            timeout=5,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass  # notify-send not available, silently skip


def _fire_reminder(task: str, speak_fn: Callable[[str], None]) -> None:
    """Called by the timer when the reminder is due."""
    message = f"Reminder: {task}"
    print(f"\n⏰ {message}")

    # Desktop notification
    _send_desktop_notification("⏰ Reminder", task)

    # Speak it out loud
    try:
        speak_fn(message)
    except Exception:
        pass


def schedule_reminder(
    minutes: int,
    task: str,
    speak_fn: Callable[[str], None],
) -> str:
    """Start a background timer and return an immediate confirmation string."""
    task_name = (task or "your task").strip() or "your task"
    delay_seconds = max(1, int(minutes)) * 60

    timer = threading.Timer(
        delay_seconds,
        _fire_reminder,
        args=(task_name, speak_fn),
    )
    timer.daemon = True  # won't block the process from exiting
    timer.start()

    return f"Reminder set for {minutes} minutes from now: {task_name}."


def create_reminder(task: str, minutes: int = 5) -> str:
    """Build a reminder message string (used in tests and simple contexts)."""
    task_name = (task or "your task").strip() or "your task"
    return f"Reminder set for {minutes} minutes from now: {task_name}."
