"""Intent detection — delegates to locales.py for language-aware detection."""

from __future__ import annotations

try:
    from src.locales import detect_intent as _detect, extract_info as _extract
except ModuleNotFoundError:
    from locales import detect_intent as _detect, extract_info as _extract


def detect_intent(text: str) -> str:
    """Return intent string (language-agnostic wrapper)."""
    intent, _ = _detect(text)
    return intent


def extract_info(text: str) -> dict:
    """Return extracted info dict (language-agnostic wrapper)."""
    from src.locales import detect_language
    lang = detect_language(text)
    return _extract(text, lang)
