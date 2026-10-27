"""Reading and writing saved risk assessments.

The feature -> column mapping lives in ml/features.py; it used to be spelled out
three times (saving, listing, and rebuilding the PDF input).
"""
from datetime import datetime

from .. import config
from ..db import connection
from ..ml.features import FEATURE_COLUMNS

_FEATURE_COLS = [column for _, column in FEATURE_COLUMNS]
_HISTORY_KEYS = ["id", "patient_name", *_FEATURE_COLS, "prediction", "confidence", "timestamp"]


def save_prediction(user_id, patient_name, input_data, symptoms, urgent_flag, prediction, confidence):
    """Insert one assessment and return its new id."""
    columns = (
        ["patient_name", *_FEATURE_COLS, "prediction", "confidence", "timestamp",
         *config.SYMPTOM_FIELDS, "urgent_flag", "user_id"]
    )
    values = (
        [patient_name]
        + [input_data.get(feature, 0) for feature, _ in FEATURE_COLUMNS]
        + [prediction, confidence, datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        + [symptoms.get(field, 0) for field in config.SYMPTOM_FIELDS]
        + [int(urgent_flag), user_id]
    )
    placeholders = ",".join("?" * len(columns))
    with connection() as conn:
        cur = conn.execute(
            f"INSERT INTO predictions ({', '.join(columns)}) VALUES ({placeholders})", values
        )
        return cur.lastrowid


def get_record(record_id, user_id):
    with connection() as conn:
        row = conn.execute(
            "SELECT * FROM predictions WHERE id = ? AND user_id = ?", (record_id, user_id)
        ).fetchone()
    return dict(row) if row else None


def get_all_predictions(user_id):
    with connection() as conn:
        rows = [dict(r) for r in conn.execute(
            "SELECT * FROM predictions WHERE user_id = ? ORDER BY id DESC", (user_id,)
        )]
    return [
        {**{key: r[key] for key in _HISTORY_KEYS}, "urgent_flag": r.get("urgent_flag", 0)}
        for r in rows
    ]


def get_risk_counts(user_id):
    counts = {label: 0 for label in config.RISK_LABELS}
    with connection() as conn:
        rows = conn.execute(
            "SELECT prediction, COUNT(*) FROM predictions WHERE user_id = ? GROUP BY prediction",
            (user_id,),
        ).fetchall()
    for prediction, count in rows:
        if prediction in counts:
            counts[prediction] = count
    return counts


def delete_prediction(record_id, user_id):
    """Delete one of the user's assessments. Returns True if a row was removed."""
    with connection() as conn:
        return conn.execute(
            "DELETE FROM predictions WHERE id = ? AND user_id = ?", (record_id, user_id)
        ).rowcount > 0


def cumulative_trend(history):
    """[{date, value}] - running total of assessments per day, for the dashboard line chart."""
    per_day = {}
    for record in sorted(history, key=lambda r: r["timestamp"]):
        day = record["timestamp"][:10]
        per_day[day] = per_day.get(day, 0) + 1
    running = 0
    points = []
    for day in sorted(per_day):
        running += per_day[day]
        points.append({"date": day, "value": running})
    return points


def record_to_input_data(record):
    """Rebuild the {feature name: value} dict from a saved row (used for the PDF report)."""
    return {feature: record[column] for feature, column in FEATURE_COLUMNS}


def record_to_symptoms(record):
    return {field: record.get(field, 0) for field in config.SYMPTOM_FIELDS}
