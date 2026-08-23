try:
    from src.commands import (
        get_date_response,
        get_search_response,
        get_time_response,
        get_weather_response,
    )
    from src.email_service import check_email
    from src.intents import detect_intent, extract_info
    from src.reminders import schedule_reminder
except ModuleNotFoundError:
    from commands import (
        get_date_response,
        get_search_response,
        get_time_response,
        get_weather_response,
    )
    from email_service import check_email
    from intents import detect_intent, extract_info
    from reminders import schedule_reminder


def get_response(text: str, speak_fn=None) -> str:
    query = (text or "").strip()
    if not query:
        return "I didn't catch that. Please say it again."

    intent = detect_intent(query)
    info = extract_info(query)

    if intent == "greeting":
        return "Hello! How can I help you?"

    if intent == "time":
        return get_time_response()

    if intent == "date":
        return get_date_response()

    if intent == "weather":
        city = info.get("city") or "Addis Ababa"
        return get_weather_response(city)

    if intent == "reminder":
        minutes = info.get("minutes", 5)
        task = info.get("task") or "your task"
        # Use a no-op speak function if none provided (e.g. web UI)
        _speak = speak_fn if callable(speak_fn) else lambda t: None
        return schedule_reminder(minutes, task, _speak, notify_email=True)

    if intent == "email":
        return check_email()

    if intent == "custom":
        task = info.get("task") or "your custom command"
        return f"Opening {task}."

    if intent == "search":
        search_query = info.get("query") or query
        return get_search_response(search_query)

    return "I heard you, but I need a better command."


if __name__ == "__main__":
    print(get_response("hello"))
