"""Outgoing email (vaccine dose reminders)."""
import smtplib
from email.mime.text import MIMEText

from .. import config


def send_email(to_addr, subject, body):
    """Send a plain-text email. Falls back to logging to the console if SMTP
    isn't configured, so the app works out of the box without mail setup."""
    if not to_addr:
        return False
    if not config.SMTP_HOST:
        print(f"[reminder email — SMTP not configured, printing instead]\nTo: {to_addr}\nSubject: {subject}\n{body}\n")
        return True
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = config.MAIL_FROM
    msg["To"] = to_addr
    try:
        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=15) as server:
            if config.SMTP_USE_TLS:
                server.starttls()
            if config.SMTP_USERNAME and config.SMTP_PASSWORD:
                server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
            server.sendmail(config.MAIL_FROM, [to_addr], msg.as_string())
        return True
    except Exception as e:
        print(f"Failed to send reminder email to {to_addr}: {e}")
        return False
