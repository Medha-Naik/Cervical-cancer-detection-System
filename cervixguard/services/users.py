"""User accounts."""
from datetime import date, datetime

from werkzeug.security import check_password_hash, generate_password_hash

from ..db import connection


def username_taken(username):
    with connection() as conn:
        return conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone() is not None


def create_user(username, password, email=None, full_name=None, birth_year=None):
    """Insert a new user and return their id."""
    with connection() as conn:
        return conn.execute(
            "INSERT INTO users (username, password_hash, email, created_at, full_name, birth_year) VALUES (?,?,?,?,?,?)",
            (username, generate_password_hash(password), email,
             datetime.now().strftime("%Y-%m-%d %H:%M:%S"), full_name, birth_year),
        ).lastrowid


def authenticate(username, password):
    """Return the user row if the credentials are right, otherwise None."""
    with connection() as conn:
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if user and check_password_hash(user["password_hash"], password):
        return user
    return None


# ── Profile: name and birth year shared by the assessment and vaccine pages ──

MIN_AGE, MAX_AGE = 10, 100  # the same limits the assessment form always had


def birth_year_range():
    """(earliest, latest) birth year the app accepts."""
    this_year = date.today().year
    return this_year - MAX_AGE, this_year - MIN_AGE


def parse_birth_year(value):
    """Return the birth year as an int if it is valid, otherwise None."""
    try:
        year = int(str(value).strip())
    except (TypeError, ValueError):
        return None
    low, high = birth_year_range()
    return year if low <= year <= high else None


def age_from_birth_year(birth_year):
    """Age in years, always current - nothing to update in the database."""
    return date.today().year - birth_year if birth_year else None


def get_profile(user_id):
    """Return {"full_name", "birth_year", "age"} for the user, or None if there is no such user."""
    with connection() as conn:
        row = conn.execute("SELECT full_name, birth_year FROM users WHERE id = ?", (user_id,)).fetchone()
    if row is None:
        return None
    return {
        "full_name": row["full_name"],
        "birth_year": row["birth_year"],
        "age": age_from_birth_year(row["birth_year"]),
    }


def save_full_name(user_id, full_name):
    with connection() as conn:
        conn.execute("UPDATE users SET full_name = ? WHERE id = ?", (full_name, user_id))


def save_birth_year(user_id, birth_year):
    with connection() as conn:
        conn.execute("UPDATE users SET birth_year = ? WHERE id = ?", (int(birth_year), user_id))
