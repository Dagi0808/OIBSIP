"""System tray entry point for the Voice Assistant.

Starts the Flask web server in a background thread, opens the browser,
and shows a system tray icon with a right-click menu.

Usage:
    python tray.py
"""

from __future__ import annotations

import threading
import webbrowser

import pystray
from PIL import Image, ImageDraw

APP_URL = "http://127.0.0.1:5000"


# ---------------------------------------------------------------------------
# Tray icon image (generated — no external file needed)
# ---------------------------------------------------------------------------
def _create_icon_image(size: int = 64) -> Image.Image:
    """Draw a simple robot-face icon programmatically."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Background circle
    draw.ellipse([2, 2, size - 2, size - 2], fill="#10a37f")

    # Eyes
    eye_y = size // 3
    eye_r = size // 10
    draw.ellipse(
        [size // 3 - eye_r, eye_y - eye_r, size // 3 + eye_r, eye_y + eye_r],
        fill="white",
    )
    draw.ellipse(
        [2 * size // 3 - eye_r, eye_y - eye_r, 2 * size // 3 + eye_r, eye_y + eye_r],
        fill="white",
    )

    # Mouth (smile arc approximated with a rectangle)
    mouth_y = int(size * 0.58)
    draw.arc(
        [size // 4, mouth_y, 3 * size // 4, mouth_y + size // 5],
        start=0, end=180, fill="white", width=max(2, size // 20),
    )

    return img


# ---------------------------------------------------------------------------
# Flask server thread
# ---------------------------------------------------------------------------
def _run_flask() -> None:
    from app import app
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)


# ---------------------------------------------------------------------------
# Tray menu actions
# ---------------------------------------------------------------------------
def _open_browser(_icon=None, _item=None) -> None:
    webbrowser.open(APP_URL)


def _quit(_icon, _item) -> None:
    _icon.stop()
    import os, signal
    os.kill(os.getpid(), signal.SIGTERM)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    # Start Flask in a daemon thread
    flask_thread = threading.Thread(target=_run_flask, daemon=True)
    flask_thread.start()

    # Give Flask a moment to start, then open browser
    def _delayed_open():
        import time
        time.sleep(1.2)
        webbrowser.open(APP_URL)

    threading.Thread(target=_delayed_open, daemon=True).start()

    # Build tray icon
    icon_image = _create_icon_image(64)
    menu = pystray.Menu(
        pystray.MenuItem("🤖 Voice Assistant", None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Open Assistant", _open_browser, default=True),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit", _quit),
    )

    icon = pystray.Icon(
        name="voice-assistant",
        icon=icon_image,
        title="Voice Assistant",
        menu=menu,
    )

    print("Voice Assistant running — tray icon active.")
    print(f"Open {APP_URL} in your browser, or double-click the tray icon.")
    icon.run()


if __name__ == "__main__":
    main()
