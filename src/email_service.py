"""Email-related helpers for the voice assistant."""

from __future__ import annotations

import email
import imaplib
import os
import smtplib
from email.header import decode_header
from email.message import EmailMessage

from dotenv import load_dotenv

load_dotenv()

IMAP_HOST = "imap.gmail.com"
IMAP_PORT = 993


def read_inbox(email_address: str, app_password: str, max_subjects: int = 3) -> str:
    """Connect to Gmail via IMAP and return unread email summary."""
    if not email_address or not app_password:
        return "EMAIL_SETUP_NEEDED"

    try:
        mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        mail.login(email_address.strip(), app_password.strip())
        mail.select("INBOX")

        # Count unread
        _, unread_data = mail.search(None, "UNSEEN")
        unread_ids = unread_data[0].split() if unread_data[0] else []
        unread_count = len(unread_ids)

        subjects = []
        # Fetch subjects of the most recent unread emails
        for uid in reversed(unread_ids[-max_subjects:]):
            _, msg_data = mail.fetch(uid, "(RFC822.HEADER)")
            for part in msg_data:
                if isinstance(part, tuple):
                    msg = email.message_from_bytes(part[1])
                    raw_subject = msg.get("Subject", "(no subject)")
                    decoded, enc = decode_header(raw_subject)[0]
                    if isinstance(decoded, bytes):
                        subject = decoded.decode(enc or "utf-8", errors="replace")
                    else:
                        subject = decoded
                    subjects.append(subject.strip())

        mail.logout()

        if unread_count == 0:
            return "Your inbox is all caught up — no unread emails! 🎉"

        subject_list = ", ".join(f'"{s}"' for s in subjects) if subjects else ""
        if subject_list:
            return (
                f"You have {unread_count} unread email{'s' if unread_count != 1 else ''}. "
                f"Latest: {subject_list}."
            )
        return f"You have {unread_count} unread email{'s' if unread_count != 1 else ''}."

    except imaplib.IMAP4.error:
        return "EMAIL_AUTH_FAILED"
    except (OSError, TimeoutError):
        return "EMAIL_CONNECT_FAILED"


def check_email() -> str:
    """Fallback for CLI mode using .env credentials."""
    email_address = os.getenv("EMAIL_ADDRESS")
    app_password = os.getenv("EMAIL_PASSWORD")

    if not email_address or not app_password:
        return "EMAIL_SETUP_NEEDED"

    return read_inbox(email_address, app_password)


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
