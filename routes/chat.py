from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from models import db
from models.chat_message import ChatMessage

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/chat/messages", methods=["GET"])
@login_required
def get_messages():
    messages = (
        ChatMessage.query
        .filter_by(lga=current_user.lga)
        .order_by(ChatMessage.created_at.desc())
        .limit(30)
        .all()
    )

    messages.reverse()

    return jsonify({
        "ok": True,
        "lga": current_user.lga,
        "messages": [
            {
                "uuid": msg.uuid,
                "name": msg.user.first_name if msg.user else "Farmer",
                "message": msg.message,
                "created_at": msg.created_at.strftime("%I:%M %p") if msg.created_at else ""
            }
            for msg in messages
        ]
    })


@chat_bp.route("/chat/messages", methods=["POST"])
@login_required
def send_message():
    message = request.form.get("message", "").strip()

    if not message:
        return jsonify({"ok": False, "message": "Message cannot be empty."}), 422

    if len(message) > 500:
        return jsonify({"ok": False, "message": "Message is too long."}), 422

    chat_message = ChatMessage(
        user_id=current_user.id,
        lga=current_user.lga,
        message=message
    )

    db.session.add(chat_message)
    db.session.commit()

    return jsonify({"ok": True, "message": "Message sent."})