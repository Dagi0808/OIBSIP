# Python Voice Assistant

**Dagmawit Dagne — OIBSIP Python Programming — Task 1 (Advanced)**

---

## Overview

A Python-based voice assistant that listens to spoken or typed commands and responds in natural language. It supports greeting, time/date queries, live weather lookup, web search, reminders, email integration, and custom commands. The project includes both a command-line interface with real microphone support and a Flask web UI with browser-based speech recognition.

---

## Features

- Voice input via microphone (SpeechRecognition + Google Speech API)
- Text-to-speech responses (pyttsx3)
- Current time and date reporting
- Live weather lookup using OpenWeatherMap API
- Web search (Google)
- Timed reminders
- Email inbox check and sending via Gmail SMTP
- Custom commands (open, launch, start, run)
- Flask web UI with quick-action chips and browser microphone support
- Extensible intent system driven by `config/commands.json`

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3 |
| Speech Input | SpeechRecognition, PyAudio |
| Speech Output | pyttsx3 |
| Web UI | Flask |
| Weather API | OpenWeatherMap |
| Email | smtplib (Gmail SMTP SSL) |
| Config | JSON |
| Environment | python-dotenv |
| Tests | pytest |

---

## Architecture

```
User (voice or text)
        │
        ▼
  app.py (Flask web UI)  ──or──  src/main.py (CLI + microphone)
        │
        ▼
  src/assistant.py  ←── get_response(text)
        │
   src/intents.py   ←── detect_intent() + extract_info()
        │
   src/commands.py  ←── time / date / search / reminder / weather
   src/weather.py   ←── OpenWeatherMap API
   src/email_service.py ←── Gmail SMTP
        │
   config/commands.json ←── intent patterns (extensible)
```

---

## Installation

**Requirements:** Python 3.8+, Ubuntu/Linux recommended

```bash
# 1. Clone the repository
git clone https://github.com/Dagi0808/OIBSIP.git
cd OIBSIP/Python-Task1-VoiceAssistant

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install system dependencies (Ubuntu — required for PyAudio)
sudo apt update
sudo apt install portaudio19-dev python3-pyaudio

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
```

| Variable | Description |
|---|---|
| `OPENWEATHER_API_KEY` | API key from [openweathermap.org](https://openweathermap.org/api) |
| `EMAIL_ADDRESS` | Your Gmail address |
| `EMAIL_PASSWORD` | A Gmail App Password (not your account password) |

> **Never commit your real `.env` file.** It is excluded by `.gitignore`.

---

## Usage

**Option 1 — Web UI (recommended for demo)**

```bash
source .venv/bin/activate
python app.py
```

Open `http://127.0.0.1:5000` in your browser. Type a command or click the 🎙️ Speak button.

**Option 2 — CLI with microphone**

```bash
source .venv/bin/activate
python -m src.main
```

Speak into your microphone when prompted.

**Option 3 — Run tests**

```bash
source .venv/bin/activate
pytest tests/ -v
```

---

## Supported Commands

| You say | Response |
|---|---|
| `hello` / `hi` / `hey` | Hello! How can I help you? |
| `what time is it` | The current time is 02:30 PM. |
| `what date is it` | The date is Sunday, August 23, 2026. |
| `what is the weather in Addis Ababa` | The weather in Addis Ababa is light rain with a temperature of 18°C. |
| `search for FastAPI tutorials` | Opens Google search in browser |
| `remind me in 5 minutes to check my email` | Reminder set for 5 minutes from now: check my email. |
| `check my email` | Checking inbox for your@email.com. |
| `open my notes` | Opening my notes. |

Custom commands can be added by editing `config/commands.json`.

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
- `01:10–01:30` Reminder
- `01:30–01:50` General knowledge
- `01:50–02:10` Email
- `02:10–02:30` Custom command

---

## Privacy Considerations

- All credentials (API keys, email address, password) are stored in a local `.env` file that is excluded from version control via `.gitignore`.
- The `.env.example` file contains only placeholder values — no real credentials are ever committed.
- The assistant does not store, log, or transmit any voice input or personal data.
- Email credentials use Gmail App Passwords, not your main account password, limiting exposure.
- OpenWeatherMap queries are made server-side and only send the city name — no personal data.

---

## Project Structure

```
Python-Task1-VoiceAssistant/
├── app.py                  # Flask web UI entry point
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── .gitignore
├── README.md
├── config/
│   └── commands.json       # Intent patterns and command definitions
├── screenshots/            # Demo screenshots
├── src/
│   ├── __init__.py
│   ├── main.py             # CLI + microphone entry point
│   ├── assistant.py        # Core response logic
│   ├── intents.py          # Intent detection and info extraction
│   ├── commands.py         # Time, date, search, reminder, weather handlers
│   ├── weather.py          # OpenWeatherMap API integration
│   ├── email_service.py    # Gmail SMTP check and send
│   ├── reminders.py        # Reminder message builder
│   ├── speech.py           # Microphone input and TTS output
│   └── config.py           # JSON config loader
└── tests/
    └── test_assistant.py   # pytest test suite
```

---

## Future Improvements

- Add a real countdown timer for reminders using `threading`
- Support multiple languages for speech recognition
- Add IMAP support to actually read emails
- Integrate a general knowledge API (Wikipedia or Wolfram Alpha)
- Add a conversation history/context window
- Package as a desktop app with a system tray icon
