"""Weather-related helper functions for the voice assistant."""

from __future__ import annotations

import os

import requests
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_weather(city: str) -> str:
    """Return a real weather response for a city using OpenWeatherMap."""
    city_name = (city or "Addis Ababa").strip() or "Addis Ababa"
    api_key = os.getenv("OPENWEATHER_API_KEY")

    if not api_key:
        return (
            f"Weather for {city_name} is unavailable because OPENWEATHER_API_KEY "
            "is not configured in your environment."
        )

    params = {
        "q": city_name,
        "appid": api_key,
        "units": "metric",
    }

    try:
        response = requests.get(OPENWEATHER_URL, params=params, timeout=10)
        if response.status_code != 200:
            return f"I couldn't fetch the weather for {city_name} right now."

        data = response.json()
        weather = data.get("weather", [{}])[0]
        main = data.get("main", {})
        description = weather.get("description", "clear sky")
        temperature = main.get("temp")

        if temperature is None:
            return f"The weather in {city_name} is {description}."

        return (
            f"The weather in {city_name} is {description} with a temperature of "
            f"{temperature}°C."
        )
    except requests.RequestException:
        return f"I couldn't fetch the weather for {city_name} right now."
