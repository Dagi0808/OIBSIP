"""Authentication helpers — password hashing and verification."""

from __future__ import annotations

import bcrypt


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def validate_username(username: str) -> str | None:
    """Return an error message or None if valid."""
    username = username.strip()
    if not username:
        return "Username cannot be empty."
    if len(username) < 3:
        return "Username must be at least 3 characters."
    if len(username) > 20:
        return "Username cannot exceed 20 characters."
    if not username.replace("_", "").replace("-", "").isalnum():
        return "Username can only contain letters, numbers, - and _."
    return None


def validate_password(password: str) -> str | None:
    """Return an error message or None if valid."""
    if not password:
        return "Password cannot be empty."
    if len(password) < 6:
        return "Password must be at least 6 characters."
    return None
