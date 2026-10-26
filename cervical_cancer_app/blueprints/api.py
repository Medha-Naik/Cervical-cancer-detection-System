from flask import Blueprint, jsonify, session
from db.database import delete_prediction, get_all_predictions, get_risk_counts

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/delete/<int:record_id>", methods=["DELETE"])
def delete_record(record_id):
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Not logged in"}), 401
    try:
        delete_prediction(record_id, session["user_id"])
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/stats")
def stats():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
    risk_counts = get_risk_counts(session["user_id"])
    return jsonify({"total": sum(risk_counts.values()), "risk_counts": risk_counts})