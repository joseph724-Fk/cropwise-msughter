from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user

from models import db
from models.community_message import CommunityMessage

community_bp = Blueprint("community", __name__)


@community_bp.route("/community")
@login_required
def community_page():
    return render_template(
        "community.html",
        title=f"{current_user.lga} Farmers Community — CropWise"
    )


@community_bp.route("/community/messages", methods=["GET"])
@login_required
def get_messages():
    messages = (
        CommunityMessage.query
        .filter_by(lga=current_user.lga)
        .order_by(CommunityMessage.created_at.desc())
        .limit(60)
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
                "is_me": msg.user_id == current_user.id,
                "message": msg.message,
                "created_at": msg.created_at.strftime("%I:%M %p") if msg.created_at else ""
            }
            for msg in messages
        ]
    })


@community_bp.route("/community/messages", methods=["POST"])
@login_required
def send_message():
    message = request.form.get("message", "").strip()

    if not message:
        return jsonify({"ok": False, "message": "Message cannot be empty."}), 422

    if len(message) > 600:
        return jsonify({"ok": False, "message": "Message is too long. Keep it under 600 characters."}), 422

    chat_message = CommunityMessage(
        user_id=current_user.id,
        lga=current_user.lga,
        message=message
    )

    db.session.add(chat_message)
    db.session.commit()

    return jsonify({
        "ok": True,
        "message": "Message sent successfully."
    })