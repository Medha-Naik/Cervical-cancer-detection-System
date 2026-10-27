"""Register, log in/out, and the language switcher."""
from functools import wraps

from flask import (Blueprint, flash, redirect, render_template, request, session, url_for)

from ..services import users
from ..translations import TRANSLATIONS

bp = Blueprint("auth", __name__)

MIN_PASSWORD_LENGTH = 8
_COMMON_PASSWORDS = {
    "password", "password1", "password123", "passw0rd", "12345678", "123456789", "1234567890",
    "qwerty123", "qwertyuiop", "iloveyou1", "admin123", "welcome1", "abc12345", "letmein123",
}


def password_problem(password, username, full_name=""):
    """Return a message saying what is wrong with the password, or None if it is fine."""
    if len(password) < MIN_PASSWORD_LENGTH:
        return f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
    if not any(ch.isalpha() for ch in password) or not any(ch.isdigit() for ch in password):
        return "Password must contain at least one letter and one number."
    lowered = password.lower()
    if lowered in _COMMON_PASSWORDS:
        return "That password is too common. Please choose a different one."
    if len(username) >= 3 and username.lower() in lowered:
        return "Password must not contain your username."
    return None


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


@bp.route("/lang/<code>")
def set_lang(code):
    if code in TRANSLATIONS:
        session["lang"] = code
    return redirect(request.referrer or url_for("assess.index"))


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        email = request.form.get("email", "").strip() or None
        full_name = request.form.get("full_name", "").strip()
        if not full_name or not username or not password:
            flash("Full name, username and password are required.")
            return render_template("register.html")
        problem = password_problem(password, username, full_name)
        if problem:
            flash(problem)
            return render_template("register.html")
        if users.username_taken(username):
            flash("That username is already taken.")
            return render_template("register.html")
        session["user_id"] = users.create_user(username, password, email, full_name)
        session["username"] = username
        return redirect(url_for("assess.index"))
    return render_template("register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = users.authenticate(request.form.get("username", "").strip(),
                                  request.form.get("password", ""))
        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(request.args.get("next") or url_for("assess.index"))
        flash("Invalid username or password.")
    return render_template("login.html")


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))