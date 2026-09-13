"""Emoji shortcode → Unicode conversion."""

from __future__ import annotations

import re

EMOJI_MAP: dict[str, str] = {
    ":smile:": "😊", ":grin:": "😁", ":laugh:": "😄", ":joy:": "😂",
    ":wink:": "😉", ":heart:": "❤️", ":thumbsup:": "👍", ":thumbsdown:": "👎",
    ":clap:": "👏", ":fire:": "🔥", ":star:": "⭐", ":check:": "✅",
    ":x:": "❌", ":warning:": "⚠️", ":info:": "ℹ️", ":question:": "❓",
    ":wave:": "👋", ":eyes:": "👀", ":muscle:": "💪", ":party:": "🎉",
    ":rocket:": "🚀", ":bug:": "🐛", ":code:": "💻", ":coffee:": "☕",
    ":sun:": "☀️", ":moon:": "🌙", ":rain:": "🌧️", ":snow:": "❄️",
    ":dog:": "🐶", ":cat:": "🐱", ":pizza:": "🍕", ":cake:": "🎂",
    ":cry:": "😢", ":angry:": "😠", ":cool:": "😎", ":think:": "🤔",
    ":ok:": "👌", ":pray:": "🙏", ":100:": "💯", ":tada:": "🎊",
}

_PATTERN = re.compile("|".join(re.escape(k) for k in EMOJI_MAP))


def replace_emoji(text: str) -> str:
    """Replace all emoji shortcodes in text with Unicode characters."""
    return _PATTERN.sub(lambda m: EMOJI_MAP[m.group(0)], text)
