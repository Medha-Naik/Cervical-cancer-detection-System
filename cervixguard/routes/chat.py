"""Chatbot endpoint."""
from flask import Blueprint, jsonify, request, session

from ..services.chatbot import EMPTY_MESSAGE_REPLY, chatbot_reply

bp = Blueprint("chat", __name__)


@bp.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")
    if not message.strip():
        return jsonify({"reply": EMPTY_MESSAGE_REPLY})
    return jsonify({"reply": chatbot_reply(message, session.get("last_result"))})
