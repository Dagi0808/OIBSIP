"""Helper utilities for loading assistant command configuration."""

from __future__ import annotations

import json
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "commands.json"


def load_commands() -> dict:
    """Load command definitions from the JSON config file."""
    if not CONFIG_PATH.exists():
        return {"commands": []}

    try:
        with CONFIG_PATH.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, OSError):
        return {"commands": []}

    if isinstance(data, dict):
        return data
    return {"commands": []}


def get_command_names() -> list[str]:
    """Return the configured command names."""
    commands = load_commands().get("commands", [])
    return [command.get("name") for command in commands if isinstance(command, dict)]
