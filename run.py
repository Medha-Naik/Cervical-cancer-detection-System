"""Start the web app:  python run.py"""
import os

from cervixguard import create_app
from cervixguard.services.reminders import start_reminder_scheduler

app = create_app()

if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "true").lower() != "false"
    app.debug = debug_mode
    start_reminder_scheduler(app)
    app.run(debug=debug_mode)
