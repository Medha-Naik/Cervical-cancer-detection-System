"""Dashboard, history API and PDF report download."""
import io

from flask import Blueprint, jsonify, render_template, send_file, session

from ..services import predictions
from ..services.recommendations import get_recommendations, get_testing_recommendations
from ..services.reports import build_pdf_report
from .auth import login_required

bp = Blueprint("dashboard", __name__)


@bp.route("/dashboard")
@login_required
def dashboard():
    history = predictions.get_all_predictions(session["user_id"])
    return render_template(
        "dashboard.html", active="dashboard",
        history=history,
        risk_counts=predictions.get_risk_counts(session["user_id"]),
        total=len(history),
        trend_points=predictions.cumulative_trend(history),
    )


@bp.route("/api/history")
@login_required
def api_history():
    return jsonify(predictions.get_all_predictions(session["user_id"]))


@bp.route("/api/stats")
@login_required
def api_stats():
    counts = predictions.get_risk_counts(session["user_id"])
    return jsonify({"counts": counts, "total": sum(counts.values())})


@bp.route("/api/delete/<int:record_id>", methods=["DELETE"])
@login_required
def delete_record(record_id):
    try:
        deleted = predictions.delete_prediction(record_id, session["user_id"])
        return jsonify({"success": deleted})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/report/<int:record_id>")
@login_required
def download_report(record_id):
    record = predictions.get_record(record_id, session["user_id"])
    if not record:
        return "Report not found.", 404

    input_data = predictions.record_to_input_data(record)
    symptoms = predictions.record_to_symptoms(record)
    recommendations = get_recommendations(record["prediction"], input_data, symptoms)
    testing_recs = get_testing_recommendations(record["prediction"], input_data)

    pdf_bytes = build_pdf_report(record, input_data, symptoms, recommendations, testing_recs)
    filename = f"CervixGuard_Report_{record['patient_name'].replace(' ', '_')}_{record['id']}.pdf"
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename,
    )
