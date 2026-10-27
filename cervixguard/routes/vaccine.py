"""HPV vaccine plans: registration, dose tracking and calendar export."""
import io
from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, send_file, session, url_for

from ..services import users, vaccine as vaccine_service
from .auth import login_required

bp = Blueprint("vaccine", __name__)


@bp.route("/vaccine")
def vaccine():
    registrations = []
    if session.get("user_id"):
        registrations = vaccine_service.list_registrations(session["user_id"])
    today = datetime.now().strftime("%Y-%m-%d")
    return render_template("vaccine.html", active="vaccine", registrations=registrations, today=today)


@bp.route("/vaccine/register", methods=["POST"])
@login_required
def register_vaccine():
    profile = users.get_profile(session["user_id"]) or {}
    patient_name = profile.get("full_name") or request.form.get("patient_name", "").strip() or "Unknown"
    if not profile.get("full_name") and patient_name != "Unknown":
        users.save_full_name(session["user_id"], patient_name)

    birth_year = profile.get("birth_year")
    if birth_year is None:
        birth_year = users.parse_birth_year(request.form.get("birth_year"))
        if birth_year is None:
            flash("Please enter a valid birth year.")
            return redirect(url_for("vaccine.vaccine"))
        users.save_birth_year(session["user_id"], birth_year)

    dose1_date_str = (request.form.get("start_date") or "").strip() or datetime.now().strftime("%Y-%m-%d")
    try:
        dose1_date = datetime.strptime(dose1_date_str, "%Y-%m-%d")
    except ValueError:
        flash("Please enter the date of dose 1 as YYYY-MM-DD.")
        return redirect(url_for("vaccine.vaccine"))

    # Age on the day of dose 1 (this decides 2 or 3 doses), not today's age.
    age_at_dose1 = float(dose1_date.year - int(birth_year))
    immunocompromised = request.form.get("immunocompromised") == "1"

    try:
        schedule = vaccine_service.compute_dose_schedule(
            age_at_dose1, dose1_date_str, immunocompromised
        )
    except ValueError as e:
        flash(str(e))
        return redirect(url_for("vaccine.vaccine"))

    vaccine_service.create_registration(
        session["user_id"], patient_name, age_at_dose1, schedule, immunocompromised
    )
    return redirect(url_for("vaccine.vaccine"))


@bp.route("/vaccine/dose/<int:reg_id>/<int:dose_num>/done", methods=["POST"])
@login_required
def mark_dose_done(reg_id, dose_num):
    vaccine_service.mark_dose_done(reg_id, dose_num, session["user_id"])
    return redirect(url_for("vaccine.vaccine"))


@bp.route("/vaccine/registration/<int:reg_id>/delete", methods=["POST"])
@login_required
def delete_vaccine_registration(reg_id):
    vaccine_service.delete_registration(reg_id, session["user_id"])
    return redirect(url_for("vaccine.vaccine"))


@bp.route("/vaccine/dose/<int:reg_id>/<int:dose_num>/ics")
@login_required
def dose_ics(reg_id, dose_num):
    if dose_num not in vaccine_service.DOSE_NUMBERS:
        return "Invalid dose.", 404
    reg = vaccine_service.get_registration(reg_id, session["user_id"])
    if not reg:
        return "Registration not found.", 404
    ics = vaccine_service.build_ics(reg, dose_num)
    if ics is None:
        return "This dose isn't scheduled for this plan.", 404
    return send_file(
        io.BytesIO(ics.encode("utf-8")),
        mimetype="text/calendar",
        as_attachment=True,
        download_name=f"hpv_dose{dose_num}_{reg['id']}.ics",
    )