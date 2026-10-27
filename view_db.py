"""Print the assessments stored in the database:  python view_db.py"""
from cervixguard.db import connection


def view():
    with connection() as conn:
        total = conn.execute("SELECT COUNT(*) FROM predictions").fetchone()[0]
        rows = conn.execute("SELECT * FROM predictions ORDER BY id DESC").fetchall()
        counts = conn.execute(
            "SELECT prediction, COUNT(*) FROM predictions GROUP BY prediction"
        ).fetchall()

    print("=" * 70)
    print(f"  CervixGuard AI - Database Records ({total} total)")
    print("=" * 70)
    if not rows:
        print("  No records yet. Submit a form to add data.")
    for r in rows:
        print(f"\n  ID        : {r['id']}")
        print(f"  Patient   : {r['patient_name']}")
        print(f"  Age       : {r['age']}")
        print(f"  Prediction: {r['prediction']}")
        print(f"  Confidence: {r['confidence']}")
        print(f"  Timestamp : {r['timestamp']}")
        print("  " + "-" * 40)
    print("\n  Risk Breakdown:")
    for prediction, count in counts:
        print(f"    {prediction}: {count}")
    print("=" * 70)


if __name__ == "__main__":
    view()
