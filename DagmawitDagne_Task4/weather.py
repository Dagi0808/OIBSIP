"""Weather API layer — fetches current weather, forecast, and IP location."""

from __future__ import annotations

import os

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.openweathermap.org/data/2.5"
ICON_URL = "https://openweathermap.org/img/wn/{}@2x.png"
IPINFO_URL = "https://ipinfo.io/json"


def _api_key() -> str:
    key = os.getenv("OPENWEATHER_API_KEY", "")
    if not key:
        raise ValueError("OPENWEATHER_API_KEY is not set in your .env file.")
    return key


def get_current_weather(city: str, units: str = "metric") -> dict:
    """Fetch current weather for a city.

    Args:
        city: City name or ZIP code.
        units: 'metric' (°C) or 'imperial' (°F).

    Returns:
        Parsed JSON dict from OpenWeatherMap.

    Raises:
        ValueError: City not found or invalid input.
        ConnectionError: Network or API error.
    """
    city = (city or "").strip()
    if not city:
        raise ValueError("City name cannot be empty.")

    try:
        response = requests.get(
            f"{BASE_URL}/weather",
            params={"q": city, "appid": _api_key(), "units": units},
            timeout=10,
        )
    except requests.exceptions.Timeout:
        raise ConnectionError("Request timed out. Check your internet connection.")
    except requests.exceptions.RequestException as exc:
        raise ConnectionError(f"Network error: {exc}")

    if response.status_code == 401:
        raise ValueError("Invalid API key. Check your OPENWEATHER_API_KEY.")
    if response.status_code == 404:
        raise ValueError(f"City '{city}' not found. Try a different name.")
    if response.status_code != 200:
        raise ConnectionError(f"API error {response.status_code}: {response.text}")

    return response.json()


def get_forecast(city: str, units: str = "metric") -> dict:
    """Fetch 5-day / 3-hour forecast for a city."""
    city = (city or "").strip()
    if not city:
        raise ValueError("City name cannot be empty.")

    try:
        response = requests.get(
            f"{BASE_URL}/forecast",
            params={"q": city, "appid": _api_key(), "units": units, "cnt": 40},
            timeout=10,
        )
    except requests.exceptions.Timeout:
        raise ConnectionError("Request timed out. Check your internet connection.")
    except requests.exceptions.RequestException as exc:
        raise ConnectionError(f"Network error: {exc}")

    if response.status_code == 401:
        raise ValueError("Invalid API key. Check your OPENWEATHER_API_KEY.")
    if response.status_code == 404:
        raise ValueError(f"City '{city}' not found.")
    if response.status_code != 200:
        raise ConnectionError(f"API error {response.status_code}: {response.text}")

    return response.json()


def get_icon_url(icon_code: str) -> str:
    """Return the URL for a weather icon."""
    return ICON_URL.format(icon_code)


def detect_city_from_ip() -> str:
    """Detect the user's city from their IP address using ipinfo.io."""
    try:
        response = requests.get(IPINFO_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("city", "")
    except requests.exceptions.RequestException:
        pass
    return ""
