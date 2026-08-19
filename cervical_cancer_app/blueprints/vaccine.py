from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db.database import save_vaccine_dose, get_vaccine_doses
from datetime import datetime
from dateutil.relativedelta import relativedelta   # pip install python-dateutil

vaccine_bp = Blueprint("vaccine", __name__)


def compute_reminders(doses: list[dict]) -> list[dict]:
    """
    Reminder schedule:
      • Dose 2 due exactly 2 months after Dose 1
      • Dose 3 due exactly 4 months after Dose 2  (= 6 months total from Dose 1)
    Only returns a reminder for a dose the user hasn't taken yet.
    """
    taken     = {d["dose_number"]: d["dose_date"] for d in doses}
    reminders = []
    now       = datetime.now()

    if 1 not in taken:
        return reminders                        # nothing to calculate without Dose 1

    d1 = datetime.strptime(taken[1], "%Y-%m-%d")

    # ── Dose 2 reminder ──────────────────────────────────────────────────────
    if 2 not in taken:
        due       = d1 + relativedelta(months=2)  # exactly 2 months after Dose 1
        overdue   = now.date() > due.date()
        days_left = (due.date() - now.date()).days

        reminders.append({
            "dose"     : 2,
            "due_date" : due.strftime("%Y-%m-%d"),
            "message"  : "Dose 2 is due 2 months after Dose 1.",
            "overdue"  : overdue,
            "days_left": days_left,
        })

    # ── Dose 3 reminder ──────────────────────────────────────────────────────
    # Requires Dose 2 to be logged; calculates 4 months from that date
    if 3 not in taken and 2 in taken:
        d2        = datetime.strptime(taken[2], "%Y-%m-%d")
        due       = d2 + relativedelta(months=4)  # exactly 4 months after Dose 2
        overdue   = now.date() > due.date()
        days_left = (due.date() - now.date()).days

        reminders.append({
            "dose"     : 3,
            "due_date" : due.strftime("%Y-%m-%d"),
            "message"  : "Dose 3 is due 4 months after Dose 2.",
            "overdue"  : overdue,
            "days_left": days_left,
        })

    return reminders


@vaccine_bp.route("/vaccine", methods=["GET", "POST"])
def vaccine():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]

    if request.method == "POST":
        dose_number = int(request.form.get("dose_number", 1))
        dose_date   = request.form.get("dose_date", "").strip()
        notes       = request.form.get("notes", "").strip()

        if not dose_date:
            flash("Please select a date for the dose.", "error")
        else:
            save_vaccine_dose(user_id, dose_number, dose_date, notes)
            flash(f"Dose {dose_number} recorded successfully!", "success")
            return redirect(url_for("vaccine.vaccine"))

    doses     = get_vaccine_doses(user_id)
    reminders = compute_reminders(doses)
    taken     = {d["dose_number"] for d in doses}
    next_dose = min({1, 2, 3} - taken) if taken != {1, 2, 3} else None
    now       = datetime.now().strftime("%Y-%m-%d")

    return render_template(
        "vaccine.html",
        doses     = doses,
        reminders = reminders,
        taken     = taken,
        next_dose = next_dose,
        complete  = taken == {1, 2, 3},
        now       = now,
    )