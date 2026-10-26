"""Central configuration: file paths, environment variables and app-wide constants.

Every other module imports from here, so nothing reads os.environ or hardcodes a
path on its own.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")  # optional; real environment variables win over .env
except ImportError:
    pass  # python-dotenv not installed - env vars can still be set the normal way

# ── Paths ──
DB_PATH = os.environ.get("DB_PATH", str(BASE_DIR / "cervical_cancer.db"))
MODEL_PATH = os.environ.get("MODEL_PATH", str(BASE_DIR / "model.pkl"))
DATASET_PATH = str(BASE_DIR / "kag_risk_factors_cervical_cancer.csv")

SECRET_KEY = os.environ.get("SECRET_KEY", "cervixguard-dev-secret-change-me")

# ── Email (vaccine dose reminders) ──
# If SMTP_HOST is unset, reminder emails are printed to the console instead of sent.
SMTP_HOST = os.environ.get("SMTP_HOST")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USERNAME = os.environ.get("SMTP_USERNAME")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
SMTP_USE_TLS = os.environ.get("SMTP_USE_TLS", "true").lower() != "false"
MAIL_FROM = os.environ.get("MAIL_FROM", SMTP_USERNAME or "no-reply@cervixguard.local")
REMINDER_CHECK_INTERVAL_SECONDS = int(
    os.environ.get("REMINDER_CHECK_INTERVAL_SECONDS", str(24 * 60 * 60))
)

# ── Symptoms (advisory only - not model inputs) ──
SYMPTOM_LABELS = {
    "symptom_bleeding": "Abnormal bleeding",
    "symptom_postcoital": "Post-intercourse bleeding",
    "symptom_discharge": "Unusual discharge",
    "symptom_pelvic_pain": "Pelvic pain",
    "symptom_pain_intercourse": "Pain during intercourse",
}
SYMPTOM_FIELDS = list(SYMPTOM_LABELS)

# ── Risk tiers ──
# (label, bootstrap class, minimum probability), checked top to bottom.
RISK_TIERS = [
    ("High Risk", "danger", 0.22),
    ("Medium Risk", "warning", 0.08),
    ("Low Risk", "success", 0.0),
]
RISK_LABELS = [label for label, _, _ in RISK_TIERS]

FOLLOWUP_DAYS = {"High Risk": 7, "Medium Risk": 30, "Low Risk": 365}
DEFAULT_FOLLOWUP_DAYS = 180
