"""Background job that emails users when an HPV vaccine dose becomes due."""
import os
import threading
import time
from datetime import datetime

from .. import config
from ..db import connection
from .mailer import send_email
from .vaccine import DOSE_NUMBERS


def check_and_send_vaccine_reminders():
    """Find HPV vaccine doses whose due date has arrived (today or earlier),
    aren't marked done yet, and haven't already had a reminder sent — email
    the account holder for each, then mark it sent so it isn't repeated."""
    today = datetime.now().strftime("%Y-%m-%d")
    sent_count = 0
    with connection() as conn:
        regs = [dict(r) for r in conn.execute("""
            SELECT v.*, u.email AS user_email
            FROM vaccine_registrations v
            JOIN users u ON u.id = v.user_id
            WHERE u.email IS NOT NULL AND u.email != ''
        """)]

        for reg in regs:
            for dose_num in DOSE_NUMBERS[:reg["doses_required"]]:
                dose_date = reg.get(f"dose{dose_num}_date")
                sent_field = f"dose{dose_num}_reminder_sent"
                if not dose_date or reg.get(f"dose{dose_num}_done") or reg.get(sent_field):
                    continue
                if dose_date > today:
                    continue  # not due yet

                subject = f"CervixGuard AI — HPV vaccine dose {dose_num} is due"
                body = (
                    f"Hi,\n\nThis is a reminder that HPV vaccine dose {dose_num} for "
                    f"{reg['patient_name']} was due on {dose_date}.\n\n"
                    "Please book it with your clinic soon if it hasn't been given yet. "
                    "You can mark it as done from the Vaccine page once it's administered.\n\n"
                    "— CervixGuard AI (educational tool, not a diagnosis)"
                )
                if send_email(reg["user_email"], subject, body):
                    conn.execute(
                        f"UPDATE vaccine_registrations SET {sent_field} = 1 WHERE id = ?", (reg["id"],)
                    )
                    sent_count += 1

    if sent_count:
        print(f"Sent {sent_count} vaccine dose reminder email(s).")
    return sent_count


def _reminder_loop():
    while True:
        try:
            check_and_send_vaccine_reminders()
        except Exception as e:
            print(f"Vaccine reminder check failed: {e}")
        time.sleep(config.REMINDER_CHECK_INTERVAL_SECONDS)


def start_reminder_scheduler(app):
    # Avoid double-starting the background thread under the Flask debug reloader,
    # which re-executes this module in a child process with WERKZEUG_RUN_MAIN=true.
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or not app.debug:
        threading.Thread(target=_reminder_loop, daemon=True).start()
