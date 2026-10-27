"""Create or upgrade the SQLite database:  python setup_db.py

Safe to re-run. The schema itself lives in cervixguard/db.py.
"""
from cervixguard import config
from cervixguard.db import connection, init_db


def setup():
    print("=" * 50)
    print("  CervixGuard AI - Database Setup")
    print("=" * 50)
    init_db()
    with connection() as conn:
        pred_count = conn.execute("SELECT COUNT(*) FROM predictions").fetchone()[0]
        user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    print(f"Database ready    : {config.DB_PATH}")
    print("Tables ready       : users, predictions, vaccine_registrations")
    print(f"Users registered   : {user_count}")
    print(f"Predictions stored : {pred_count}")
    print("You can now run: python run.py")
    print("=" * 50)


if __name__ == "__main__":
    setup()
