import re

from src.config import load_commands


def _load_intent_patterns():
    fallback = {
        "greeting": ["hello", "hi", "hey"],
        "time": ["time is it", "current time", "time"],
        "date": ["date is it", "today's date", "date"],
        "search": ["search for", "look up", "google", "search"],
        "weather": ["weather"],
        "reminder": ["remind"],
        "email": ["email"],
        "custom": ["open", "launch", "start", "run"],
    }

    data = load_commands()
    commands = data.get("commands", [])
    patterns = {}

    for command in commands:
        if not isinstance(command, dict):
            continue
        name = command.get("name")
        items = command.get("patterns", [])
        if not isinstance(name, str):
            continue
        patterns[name] = [str(item).lower() for item in items if isinstance(item, str)]

    return {**fallback, **patterns}


INTENT_PATTERNS = _load_intent_patterns()


def detect_intent(text: str) -> str:
    query = (text or "").strip().lower()
    if not query:
        return "unknown"

    if any(term in query for term in INTENT_PATTERNS["greeting"]):
        return "greeting"
    if any(term in query for term in INTENT_PATTERNS["weather"]):
        return "weather"
    if any(term in query for term in INTENT_PATTERNS["reminder"]):
        return "reminder"
    if any(term in query for term in INTENT_PATTERNS["email"]):
        return "email"
    if any(term in query for term in INTENT_PATTERNS["custom"]):
        return "custom"
    if any(term in query for term in INTENT_PATTERNS["search"]):
        return "search"
    if any(term in query for term in INTENT_PATTERNS["time"]):
        return "time"
    if any(term in query for term in INTENT_PATTERNS["date"]):
        return "date"

    return "unknown"


def extract_info(text: str):
    query = (text or "").strip()
    if not query:
        return {"intent": "unknown", "city": "", "task": "", "minutes": 5, "query": ""}

    intent = detect_intent(query)
    info = {"intent": intent, "city": "", "task": "", "minutes": 5, "query": query}

    if intent == "weather":
        match = re.search(r"in\s+(.+)$", query, flags=re.IGNORECASE)
        if match:
            info["city"] = match.group(1).strip()
        elif "addis" in query.lower():
            info["city"] = "Addis Ababa"

    if intent == "reminder":
        match = re.search(r"in\s+(\d+)\s+minutes?", query, flags=re.IGNORECASE)
        if match:
            info["minutes"] = int(match.group(1))
        if "email" in query.lower():
            info["task"] = "check my email"

    if intent == "search":
        cleaned = query.lower()
        for prefix in ["search for", "look up", "google"]:
            if prefix in cleaned:
                cleaned = cleaned.replace(prefix, "", 1)
        info["query"] = cleaned.strip()

    if intent == "email":
        info["task"] = "check my email"

    if intent == "custom":
        info["task"] = re.sub(r"^(open|launch|start|run)\s+", "", query, flags=re.IGNORECASE).strip()

    return info
