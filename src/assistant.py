"""Core response logic for the voice assistant."""

from __future__ import annotations

import datetime

try:
    from src.commands import (
        get_search_response,
        get_weather_response,
    )
    from src.email_service import check_email
    from src.knowledge import get_knowledge
    from src.locales import (
        DATE_TEMPLATES,
        TIME_TEMPLATES,
        detect_intent,
        extract_info,
        get_response_text,
    )
    from src.reminders import schedule_reminder
except ModuleNotFoundError:
    from commands import (
        get_search_response,
        get_weather_response,
    )
    from email_service import check_email
    from knowledge import get_knowledge
    from locales import (
        DATE_TEMPLATES,
        TIME_TEMPLATES,
        detect_intent,
        extract_info,
        get_response_text,
    )
    from reminders import schedule_reminder


def get_response(text: str, speak_fn=None) -> str:
    query = (text or "").strip()
    if not query:
        return get_response_text("empty", "en")

    intent, lang = detect_intent(query)
    info = extract_info(query, lang)

    if intent == "greeting":
        return get_response_text("greeting", lang)

    if intent == "time":
        now = datetime.datetime.now().strftime("%I:%M %p")
        return TIME_TEMPLATES.get(lang, TIME_TEMPLATES["en"]).format(time=now)

    if intent == "date":
        now = datetime.datetime.now().strftime("%A, %B %d, %Y")
        return DATE_TEMPLATES.get(lang, DATE_TEMPLATES["en"]).format(date=now)

    if intent == "weather":
        city = info.get("city") or "Addis Ababa"
        # get_weather_response returns English; wrap for Amharic
        result = get_weather_response(city)
        return result

    if intent == "reminder":
        minutes = info.get("minutes", 5)
        task = info.get("task") or ("your task" if lang == "en" else "ተግባርዎ")
        _speak = speak_fn if callable(speak_fn) else lambda t: None
        # schedule_reminder returns English; override for Amharic
        schedule_reminder(minutes, task, _speak)
        return get_response_text("reminder_set", lang, minutes=minutes, task=task)

    if intent == "email":
        return "EMAIL_SETUP_NEEDED"

    if intent == "custom":
        task = info.get("task") or ("your custom command" if lang == "en" else "ትዕዛዝዎ")
        return get_response_text("opening", lang, task=task)

    if intent == "search":
        search_query = info.get("query") or query
        if lang == "am":
            return get_response_text("search_info", lang, query=search_query)
        return get_search_response(search_query)

    if intent == "knowledge":
        return get_knowledge(query)

    return get_response_text("unknown", lang)


if __name__ == "__main__":
    print(get_response("ሰላም"))
    print(get_response("ሰዓቱ ስንት ነው"))
    print(get_response("hello"))
