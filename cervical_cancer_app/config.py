import os
from dotenv import load_dotenv
load_dotenv()
# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DB_PATH    = os.path.join(BASE_DIR, "cervical_cancer.db")
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")

# ── ML thresholds ─────────────────────────────────────────────────────────────
HIGH_RISK_THRESHOLD   = 0.22
MEDIUM_RISK_THRESHOLD = 0.08

# ── Features (must match training order) ─────────────────────────────────────
FEATURES = [
    "Age",
    "Number of sexual partners",
    "First sexual intercourse",
    "Num of pregnancies",
    "Smokes",
    "Smokes (years)",
    "Hormonal Contraceptives",
    "IUD",
    "STDs",
    "STDs (number)",
    "STDs:HPV",
]

# ── Flask secret key ─────────────────────────────────────────────────────────
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY env variable not set!")