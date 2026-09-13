"""Localization support for the voice assistant.

Supports English (en) and Amharic (am).
"""

from __future__ import annotations
import re

# ---------------------------------------------------------------------------
# Intent patterns per language
# ---------------------------------------------------------------------------
INTENT_PATTERNS: dict[str, dict[str, list[str]]] = {
    "en": {
        "greeting": ["hello", "hi", "hey"],
        "time":     ["time is it", "current time", "time"],
        "date":     ["date is it", "today's date", "date"],
        "weather":  ["weather", "forecast"],
        "search":   ["search for", "look up", "google", "search"],
        "reminder": ["remind"],
        "email":    ["email"],
        "knowledge":["who is", "who was", "what is", "what are", "what was",
                     "tell me about", "explain", "describe"],
        "custom":   ["open", "launch", "start", "run"],
    },
    "am": {
        "greeting": ["ሰላም", "ሄሎ", "ሃይ"],
        "time":     ["ሰዓቱ ስንት ነው", "ሰዓቱ", "ሰዓት"],
        "date":     ["ቀኑ ስንት ነው", "ዛሬ ቀን", "ቀን"],
        "weather":  ["የአየር ሁኔታ", "አየር ሁኔታ", "የአየር"],
        "search":   ["ፈልግ", "ፈልጉ", "ፍለጋ", "ፈልጋ"],
        "reminder": ["አስታውሰኝ", "ማስታወሻ"],
        "email":    ["ኢሜይል", "ኢሜይሌን ፈትሽ", "ኢሜይሌን"],
        "knowledge":["ማን ነው", "ምንድን ነው", "ምን ነው", "ንገረኝ", "አብራራ"],
        "custom":   ["ክፈት", "አስጀምር", "ጀምር"],
    },
}

# ---------------------------------------------------------------------------
# Response templates per language
# ---------------------------------------------------------------------------
RESPONSES: dict[str, dict[str, str]] = {
    "en": {
        "greeting":     "Hello! How can I help you?",
        "unknown":      "I heard you, but I need a better command.",
        "empty":        "I didn't catch that. Please say it again.",
        "reminder_set": "Reminder set for {minutes} minutes from now: {task}.",
        "email_needed": "I need your Gmail credentials to check your inbox.",
        "opening":      "Opening {task}.",
        "search_info":  "I can search for {query}. Open a browser to look it up.",
    },
    "am": {
        "greeting":     "ሰላም! እንዴት ልረዳዎ?",
        "unknown":      "ሰምቻለሁ፣ ነገር ግን የተሻለ ትዕዛዝ ያስፈልገኛል።",
        "empty":        "አልሰማሁም። እባክዎ ድጋሚ ይናገሩ።",
        "reminder_set": "ማስታወሻ ከዛሬ ጀምሮ {minutes} ደቂቃ ውስጥ ተቀናብሯል: {task}።",
        "email_needed": "ኢሜይልዎን ለማየት የ Gmail ምስክርነት ያስፈልጋል።",
        "opening":      "{task} እየከፈትኩ ነው።",
        "search_info":  "{query} ፍለጋ ጀምሯል።",
    },
}

# ---------------------------------------------------------------------------
# Weather response templates
# ---------------------------------------------------------------------------
WEATHER_TEMPLATES: dict[str, str] = {
    "en": "The weather in {city} is {description} with a temperature of {temp}°C.",
    "am": "በ{city} የአየር ሁኔታ {description} ሲሆን የሙቀት መጠኑ {temp}°C ነው።",
}

TIME_TEMPLATES: dict[str, str] = {
    "en": "The current time is {time}.",
    "am": "አሁን ሰዓቱ {time} ነው።",
}

DATE_TEMPLATES: dict[str, str] = {
    "en": "The date is {date}.",
    "am": "ዛሬ {date} ነው።",
}


# ---------------------------------------------------------------------------
# Language detection
# ---------------------------------------------------------------------------
def detect_language(text: str) -> str:
    """Return 'am' if text contains Amharic characters, else 'en'."""
    if not text:
        return "en"
    # Amharic Unicode block: U+1200–U+137F
    for ch in text:
        if "\u1200" <= ch <= "\u137f":
            return "am"
    return "en"


# ---------------------------------------------------------------------------
# Intent detection (language-aware)
# ---------------------------------------------------------------------------
def detect_intent(text: str) -> tuple[str, str]:
    """Return (intent, language) for the given text."""
    query = (text or "").strip().lower()
    if not query:
        return "unknown", "en"

    lang = detect_language(text)
    patterns = INTENT_PATTERNS.get(lang, INTENT_PATTERNS["en"])

    # Check in priority order
    for intent in ["greeting", "weather", "reminder", "email",
                   "knowledge", "custom", "search", "time", "date"]:
        if intent in patterns:
            if any(term in query for term in patterns[intent]):
                return intent, lang

    # Fallback: also check English patterns if Amharic detected nothing
    if lang == "am":
        en_patterns = INTENT_PATTERNS["en"]
        for intent in ["greeting", "weather", "reminder", "email",
                       "knowledge", "custom", "search", "time", "date"]:
            if any(term in query for term in en_patterns[intent]):
                return intent, "en"

    return "unknown", lang


# ---------------------------------------------------------------------------
# Info extraction (language-aware)
# ---------------------------------------------------------------------------
def extract_info(text: str, lang: str = "en") -> dict:
    """Extract structured info from the query."""
    query = (text or "").strip()
    info: dict = {"city": "", "task": "", "minutes": 5, "query": query}

    if lang == "am":
        # City: "የ<city> የአየር ሁኔታ" or "የ<city>"
        city_match = re.search(r"የ(.+?)\s+የአየር", query)
        if not city_match:
            city_match = re.search(r"^የ(\S+)", query)
        if city_match:
            info["city"] = city_match.group(1).strip()

        # Minutes: Amharic numbers or Arabic numerals
        min_match = re.search(r"(\d+)\s*ደቂቃ", query)
        if min_match:
            info["minutes"] = int(min_match.group(1))

        # Task after "ለ" or "ማስታወሻ"
        task_match = re.search(r"ለ\s*(.+)$", query)
        if task_match:
            info["task"] = task_match.group(1).strip()

        # Search query — strip intent keywords
        for kw in ["ፈልግ", "ፈልጉ", "ፍለጋ"]:
            if kw in query:
                info["query"] = query.replace(kw, "").strip()

    else:
        # English extraction
        city_match = re.search(r"\bin\s+(.+)$", query, re.IGNORECASE)
        if city_match:
            info["city"] = city_match.group(1).strip()

        min_match = re.search(r"in\s+(\d+)\s+minutes?", query, re.IGNORECASE)
        if min_match:
            info["minutes"] = int(min_match.group(1))

        task_match = re.search(r"\bto\s+(.+)$", query, re.IGNORECASE)
        if task_match:
            info["task"] = task_match.group(1).strip()

        for prefix in ["search for", "look up", "google"]:
            if prefix in query.lower():
                info["query"] = query.lower().replace(prefix, "").strip()
                break

    return info


# ---------------------------------------------------------------------------
# Get response string
# ---------------------------------------------------------------------------
def get_response_text(key: str, lang: str = "en", **kwargs) -> str:
    """Return a localized response string."""
    templates = RESPONSES.get(lang, RESPONSES["en"])
    template = templates.get(key, RESPONSES["en"].get(key, ""))
    if kwargs:
        return template.format(**kwargs)
    return template
