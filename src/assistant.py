try:
    from src.commands import (
        create_reminder_response,
        get_date_response,
        get_search_response,
        get_time_response,
        get_weather_response,
    )
    from src.email_service import check_email
    from src.intents import detect_intent, extract_info
except ModuleNotFoundError:
    from commands import (
        create_reminder_response,
        get_date_response,
        get_search_response,
        get_time_response,
        get_weather_response,
    )
    from email_service import check_email
    from intents import detect_intent, extract_info


def get_response(text: str) -> str:
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
        return create_reminder_response(minutes, task)

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
