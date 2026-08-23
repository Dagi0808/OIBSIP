import datetime
import urllib.parse
import webbrowser

from src.weather import get_weather


def get_time_response() -> str:
    now = datetime.datetime.now()
    return f"The current time is {now.strftime('%I:%M %p')}."


def get_date_response() -> str:
    now = datetime.datetime.now()
    return f"The date is {now.strftime('%A, %B %d, %Y')}."


def get_search_response(query: str) -> str:
    cleaned = (
        query.lower()
        .replace("search for", "")
        .replace("look up", "")
        .replace("search", "")
        .replace("google", "")
        .strip()
    )

    if not cleaned:
        return "What would you like me to search for?"

    return f"I can search for {cleaned}. Open a browser to look it up."


def open_search_in_browser(query: str) -> str:
    cleaned = query.strip()
    if not cleaned:
        return "What would you like me to search for?"

    encoded = urllib.parse.quote(cleaned)
    url = f"https://www.google.com/search?q={encoded}"
    webbrowser.open(url)
    return f"Searching the web for: {cleaned}"


def get_weather_response(city: str) -> str:
    city_name = (city or "").strip()
    if not city_name:
        return "Which city would you like the weather for?"

    return get_weather(city_name)


def create_reminder_response(minutes: int, task: str) -> str:
    task_text = (task or "your task").strip()
    return f"Reminder set for {minutes} minutes from now: {task_text}."
