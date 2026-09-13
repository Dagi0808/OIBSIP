"""Flask-SocketIO chat server."""

from __future__ import annotations

import os
from datetime import datetime
from functools import wraps

from flask import Flask, redirect, render_template, request, session, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room

from auth import check_password, hash_password, validate_password, validate_username
from emoji_utils import replace_emoji
from models import (
    create_room,
    create_user,
    get_all_rooms,
    get_room_by_name,
    get_room_history,
    get_user_by_id,
    get_user_by_username,
    init_db,
    save_message,
)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
socketio = SocketIO(app, cors_allowed_origins="*")

# Track online users per room: {room_name: {username, ...}}
_online: dict[str, set[str]] = {}


# ── Auth helpers ─────────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def current_user():
    uid = session.get("user_id")
    return get_user_by_id(uid) if uid else None


# ── HTTP routes ───────────────────────────────────────────────────────────────

@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return redirect(url_for("chat"))


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm  = request.form.get("confirm", "")

        error = validate_username(username) or validate_password(password)
        if not error and password != confirm:
            error = "Passwords do not match."
        if not error:
            uid = create_user(username, hash_password(password))
            if uid is None:
                error = "Username already taken."
            else:
                session["user_id"] = uid
                session["username"] = username
                return redirect(url_for("chat"))

    return render_template("register.html", error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = get_user_by_username(username)
        if user and check_password(password, user["password_hash"]):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("chat"))
        error = "Invalid username or password."

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/chat")
@login_required
def chat():
    rooms = get_all_rooms()
    username = session.get("username", "")
    return render_template("chat.html", rooms=rooms, username=username)


@app.route("/create-room", methods=["POST"])
@login_required
def create_room_route():
    name = request.form.get("room_name", "").strip()
    if name:
        create_room(name, session["user_id"])
    return redirect(url_for("chat"))


# ── SocketIO events ───────────────────────────────────────────────────────────

@socketio.on("join")
def on_join(data):
    room = data.get("room", "General")
    username = session.get("username", "Anonymous")

    join_room(room)
    _online.setdefault(room, set()).add(username)

    # Send message history
    room_row = get_room_by_name(room)
    if room_row:
        history = get_room_history(room_row["id"], limit=50)
        emit("history", {"messages": history, "room": room})

    # Notify room
    emit("status", {
        "msg": f"👋 {username} joined the room.",
        "room": room,
        "online": list(_online[room]),
    }, to=room)


@socketio.on("leave")
def on_leave(data):
    room = data.get("room", "General")
    username = session.get("username", "Anonymous")

    leave_room(room)
    if room in _online:
        _online[room].discard(username)

    emit("status", {
        "msg": f"👋 {username} left the room.",
        "room": room,
        "online": list(_online.get(room, set())),
    }, to=room)


@socketio.on("message")
def on_message(data):
    room    = data.get("room", "General")
    content = data.get("content", "").strip()
    username = session.get("username", "Anonymous")
    user_id  = session.get("user_id")

    if not content:
        return

    content = replace_emoji(content)
    room_row = get_room_by_name(room)
    ts = datetime.now().strftime("%H:%M")

    if room_row and user_id:
        ts = save_message(room_row["id"], user_id, content)

    emit("message", {
        "username": username,
        "content":  content,
        "timestamp": ts,
        "room":     room,
    }, to=room)


@socketio.on("disconnect")
def on_disconnect():
    username = session.get("username", "")
    for room, users in _online.items():
        if username in users:
            users.discard(username)
            emit("status", {
                "msg": f"⚡ {username} disconnected.",
                "room": room,
                "online": list(users),
            }, to=room)


if __name__ == "__main__":
    init_db()
    socketio.run(app, host="127.0.0.1", port=5001, debug=True)
