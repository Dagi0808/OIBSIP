# Python Voice Assistant

**Dagmawit Dagne — OIBSIP Python Programming — Task 1 (Advanced)**

---

## Overview

A Python-based voice assistant that listens to spoken or typed commands and responds in natural language. Supports both English and Amharic (አማርኛ). Includes a chat-style web UI, a CLI microphone mode, and a system tray desktop app.

---

## Features

- Voice input via microphone (SpeechRecognition + Google Speech API)
- Text-to-speech responses (pyttsx3)
- Current time and date (English and Amharic)
- Live weather lookup — OpenWeatherMap API (English and Amharic responses)
- Web search (Google)
- Timed reminders with desktop notifications (notify-send)
- Email inbox reading via Gmail IMAP (per-user credentials, session-only)
- Wikipedia general knowledge lookup with search fallback
- Amharic localization — intent detection, responses, and UI
- Multi-language speech recognition (8 languages)
- Conversation context window — resolves follow-up references
- Chat-style web UI with dark/light theme toggle
- System tray desktop app (`tray.py`)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.8+ |
| Speech Input | SpeechRecognition, PyAudio |
| Speech Output | pyttsx3 |
| Web UI | Flask |
| Weather API | OpenWeatherMap |
| Knowledge | Wikipedia REST API |
| Email | imaplib (Gmail IMAP) |
| Desktop Notification | notify-send (Ubuntu) |
| System Tray | pystray + Pillow |
| Localization | Custom locales.py (en + am) |
| Config | JSON |
| Environment | python-dotenv |
| Tests | pytest |

---

## Architecture

```
User (voice or text)
        │
        ▼
  tray.py            ← System tray entry point (launches Flask + browser)
  app.py             ← Flask web UI
  src/main.py        ← CLI + microphone entry point
        │
        ▼
  src/assistant.py   ← get_response(text, history)
        │
   src/locales.py    ← Language detection, intent patterns (en + am)
   src/context.py    ← Follow-up resolution (conversation history)
   src/commands.py   ← Time, date, search, reminder handlers
   src/weather.py    ← OpenWeatherMap API
   src/email_service.py ← Gmail IMAP read
   src/knowledge.py  ← Wikipedia API
   src/reminders.py  ← threading.Timer + notify-send
   src/speech.py     ← Microphone input + TTS
   src/config.py     ← JSON config loader
        │
   config/commands.json ← Intent patterns (extensible)
```

---

## Installation

**Requirements:** Python 3.8+, Ubuntu/Linux

```bash
# 1. Clone the repository
git clone https://github.com/Dagi0808/OIBSIP.git
cd OIBSIP/Python-Task1-VoiceAssistant

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install system dependencies (Ubuntu)
sudo apt update
sudo apt install portaudio19-dev python3-pyaudio libnotify-bin

# 4. Install Python dependencies
pip install -r requirements.txt

# 5. Set up environment variables
cp .env.example .env
# Edit .env and add your real API keys
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```env
OPENWEATHER_API_KEY=your_openweathermap_api_key_here
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password_here
ASSISTANT_LANG=en-US
```

| Variable | Description |
|---|---|
| `OPENWEATHER_API_KEY` | API key from [openweathermap.org](https://openweathermap.org/api) |
| `EMAIL_ADDRESS` | Your Gmail address (CLI mode only) |
| `EMAIL_PASSWORD` | Gmail App Password (not your login password) |
| `ASSISTANT_LANG` | Default speech language for CLI mode (e.g. `en-US`, `am-ET`) |

> **Never commit your real `.env` file.** It is excluded by `.gitignore`.

---

## Usage

**Option 1 — System tray app (recommended)**

```bash
source .venv/bin/activate
python tray.py
```

A tray icon appears. The browser opens automatically. Right-click the icon for the menu.

**Option 2 — Web UI only**

```bash
source .venv/bin/activate
python app.py
```

Open `http://127.0.0.1:5000`.

**Option 3 — CLI with microphone**

```bash
source .venv/bin/activate
python -m src.main
```

**Option 4 — Run tests**

```bash
source .venv/bin/activate
pytest tests/ -v
```

---

## Supported Commands

### English

| Command | Response |
|---|---|
| `hello` | Hello! How can I help you? |
| `what time is it` | The current time is 02:30 PM. |
| `what date is it` | The date is Sunday, August 23, 2026. |
| `what is the weather in Addis Ababa` | Live weather from OpenWeatherMap |
| `search for Python tutorials` | Google search info |
| `remind me in 5 minutes to drink water` | Reminder + desktop notification after 5 min |
| `check my email` | Gmail inbox summary (prompts for credentials) |
| `who is Albert Einstein` | Wikipedia summary |
| `what about Nairobi` | Follows up previous weather query |
| `open my notes` | Opening my notes. |

### አማርኛ (Amharic)

| ትዕዛዝ | ምላሽ |
|---|---|
| `ሰላም` | ሰላም! እንዴት ልረዳዎ? |
| `ሰዓቱ ስንት ነው` | አሁን ሰዓቱ 02:30 PM ነው። |
| `ቀኑ ስንት ነው` | ዛሬ እሁድ፣ ኦገስት 23፣ 2026 ነው። |
| `የአዲስ አበባ የአየር ሁኔታ` | በአዲስ አበባ የአየር ሁኔታ... |
| `ፈልግ Python` | Python ፍለጋ ጀምሯል። |
| `አስታውሰኝ ከ5 ደቂቃ ለውሃ ጠጣ` | ማስታወሻ ተቀናብሯል + የዴስክቶፕ ማሳወቂያ |
| `ማን ነው አልበርት አንስታይን` | Wikipedia ማጠቃለያ |

---

## Multi-language Support

Select the language from the dropdown in the header. The UI, chips, and placeholder text switch automatically. Speech recognition uses the selected language.

Supported languages: English (US/UK), አማርኛ (Amharic), Français, العربية, Español, Deutsch, 中文

---

## Screenshots

> Screenshots will be added to the `screenshots/` folder after the demo recording.

---

## Demo

> Demo video will be linked here after recording.

Demo sequence:
- `00:00–00:02` Title card
- `00:02–00:20` Greeting + speech recognition
- `00:20–00:35` Time and date
- `00:35–00:50` Web search
- `00:50–01:10` Weather
- `01:10–01:30` Reminder + desktop notification
- `01:30–01:50` Wikipedia knowledge
- `01:50–02:10` Email (Gmail IMAP)
- `02:10–02:30` Amharic commands

---

## Privacy Considerations

- All credentials (API keys, email address, password) are stored in a local `.env` file excluded from version control via `.gitignore`
- The `.env.example` file contains only placeholder values — no real credentials are committed
- Email credentials entered in the web UI are stored only in the Flask session (in-memory, cleared on tab close or new chat)
- The assistant does not store, log, or transmit voice input or personal data
- Gmail uses App Passwords (not your main account password), limiting credential scope
- OpenWeatherMap queries only send the city name — no personal data

---

## Project Structure

```
Python-Task1-VoiceAssistant/
├── app.py                  # Flask web UI entry point
├── tray.py                 # System tray entry point
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── config/
│   └── commands.json       # Intent patterns and command definitions
├── screenshots/
├── src/
│   ├── __init__.py
│   ├── main.py             # CLI + microphone entry point
│   ├── assistant.py        # Core response logic
│   ├── locales.py          # Language detection + localized intent/response (en + am)
│   ├── context.py          # Conversation context window / follow-up resolution
│   ├── intents.py          # Intent detection wrapper
│   ├── commands.py         # Time, date, search, reminder handlers
│   ├── weather.py          # OpenWeatherMap API
│   ├── email_service.py    # Gmail IMAP read + send
│   ├── reminders.py        # threading.Timer + notify-send desktop notification
│   ├── knowledge.py        # Wikipedia REST API
│   ├── speech.py           # Microphone input + TTS
│   └── config.py           # JSON config loader
└── tests/
    └── test_assistant.py
```

---

## Future Improvements

- Add OAuth2 Google Sign-In for email (no App Password needed)
- Add IMAP support for Outlook and Yahoo
- Expand Amharic support to Wikipedia Amharic edition
- Add more languages (French, Arabic full localization)
- Package as a standalone `.deb` installer
