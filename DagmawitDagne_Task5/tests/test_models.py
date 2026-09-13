"""Tests for models, auth, and emoji utilities."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import tempfile
from pathlib import Path

# ── Auth tests ────────────────────────────────────────────────────────────────
from auth import (
    hash_password, check_password,
    validate_username, validate_password,
)

def test_password_hash_and_check():
    h = hash_password("secret123")
    assert check_password("secret123", h)
    assert not check_password("wrong", h)

def test_validate_username_ok():
    assert validate_username("dagmawit") is None
    assert validate_username("user_01") is None

def test_validate_username_too_short():
    assert validate_username("ab") is not None

def test_validate_username_empty():
    assert validate_username("") is not None

def test_validate_username_too_long():
    assert validate_username("a" * 21) is not None

def test_validate_password_ok():
    assert validate_password("pass12") is None

def test_validate_password_too_short():
    assert validate_password("abc") is not None

def test_validate_password_empty():
    assert validate_password("") is not None


# ── Emoji tests ───────────────────────────────────────────────────────────────
from emoji_utils import replace_emoji

def test_replace_smile():
    assert replace_emoji("Hello :smile:") == "Hello 😊"

def test_replace_multiple():
    assert replace_emoji(":heart: :fire:") == "❤️ 🔥"

def test_no_replacement():
    assert replace_emoji("Hello world") == "Hello world"

def test_unknown_shortcode():
    assert replace_emoji(":unknown:") == ":unknown:"


# ── Models tests (using temp DB) ──────────────────────────────────────────────
import models as _models

@pytest.fixture
def tmp_db(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr(_models, "DB_PATH", db_path)
    _models.init_db()
    return db_path

def test_create_and_get_user(tmp_db):
    uid = _models.create_user("alice", hash_password("pass123"))
    assert uid is not None
    user = _models.get_user_by_username("alice")
    assert user["username"] == "alice"

def test_duplicate_user_returns_none(tmp_db):
    _models.create_user("bob", hash_password("pass"))
    uid2 = _models.create_user("bob", hash_password("pass"))
    assert uid2 is None

def test_default_rooms_created(tmp_db):
    rooms = _models.get_all_rooms()
    names = [r["name"] for r in rooms]
    assert "General" in names
    assert "Random" in names

def test_create_and_get_room(tmp_db):
    uid = _models.create_user("carol", hash_password("pass"))
    rid = _models.create_room("MyRoom", uid)
    assert rid is not None
    room = _models.get_room_by_name("MyRoom")
    assert room["name"] == "MyRoom"

def test_save_and_get_message(tmp_db):
    uid = _models.create_user("dave", hash_password("pass"))
    room = _models.get_room_by_name("General")
    ts = _models.save_message(room["id"], uid, "Hello!")
    assert ts is not None
    history = _models.get_room_history(room["id"])
    assert len(history) == 1
    assert history[0]["content"] == "Hello!"
    assert history[0]["username"] == "dave"

def test_message_history_limit(tmp_db):
    uid = _models.create_user("eve", hash_password("pass"))
    room = _models.get_room_by_name("General")
    for i in range(10):
        _models.save_message(room["id"], uid, f"msg {i}")
    history = _models.get_room_history(room["id"], limit=5)
    assert len(history) == 5
