"""General knowledge lookup using the Wikipedia REST API."""

from __future__ import annotations

import re

import requests

WIKIPEDIA_SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{topic}"
WIKIPEDIA_SEARCH_URL = "https://en.wikipedia.org/w/api.php"


def _is_relevant(topic: str, page_title: str) -> bool:
    """Check if the Wikipedia page title is relevant to the topic."""
    stop_words = {"the", "a", "an", "of", "in", "is", "are", "was", "were",
                  "and", "or", "for", "to", "at", "by", "with", "only", "any",
                  "that", "does", "not", "letter", "appear", "which", "what",
                  "who", "how", "why", "when", "where", "tell", "me", "about",
                  "explain", "describe"}

    topic_words = [w.lower() for w in re.split(r"\W+", topic) if len(w) > 3]
    meaningful_words = [w for w in topic_words if w not in stop_words]

    # Trivia/question queries are typically long (7+ meaningful words)
    # Knowledge queries are short: "Albert Einstein", "machine learning", "Ethiopia"
    if len(meaningful_words) > 5:
        return False

    title_words = {w.lower() for w in re.split(r"\W+", page_title) if len(w) > 3} - stop_words
    topic_set = set(meaningful_words)

    if not topic_set or not title_words:
        return True

    overlap = topic_set & title_words
    relevance_ratio = len(overlap) / len(title_words)
    return relevance_ratio >= 0.5


def get_knowledge(query: str) -> str:
    """Return a Wikipedia summary for the given query."""
    topic = _extract_topic(query)
    if not topic:
        return "What would you like to know about?"

    # If the topic is a long question sentence (7+ words), it's likely trivia
    # Wikipedia is an encyclopedia, not a trivia engine
    if len(topic.split()) > 6:
        return "I couldn't find a direct answer to that. Try searching for it."

    # First try direct lookup
    result = _fetch_summary(topic)
    if result:
        return result

    # Fall back to search API to find the best matching page
    best_title = _search_wikipedia(topic)
    if not best_title:
        return f"I couldn't find a direct answer to that. Try searching for it."

    if not _is_relevant(topic, best_title):
        return f"I couldn't find a direct answer to that. Try searching for it."

    result = _fetch_summary(best_title)
    if result:
        return result

    return f"I couldn't find anything about '{topic}' on Wikipedia."


def _fetch_summary(topic: str) -> str | None:
    """Fetch a Wikipedia page summary. Returns None if not found or disambiguation."""
    url = WIKIPEDIA_SUMMARY_URL.format(topic=requests.utils.quote(topic))
    try:
        response = requests.get(
            url, timeout=10, headers={"User-Agent": "VoiceAssistant/1.0"}
        )
        if response.status_code != 200:
            return None

        data = response.json()

        # Skip disambiguation pages
        if data.get("type") == "disambiguation":
            return None

        extract = data.get("extract", "").strip()
        if not extract:
            return None

        # Return first 2 sentences
        sentences = re.split(r"(?<=[.!?])\s+", extract)
        return " ".join(sentences[:2])

    except requests.RequestException:
        return None


def _search_wikipedia(topic: str) -> str | None:
    """Use Wikipedia's search API to find the best matching page title."""
    params = {
        "action": "query",
        "list": "search",
        "srsearch": topic,
        "format": "json",
        "srlimit": 1,
    }
    try:
        response = requests.get(
            WIKIPEDIA_SEARCH_URL,
            params=params,
            timeout=10,
            headers={"User-Agent": "VoiceAssistant/1.0"},
        )
        if response.status_code != 200:
            return None

        results = response.json().get("query", {}).get("search", [])
        if results:
            return results[0]["title"]
        return None

    except requests.RequestException:
        return None


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
            return text[len(prefix):].strip()
    return text
