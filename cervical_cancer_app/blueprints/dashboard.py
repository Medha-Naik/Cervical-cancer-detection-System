from flask import Blueprint, render_template, session, redirect, url_for
from db.database import get_all_predictions, get_risk_counts, get_vaccine_doses
from blueprints.vaccine import compute_reminders

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user_id     = session["user_id"]
    history     = get_all_predictions(user_id)
    risk_counts = get_risk_counts(user_id)
    total       = len(history)

    # ── Vaccine reminders ─────────────────────────────────────────────────────
    doses             = get_vaccine_doses(user_id)
    vaccine_reminders = compute_reminders(doses)

    return render_template(
        "dashboard.html",
        history           = history,
        risk_counts       = risk_counts,
        total             = total,
        vaccine_reminders = vaccine_reminders,
    )