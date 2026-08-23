"""Reminder helper functions for the voice assistant."""

from __future__ import annotations


def create_reminder(task: str, minutes: int = 5) -> str:
    """Build a reminder message from a task and time interval."""
    task_name = (task or "your task").strip() or "your task"
    return f"Reminder set for {minutes} minutes from now: {task_name}."
