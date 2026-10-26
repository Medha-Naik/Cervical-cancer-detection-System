import sqlite3
from datetime import datetime
from config import DB_PATH


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT    NOT NULL UNIQUE,
            email         TEXT    NOT NULL UNIQUE,
            password_hash TEXT    NOT NULL,
            created_at    TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS vaccine_doses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL REFERENCES users(id),
            dose_number INTEGER NOT NULL,
            dose_date   TEXT    NOT NULL,
            notes       TEXT,
            recorded_at TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id                      INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id                 INTEGER NOT NULL REFERENCES users(id),
            patient_name            TEXT    NOT NULL,
            age                     REAL,
            sexual_partners         REAL,
            first_intercourse       REAL,
            pregnancies             REAL,
            smokes                  REAL,
            smokes_years            REAL,
            hormonal_contraceptives REAL,
            iud                     REAL,
            stds                    REAL,
            stds_number             REAL,
            stds_hpv                REAL,
            prediction              TEXT,
            confidence              TEXT,
            timestamp               TEXT
        )
    """)

    conn.commit()
    conn.close()
    print(f"[DB] Ready: {DB_PATH}")


# ── User helpers ──────────────────────────────────────────────────────────────

def create_user(username: str, email: str, password_hash: str):
    conn = get_db()
    conn.execute("""
        INSERT INTO users (username, email, password_hash, created_at)
        VALUES (?, ?, ?, ?)
    """, (username, email, password_hash, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()


def get_user_by_email(email: str):
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(user_id: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ── Prediction helpers ────────────────────────────────────────────────────────

def save_prediction(user_id: int, patient_name: str, input_data: dict, prediction: str, confidence: str):
    conn = get_db()
    conn.execute("""
        INSERT INTO predictions (
            user_id, patient_name, age, sexual_partners, first_intercourse,
            pregnancies, smokes, smokes_years, hormonal_contraceptives,
            iud, stds, stds_number, stds_hpv,
            prediction, confidence, timestamp
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        user_id,
        patient_name,
        input_data.get("Age", 0),
        input_data.get("Number of sexual partners", 0),
        input_data.get("First sexual intercourse", 0),
        input_data.get("Num of pregnancies", 0),
        input_data.get("Smokes", 0),
        input_data.get("Smokes (years)", 0),
        input_data.get("Hormonal Contraceptives", 0),
        input_data.get("IUD", 0),
        input_data.get("STDs", 0),
        input_data.get("STDs (number)", 0),
        input_data.get("STDs:HPV", 0),
        prediction,
        confidence,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    ))
    conn.commit()
    conn.close()


def delete_prediction(record_id: int, user_id: int):
    """Only deletes if the record belongs to this user."""
    conn = get_db()
    conn.execute(
        "DELETE FROM predictions WHERE id = ? AND user_id = ?",
        (record_id, user_id)
    )
    conn.commit()
    conn.close()


def get_all_predictions(user_id: int) -> list[dict]:
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM predictions WHERE user_id = ? ORDER BY id DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_risk_counts(user_id: int) -> dict:
    conn = get_db()
    rows = conn.execute(
        "SELECT prediction, COUNT(*) FROM predictions WHERE user_id = ? GROUP BY prediction",
        (user_id,)
    ).fetchall()
    conn.close()
    counts = {"Low Risk": 0, "Medium Risk": 0, "High Risk": 0}
    for pred, cnt in rows:
        if pred in counts:
            counts[pred] = cnt
    return counts


# ── Vaccine helpers 

def save_vaccine_dose(user_id: int, dose_number: int, dose_date: str, notes: str = ""):
    conn = get_db()
    existing = conn.execute(
        "SELECT id FROM vaccine_doses WHERE user_id = ? AND dose_number = ?",
        (user_id, dose_number)
    ).fetchone()
    if existing:
        conn.execute(
            "UPDATE vaccine_doses SET dose_date = ?, notes = ? WHERE user_id = ? AND dose_number = ?",
            (dose_date, notes, user_id, dose_number)
        )
    else:
        conn.execute("""
            INSERT INTO vaccine_doses (user_id, dose_number, dose_date, notes, recorded_at)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, dose_number, dose_date, notes,
              datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()


def get_vaccine_doses(user_id: int) -> list[dict]:
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM vaccine_doses WHERE user_id = ? ORDER BY dose_number",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]