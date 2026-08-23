"""General knowledge lookup using the Wikipedia REST API."""

from __future__ import annotations

import re

import requests

WIKIPEDIA_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{topic}"


def get_knowledge(query: str) -> str:
    """Return a Wikipedia summary for the given query."""
    topic = _extract_topic(query)
    if not topic:
        return "What would you like to know about?"

    url = WIKIPEDIA_URL.format(topic=requests.utils.quote(topic))

    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "VoiceAssistant/1.0"})

        if response.status_code == 404:
            return f"I couldn't find anything about '{topic}' on Wikipedia."

        if response.status_code != 200:
            return f"I had trouble looking up '{topic}' right now."

        data = response.json()

        # Prefer the extract (plain text summary)
        extract = data.get("extract", "").strip()
        if not extract:
            return f"I found a page for '{topic}' but it had no summary."

        # Limit to first 2 sentences for a concise spoken response
        sentences = re.split(r"(?<=[.!?])\s+", extract)
        summary = " ".join(sentences[:2])
        return summary

    except requests.RequestException:
        return f"I couldn't connect to Wikipedia right now."


def _extract_topic(query: str) -> str:
    """Strip intent keywords to get the bare topic."""
    text = (query or "").strip()
    prefixes = [
        "who is", "who was", "who are",
        "what is", "what are", "what was",
        "tell me about", "explain", "describe",
        "search for", "look up",
    ]
    lower = text.lower()
    for prefix in prefixes:
        if lower.startswith(prefix):
            topic = text[len(prefix):].strip()
            return topic
    return text
