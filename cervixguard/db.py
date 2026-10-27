"""SQLite access: connection helper and the one and only schema definition.

The schema used to be written twice (init_db() in app.py and setup_db.py), each with
its own copy of the migration code. Both now call init_db() below.
"""
import sqlite3
from contextlib import contextmanager

from . import config
from .ml.features import FEATURE_COLUMNS

# Column name -> SQL definition. Order matters: it is the column order of a fresh database.
# Columns that were added in later versions are listed last so init_db() can add them to
# an old database with ALTER TABLE.
SCHEMA = {
    "users": {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "username": "TEXT UNIQUE NOT NULL",
        "password_hash": "TEXT NOT NULL",
        "email": "TEXT",
        "created_at": "TEXT",
        # Added later - init_db() adds these to an existing database automatically.
        # Age is never stored: it is worked out from birth_year, so it can't go out of date.
        "full_name": "TEXT",
        "birth_year": "INTEGER",
    },
    "predictions": {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "patient_name": "TEXT",
        **{column: "REAL" for _, column in FEATURE_COLUMNS},
        "prediction": "TEXT",
        "confidence": "TEXT",
        "timestamp": "TEXT",
        **{field: "INTEGER DEFAULT 0" for field in config.SYMPTOM_FIELDS},
        "urgent_flag": "INTEGER DEFAULT 0",
        "user_id": "INTEGER DEFAULT 0",
    },
    "vaccine_registrations": {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "user_id": "INTEGER",
        "patient_name": "TEXT",
        "age": "REAL",
        "doses_required": "INTEGER",
        "dose1_date": "TEXT",
        "dose2_date": "TEXT",
        "dose3_date": "TEXT",
        "dose1_done": "INTEGER DEFAULT 0",
        "dose2_done": "INTEGER DEFAULT 0",
        "dose3_done": "INTEGER DEFAULT 0",
        "dose1_reminder_sent": "INTEGER DEFAULT 0",
        "dose2_reminder_sent": "INTEGER DEFAULT 0",
        "dose3_reminder_sent": "INTEGER DEFAULT 0",
        "created_at": "TEXT",
        # Added later - init_db() adds this to an existing database automatically.
        "immunocompromised": "INTEGER DEFAULT 0",
    },
}


def get_conn():
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def connection():
    """Open a connection, commit if the block succeeds, always close it.

    Replaces the get_conn() / commit() / close() boilerplate that was repeated in
    every route and helper.
    """
    conn = get_conn()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """Create any missing tables and add any columns that predate this version."""
    with connection() as conn:
        for table, columns in SCHEMA.items():
            column_defs = ", ".join(f"{name} {definition}" for name, definition in columns.items())
            conn.execute(f"CREATE TABLE IF NOT EXISTS {table} ({column_defs})")

            existing = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}
            for name, definition in columns.items():
                if name not in existing:
                    conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {definition}")

        # One-off carry-over from the short-lived "stored age" version: work out a birth
        # year from the old age so those users don't have to enter anything again.
        user_cols = {row["name"] for row in conn.execute("PRAGMA table_info(users)")}
        if {"age", "age_updated_on"} <= user_cols:
            conn.execute(
                "UPDATE users SET birth_year = CAST(substr(age_updated_on, 1, 4) AS INTEGER) - age "
                "WHERE birth_year IS NULL AND age IS NOT NULL AND age_updated_on IS NOT NULL"
            )