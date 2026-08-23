"""Email-related helpers for the voice assistant."""

from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv

load_dotenv()


def check_email() -> str:
    """Return a status message for the configured inbox."""
    email_address = os.getenv("EMAIL_ADDRESS")
    if not email_address:
        return "Email checking is not configured yet. Add EMAIL_ADDRESS to your .env file."
    return f"Checking inbox for {email_address}."


def send_email(recipient: str, subject: str, body: str) -> str:
    """Send an email using SMTP if credentials are configured."""
    sender = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")

    if not sender or not password:
        return (
            "Email sending is not configured. Add EMAIL_ADDRESS and EMAIL_PASSWORD "
            "to your .env file."
        )

    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.send_message(msg)
        return f"Email sent to {recipient} with subject '{subject}'."
    except (OSError, smtplib.SMTPException):
        return f"I couldn't send the email to {recipient} right now."
