"""SQLite database models for the chat application."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "chat.db"


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """Create all tables and seed default rooms."""
    with get_db() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                username      TEXT    UNIQUE NOT NULL,
                password_hash TEXT    NOT NULL,
                created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS rooms (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT    UNIQUE NOT NULL,
                created_by INTEGER REFERENCES users(id),
                created_at TEXT    NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS messages (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                room_id    INTEGER NOT NULL REFERENCES rooms(id),
                user_id    INTEGER NOT NULL REFERENCES users(id),
                content    TEXT    NOT NULL,
                timestamp  TEXT    NOT NULL DEFAULT (datetime('now'))
            );
        """)
        # Seed default rooms
        for room in ("General", "Random", "Tech"):
            db.execute(
                "INSERT OR IGNORE INTO rooms (name) VALUES (?)", (room,)
            )


# ── User operations ──────────────────────────────────────────────────────────

def create_user(username: str, password_hash: str) -> int | None:
    """Insert a new user. Returns the new user id or None if username taken."""
    try:
        with get_db() as db:
            cur = db.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash),
            )
            return cur.lastrowid
    except sqlite3.IntegrityError:
        return None


def get_user_by_username(username: str) -> sqlite3.Row | None:
    with get_db() as db:
        return db.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()


def get_user_by_id(user_id: int) -> sqlite3.Row | None:
    with get_db() as db:
        return db.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()


# ── Room operations ──────────────────────────────────────────────────────────

def get_all_rooms() -> list[sqlite3.Row]:
    with get_db() as db:
        return db.execute(
            "SELECT * FROM rooms ORDER BY name"
        ).fetchall()


def get_room_by_name(name: str) -> sqlite3.Row | None:
    with get_db() as db:
        return db.execute(
            "SELECT * FROM rooms WHERE name = ?", (name,)
        ).fetchone()


def create_room(name: str, created_by: int) -> int | None:
    """Create a room. Returns room id or None if name taken."""
    try:
        with get_db() as db:
            cur = db.execute(
                "INSERT INTO rooms (name, created_by) VALUES (?, ?)",
                (name, created_by),
            )
            return cur.lastrowid
    except sqlite3.IntegrityError:
        return None


# ── Message operations ────────────────────────────────────────────────────────

def save_message(room_id: int, user_id: int, content: str) -> str:
    """Save a message and return its timestamp string."""
    ts = datetime.now().strftime("%H:%M")
    with get_db() as db:
        db.execute(
            "INSERT INTO messages (room_id, user_id, content, timestamp) "
            "VALUES (?, ?, ?, ?)",
            (room_id, user_id, content, ts),
        )
    return ts


def get_room_history(room_id: int, limit: int = 50) -> list[dict]:
    """Return the last `limit` messages for a room, oldest first."""
    with get_db() as db:
        rows = db.execute(
            """
            SELECT m.content, m.timestamp, u.username
            FROM messages m
            JOIN users u ON u.id = m.user_id
            WHERE m.room_id = ?
            ORDER BY m.id DESC
            LIMIT ?
            """,
            (room_id, limit),
        ).fetchall()
    return [
        {"username": r["username"], "content": r["content"], "timestamp": r["timestamp"]}
        for r in reversed(rows)
    ]
