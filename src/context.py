"""Conversation context window for the voice assistant.

Resolves follow-up references like:
  "what about Nairobi?"  → after a weather query about Addis Ababa
  "who is she?"          → after mentioning a person
  "remind me again"      → repeats last reminder
  "search that"          → searches the last topic discussed
"""

from __future__ import annotations

import re

# Follow-up trigger words
FOLLOWUP_PATTERNS = [
    r"^what about\b",
    r"^how about\b",
    r"^and in\b",
    r"^what about in\b",
    r"^remind me again\b",
    r"^search that\b",
    r"^look that up\b",
    r"^who is (he|she|they|it)\b",
    r"^what is (it|that|this)\b",
    # Amharic follow-ups
    r"^ስለ\s",
    r"^ደግሞ\s",
]


def is_followup(text: str) -> bool:
    """Return True if the text looks like a follow-up to a previous turn."""
    query = (text or "").strip().lower()
    return any(re.match(p, query) for p in FOLLOWUP_PATTERNS)


def resolve_query(text: str, history: list[dict]) -> str:
    """Enrich a follow-up query using context from recent history.

    Args:
        text: The current user input.
        history: List of {"role": "user"|"assistant", "text": "...", "time": "..."}.

    Returns:
        Enriched query string ready for intent detection.
    """
    if not is_followup(text):
        return text

    query = text.strip()
    recent = [m for m in history[-10:] if m.get("role") == "user"]

    # ── "what about <place>" after weather ──
    place_match = re.match(
        r"^(?:what about|how about|and in|what about in)\s+(.+)$",
        query, re.IGNORECASE
    )
    if place_match:
        subject = place_match.group(1).strip()
        # Find the last intent from history to inherit
        last_intent = _last_intent_type(recent)
        if last_intent == "weather":
            return f"what is the weather in {subject}"
        if last_intent == "knowledge":
            return f"who is {subject}"
        if last_intent == "search":
            return f"search for {subject}"
        # Generic fallback — treat as weather or knowledge
        return f"what is the weather in {subject}"

    # ── "remind me again" ──
    if re.match(r"^remind me again\b", query, re.IGNORECASE):
        last_reminder = _last_text_with_intent(recent, "remind")
        if last_reminder:
            return last_reminder
        return query

    # ── "search that" / "look that up" ──
    if re.match(r"^(?:search that|look that up)\b", query, re.IGNORECASE):
        last_topic = _last_topic(recent)
        if last_topic:
            return f"search for {last_topic}"
        return query

    # ── "who is he/she/they" ──
    pronoun_match = re.match(r"^who is (he|she|they|it)\b", query, re.IGNORECASE)
    if pronoun_match:
        last_person = _last_named_entity(history)
        if last_person:
            return f"who is {last_person}"
        return query

    # ── "what is it/that" ──
    it_match = re.match(r"^what is (it|that|this)\b", query, re.IGNORECASE)
    if it_match:
        last_topic = _last_topic(recent)
        if last_topic:
            return f"what is {last_topic}"
        return query

    # ── Amharic: "ስለ <subject>" (about <subject>) ──
    am_match = re.match(r"^ስለ\s+(.+)$", query)
    if am_match:
        subject = am_match.group(1).strip()
        last_intent = _last_intent_type(recent)
        if last_intent == "weather":
            return f"የ{subject} የአየር ሁኔታ"
        return f"ምንድን ነው {subject}"

    return query


def _last_intent_type(recent_user_msgs: list[dict]) -> str:
    """Guess the intent of the most recent user message."""
    if not recent_user_msgs:
        return ""
    last = recent_user_msgs[-1].get("text", "").lower()
    if any(w in last for w in ["weather", "forecast", "የአየር"]):
        return "weather"
    if any(w in last for w in ["who is", "what is", "tell me", "ምንድን", "ማን"]):
        return "knowledge"
    if any(w in last for w in ["search", "look up", "google", "ፈልግ"]):
        return "search"
    if any(w in last for w in ["remind", "አስታውሰኝ"]):
        return "reminder"
    return ""


def _last_text_with_intent(recent: list[dict], keyword: str) -> str:
    """Return the last user message containing a keyword."""
    for msg in reversed(recent):
        if keyword.lower() in msg.get("text", "").lower():
            return msg["text"]
    return ""


def _last_topic(recent: list[dict]) -> str:
    """Extract the main topic from the last user message."""
    if not recent:
        return ""
    last = recent[-1].get("text", "")
    # Strip common prefixes to get the core topic
    for prefix in ["search for", "look up", "what is", "who is",
                   "tell me about", "what is the weather in"]:
        if last.lower().startswith(prefix):
            return last[len(prefix):].strip()
    return last.strip()


def _last_named_entity(history: list[dict]) -> str:
    """Try to find the last named entity mentioned in assistant responses."""
    for msg in reversed(history):
        if msg.get("role") != "assistant":
            continue
        text = msg.get("text", "")
        # Look for "X is a/was a" pattern — first word(s) are likely the entity
        match = re.match(r"^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:is|was)\b", text)
        if match:
            return match.group(1)
    return ""
