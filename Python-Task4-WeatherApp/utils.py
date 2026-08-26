"""Utility helpers for the weather app."""

from __future__ import annotations

import io
import os
from datetime import datetime

import requests
from PIL import Image, ImageTk


def celsius_to_fahrenheit(celsius: float) -> float:
    return celsius * 9 / 5 + 32


def fahrenheit_to_celsius(fahrenheit: float) -> float:
    return (fahrenheit - 32) * 5 / 9


def format_temp(temp: float, unit: str) -> str:
    """Format temperature with unit symbol."""
    symbol = "°C" if unit == "metric" else "°F"
    return f"{temp:.1f}{symbol}"


def format_wind(speed: float, unit: str) -> str:
    """Format wind speed with unit."""
    label = "m/s" if unit == "metric" else "mph"
    return f"{speed:.1f} {label}"


def epoch_to_time(epoch: int, fmt: str = "%I:%M %p") -> str:
    """Convert Unix epoch to readable time string."""
    return datetime.fromtimestamp(epoch).strftime(fmt)


def epoch_to_day(epoch: int) -> str:
    """Convert Unix epoch to day name."""
    return datetime.fromtimestamp(epoch).strftime("%A")


def epoch_to_date(epoch: int) -> str:
    """Convert Unix epoch to short date string."""
    return datetime.fromtimestamp(epoch).strftime("%b %d")


def load_icon(icon_code: str, size: tuple[int, int] = (64, 64)) -> ImageTk.PhotoImage | None:
    """Download and return a tkinter-compatible weather icon image."""
    url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
    try:
        response = requests.get(url, timeout=8)
        if response.status_code == 200:
            img = Image.open(io.BytesIO(response.content)).convert("RGBA")
            img = img.resize(size, Image.LANCZOS)
            return ImageTk.PhotoImage(img)
    except Exception:
        pass
    return None


def load_small_icon(icon_code: str) -> ImageTk.PhotoImage | None:
    """Load a small (40x40) icon for forecast cards."""
    return load_icon(icon_code, size=(40, 40))


def parse_current(data: dict, unit: str = "metric") -> dict:
    """Extract display-ready fields from current weather API response."""
    main = data.get("main", {})
    weather = data.get("weather", [{}])[0]
    wind = data.get("wind", {})
    sys = data.get("sys", {})

    return {
        "city": data.get("name", ""),
        "country": sys.get("country", ""),
        "temp": main.get("temp", 0),
        "feels_like": main.get("feels_like", 0),
        "temp_min": main.get("temp_min", 0),
        "temp_max": main.get("temp_max", 0),
        "humidity": main.get("humidity", 0),
        "description": weather.get("description", "").title(),
        "icon": weather.get("icon", "01d"),
        "wind_speed": wind.get("speed", 0),
        "wind_deg": wind.get("deg", 0),
        "visibility": data.get("visibility", 0) // 1000,  # km
        "sunrise": sys.get("sunrise", 0),
        "sunset": sys.get("sunset", 0),
        "unit": unit,
    }


def parse_hourly(forecast_data: dict, count: int = 6) -> list[dict]:
    """Extract the next `count` 3-hour forecast entries."""
    items = forecast_data.get("list", [])[:count]
    result = []
    for item in items:
        weather = item.get("weather", [{}])[0]
        main = item.get("main", {})
        result.append({
            "time": epoch_to_time(item.get("dt", 0)),
            "temp": main.get("temp", 0),
            "icon": weather.get("icon", "01d"),
            "description": weather.get("description", "").title(),
        })
    return result


def parse_daily(forecast_data: dict) -> list[dict]:
    """Extract one entry per day (noon reading) for the next 5 days."""
    items = forecast_data.get("list", [])
    seen_days: set[str] = set()
    result = []

    for item in items:
        dt = item.get("dt", 0)
        day = epoch_to_day(dt)
        date = epoch_to_date(dt)
        day_key = date

        if day_key in seen_days:
            continue
        seen_days.add(day_key)

        weather = item.get("weather", [{}])[0]
        main = item.get("main", {})
        result.append({
            "day": day,
            "date": date,
            "temp_max": main.get("temp_max", main.get("temp", 0)),
            "temp_min": main.get("temp_min", main.get("temp", 0)),
            "icon": weather.get("icon", "01d"),
            "description": weather.get("description", "").title(),
        })

        if len(result) == 5:
            break

    return result
