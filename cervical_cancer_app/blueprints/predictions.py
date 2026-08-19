from flask import Blueprint, render_template, request, redirect, url_for, session
from ml.predictor import get_model, predict, get_recommendations, get_testing_recommendations
from db.database import save_prediction

predictions_bp = Blueprint("predictions", __name__)


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


@predictions_bp.route("/")
@login_required
def index():
    return render_template("index.html")


@predictions_bp.route("/predict", methods=["POST"])
@login_required
def predict_route():
    if get_model() is None:
        return render_template("result.html", error="Model not loaded.")

    patient_name = request.form.get("patient_name", "").strip() or "Unknown"

    try:
        model_data = get_model()
        features   = model_data["features"]
        input_data = {feat: float(request.form.get(feat, 0)) for feat in features}
    except Exception as e:
        return render_template("result.html", error=str(e))

    result       = predict(input_data)
    recs         = get_recommendations(result["prediction"], input_data)
    testing_recs = get_testing_recommendations(result["prediction"], input_data)

    try:
        save_prediction(session["user_id"], patient_name, input_data, result["prediction"], result["confidence"])
    except Exception as e:
        print(f"[DB] Save failed: {e}")

    return render_template(
        "result.html",
        patient_name    = patient_name,
        prediction      = result["prediction"],
        risk_class      = result["risk_class"],
        confidence      = result["confidence"],
        prob_at_risk    = result["prob_at_risk"],
        recommendations = recs,
        testing_recs    = testing_recs,
        input_data      = input_data,
    )