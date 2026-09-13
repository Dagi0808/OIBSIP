# OIBSIP — Python Programming Internship

**Dagmawit Dagne**  
Oasis Infobyte Software Programming Internship  
Python Programming Track

---

## Repository Structure

This repository contains all task submissions for the internship.
Each task lives in its own folder and development branch.

```
OIBSIP/
├── Python-Task1-VoiceAssistant/    ← Task 1 · Advanced Voice Assistant
├── Python-Task4-WeatherApp/        ← Task 4 · Advanced Weather App
└── Python-Task5-ChatApplication/   ← Task 5 · Advanced Chat Application
```

| Branch | Task |
|---|---|
| `task1-voice-assistant` | Task 1 — Voice Assistant |
| `task4-weather-app` | Task 4 — Weather App |
| `task5-chat-app` | Task 5 — Chat Application |
| `main` | All tasks merged |

---

## Task 1 · Advanced Voice Assistant

**Folder:** `Python-Task1-VoiceAssistant/`

A Python voice assistant with a Flask web UI and CLI microphone mode. Supports English and Amharic (አማርኛ) with full localization.

### Highlights
- 🎙️ Voice input via microphone + browser speech recognition
- 🔊 Text-to-speech responses
- 🌤️ Live weather from OpenWeatherMap API
- 🧠 Wikipedia general knowledge lookup
- ⏰ Timed reminders with desktop notifications
- 📧 Gmail IMAP inbox reading (per-user, session-only credentials)
- 🌍 Multi-language support — English, አማርኛ, French, Arabic, Spanish, German, Chinese
- 💬 Conversation context window — resolves follow-up references
- 🤖 System tray desktop app (`tray.py`)
- 🌙 Dark / ☀️ Light theme toggle

### Tech Stack
`Python` · `Flask` · `Flask-SocketIO` · `SpeechRecognition` · `pyttsx3` · `pystray` · `Pillow` · `requests` · `SQLite` · `python-dotenv`

### Run
```bash
cd Python-Task1-VoiceAssistant
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your OpenWeatherMap API key
python app.py          # web UI at http://127.0.0.1:5000
# or
python tray.py         # system tray + auto-browser
```

---

## Task 4 · Advanced Weather App

**Folder:** `Python-Task4-WeatherApp/`

A Python desktop weather application built with tkinter. Fetches real-time weather and forecasts from OpenWeatherMap and auto-detects your city from your IP.

### Highlights
- 📍 Auto-detects your city on startup via ipinfo.io
- 🌡️ Current weather: temperature, feels like, humidity, wind, visibility, sunrise/sunset
- 🖼️ Weather icons from OpenWeatherMap
- 🕐 Hourly forecast: next 6 hours
- 📅 5-day daily forecast with high/low temperatures
- 🔄 Celsius / Fahrenheit toggle
- 🌙 Dark / ☀️ Light theme toggle
- ⚠️ Full error handling: empty input, city not found, timeout, invalid key

### Tech Stack
`Python` · `tkinter` · `Pillow` · `requests` · `python-dotenv`

### Run
```bash
cd Python-Task4-WeatherApp
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your OpenWeatherMap API key
python main.py
```

---

## Task 5 · Advanced Chat Application

**Folder:** `Python-Task5-ChatApplication/`

A real-time web chat application with Discord-inspired UI. Built with Flask-SocketIO and SQLite, supporting multiple rooms, authentication, message history, and emoji.

### Highlights
- 👤 User registration and login (bcrypt password hashing)
- 💬 Multiple chat rooms — join or create channels
- ⚡ Real-time bidirectional messaging via WebSockets
- 📜 Message history — last 50 messages loaded when joining a room
- 😊 Emoji shortcodes: `:smile:` → 😊, `:fire:` → 🔥, `:rocket:` → 🚀
- 🔔 Desktop notifications for new messages (browser Notification API)
- 👥 Online user list with colored avatars per room
- ⏱️ Timestamps on all messages
- 🔌 Graceful disconnect — notifies the room when a user leaves
- 🔒 Security transparency documented in README

### Tech Stack
`Python` · `Flask` · `Flask-SocketIO` · `SQLite` · `bcrypt` · `HTML/CSS/JS`

### Run
```bash
cd Python-Task5-ChatApplication
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # set SECRET_KEY
python server.py       # http://127.0.0.1:5001
```

To test real-time chat, open the URL in two different browser windows and register two different users.

---

## Privacy & Security

All tasks follow secure coding practices:
- API keys and credentials stored in `.env` files, excluded from version control via `.gitignore`
- No real credentials are committed to this repository
- Each task folder contains a `.env.example` with placeholder values only
- Task 5 README documents message storage and encryption transparency

---

## Author

**Dagmawit Dagne**  
OIBSIP Python Programming Internship  
[GitHub: Dagi0808](https://github.com/Dagi0808)
