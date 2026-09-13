# Python Chat Application

**Dagmawit Dagne — OIBSIP Python Programming — Task 5 (Advanced)**

---

## Overview

A real-time web-based chat application built with Flask-SocketIO and SQLite. Users can register, log in, join multiple chat rooms, send messages with emoji support, and receive desktop notifications for new messages.

---

## Features

- User registration and login with bcrypt password hashing
- Multiple chat rooms — join existing rooms or create new ones
- Real-time bidirectional messaging via WebSockets (Flask-SocketIO)
- Message history — last 50 messages loaded when joining a room
- Timestamps on all messages (`[14:35] Alice: Hello`)
- Emoji shortcode support (`:smile:` → 😊, `:fire:` → 🔥, etc.)
- Desktop notifications for new messages when the window is not focused
- Online user count displayed per room
- Graceful disconnect handling — notifies the room when a user leaves
- Discord-style dark UI with sidebar room list and online users panel
- Runs on localhost — no external services required

---

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.8+ |
| Web framework | Flask |
| Real-time | Flask-SocketIO (WebSockets) |
| Database | SQLite (sqlite3) |
| Auth | bcrypt password hashing |
| Frontend | HTML, CSS, JavaScript |
| SocketIO client | socket.io v4 (CDN) |
| Tests | pytest |

---

## Installation

```bash
# 1. Navigate to the project folder
cd OIBSIP/Python-Task5-ChatApplication

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env — set a strong SECRET_KEY
```

---

## Environment Variables

```env
SECRET_KEY=change-this-to-a-random-secret-key
```

> Never commit your real `.env` file. It is excluded by `.gitignore`.

---

## Usage

```bash
source .venv/bin/activate
python server.py
```

Open `http://127.0.0.1:5001` in your browser.

To test multi-user chat, open the same URL in two different browser windows or use an incognito window.

---

## Supported Emoji Shortcodes

| Shortcode | Emoji |
|---|---|
| `:smile:` | 😊 |
| `:heart:` | ❤️ |
| `:fire:` | 🔥 |
| `:thumbsup:` | 👍 |
| `:rocket:` | 🚀 |
| `:laugh:` | 😄 |
| `:wave:` | 👋 |
| `:clap:` | 👏 |
| `:100:` | 💯 |
| `:tada:` | 🎊 |

See `emoji_utils.py` for the full list of 40+ supported shortcodes.

---

## Project Structure

```
Python-Task5-ChatApplication/
├── server.py           # Flask-SocketIO server, routes, socket events
├── models.py           # SQLite database — users, rooms, messages
├── auth.py             # Password hashing and input validation
├── emoji_utils.py      # Emoji shortcode → Unicode conversion
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   └── chat.html       # Main chat window
├── static/
│   └── chat.js         # SocketIO client, room management, notifications
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── tests/
    └── test_models.py
```

---

## Screenshots

> Screenshots will be added after the demo recording.

---

## Security Transparency

This section is required by the Oasis task specification.

### What is protected
- Passwords are hashed using **bcrypt** before storage — plain text passwords are never saved to the database.
- Session tokens are stored in signed, server-side Flask session cookies.

### What is NOT encrypted
- **Messages are stored in plain text** in the SQLite database (`chat.db`). Anyone with file system access to the server can read all messages.
- **Network traffic is not encrypted** in development (HTTP, not HTTPS). In a production deployment, TLS (HTTPS) would be required to prevent message interception.
- There is **no end-to-end encryption** — the server can read all messages as they pass through.

### Recommendations for production
- Deploy behind HTTPS with a valid TLS certificate
- Encrypt the SQLite database or migrate to a production database with access controls
- Implement message encryption at the application layer if privacy is required

---

## Future Improvements

- Direct (private) messaging between users
- File and image sharing
- Message editing and deletion
- Read receipts
- User profile pictures
- HTTPS support for production deployment
- Rate limiting to prevent spam
