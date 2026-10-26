"""The assessment form and prediction."""
from datetime import datetime, timedelta

from flask import Blueprint, redirect, render_template, request, session, url_for

from .. import config
from ..ml import model as ml_model
from ..services import predictions, users
from ..services.recommendations import get_recommendations, get_testing_recommendations
from .auth import login_required

bp = Blueprint("assess", __name__)


@bp.route("/")
@login_required
def index():
    return render_template("index.html", active="assess")


@bp.route("/predict", methods=["GET", "POST"])
@login_required
def predict():
    if request.method == "GET":
        # Opening /predict directly (or coming back to it, e.g. after switching language)
        # has no form data, so send the user to the assessment form.
        return redirect(url_for("assess.index"))
    model_data = ml_model.get_model_data()
    if model_data is None:
        return render_template("result.html", error="Model not loaded. Run train_model.py first.")
    # The name comes from the account. Older accounts that have none yet fall back to the
    # form value, which is then saved to the account.
    profile = users.get_profile(session["user_id"]) or {}
    patient_name = profile.get("full_name") or request.form.get("patient_name", "").strip() or "Unknown"
    if not profile.get("full_name") and patient_name != "Unknown":
        users.save_full_name(session["user_id"], patient_name)

    try:
        input_data = {feat: float(request.form.get(feat, 0)) for feat in model_data["features"]}
    except Exception as e:
        return render_template("result.html", error=str(e))

    # Age comes from the birth year on the account (accounts without one enter it once here).
    birth_year = profile.get("birth_year")
    if birth_year is None:
        birth_year = users.parse_birth_year(request.form.get("birth_year"))
        if birth_year is None:
            return render_template("result.html", error="Please enter a valid birth year.")
        users.save_birth_year(session["user_id"], birth_year)
    input_data["Age"] = float(users.age_from_birth_year(birth_year))

    symptoms = {f: int(request.form.get(f, 0) == "1") for f in config.SYMPTOM_FIELDS}
    urgent_flag = any(symptoms.values())

    prob = ml_model.predict_probability(input_data)
    risk_label, risk_class = ml_model.classify_risk(prob)
    confidence = f"{prob * 100:.1f}%"

    recommendations = get_recommendations(risk_label, input_data, symptoms)
    testing_recs = get_testing_recommendations(risk_label, input_data)

    record_id = None
    try:
        record_id = predictions.save_prediction(session["user_id"], patient_name, input_data, symptoms,
                                                urgent_flag, risk_label, confidence)
        print(f"Saved: {patient_name} -> {risk_label} (id={record_id})")
    except Exception as e:
        print(f"DB save failed: {e}")

    # Remember the latest result for the chatbot's context.
    session["last_result"] = {
        "patient_name": patient_name,
        "risk": risk_label,
        "confidence": confidence,
        "urgent": urgent_flag,
    }

    # Redirect to the saved result's own page. A page that is the direct answer to a POST
    # breaks on refresh and when the language is switched (the browser tries to GET /predict).
    if record_id:
        return redirect(url_for("assess.result", record_id=record_id))

    followup_days = config.FOLLOWUP_DAYS.get(risk_label, config.DEFAULT_FOLLOWUP_DAYS)
    suggested_date = (datetime.now() + timedelta(days=followup_days)).strftime("%Y-%m-%d")
    return render_template(
        "result.html",
        patient_name=patient_name, prediction=risk_label,
        risk_class=risk_class, confidence=confidence,
        prob_at_risk=round(prob * 100, 1),
        recommendations=recommendations,
        testing_recs=testing_recs,
        input_data={**input_data, **symptoms},
        record_id=record_id,
        suggested_date=suggested_date,
    )


@bp.route("/result/<int:record_id>")
@login_required
def result(record_id):
    """Show a saved assessment result (the page /predict redirects to)."""
    record = predictions.get_record(record_id, session["user_id"])
    if not record:
        return redirect(url_for("assess.index"))

    risk_label = record["prediction"]
    risk_class = next((css for label, css, _ in config.RISK_TIERS if label == risk_label), "success")
    try:
        prob_at_risk = round(float(str(record["confidence"]).rstrip("%")), 1)
    except ValueError:
        prob_at_risk = 0.0

    input_data = predictions.record_to_input_data(record)
    symptoms = predictions.record_to_symptoms(record)

    followup_days = config.FOLLOWUP_DAYS.get(risk_label, config.DEFAULT_FOLLOWUP_DAYS)
    try:
        assessed_on = datetime.strptime(record["timestamp"], "%Y-%m-%d %H:%M:%S")
    except (TypeError, ValueError):
        assessed_on = datetime.now()
    suggested_date = (assessed_on + timedelta(days=followup_days)).strftime("%Y-%m-%d")

    return render_template(
        "result.html",
        patient_name=record["patient_name"], prediction=risk_label,
        risk_class=risk_class, confidence=record["confidence"],
        prob_at_risk=prob_at_risk,
        recommendations=get_recommendations(risk_label, input_data, symptoms),
        testing_recs=get_testing_recommendations(risk_label, input_data),
        input_data={**input_data, **symptoms},
        record_id=record_id,
        suggested_date=suggested_date,
    )