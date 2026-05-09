from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user, logout_user
from werkzeug.security import check_password_hash
from models import db

profile_bp = Blueprint("profile", __name__)


def is_ajax():
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


def respond(ok, message, redirect_url=None, status=200):
    if is_ajax():
        payload = {"ok": ok, "message": message}
        if redirect_url:
            payload["redirect"] = redirect_url
        return jsonify(payload), status

    flash(message, "success" if ok else "error")
    if redirect_url:
        return redirect(redirect_url)
    return redirect(url_for("profile.account"))


@profile_bp.route("/account", methods=["GET"])
@login_required
def account():
    return render_template("account.html")


@profile_bp.route("/account/location", methods=["POST"])
@login_required
def update_location():
    lga = request.form.get("lga", "").strip()
    soil_type = request.form.get("soil_type", "").strip().lower()

    allowed_lgas = {"Ikorodu", "Epe", "Badagry"}
    allowed_soils = {"sandy", "loamy", "clay"}

    if lga not in allowed_lgas:
        return respond(False, "Please select a supported Lagos LGA.", status=422)

    if soil_type not in allowed_soils:
        return respond(False, "Please select a valid soil type.", status=422)

    current_user.lga = lga
    current_user.soil_type = soil_type

    db.session.commit()

    return respond(
        True,
        "Location and soil profile updated successfully.",
        url_for("profile.account")
    )


@profile_bp.route("/account/password", methods=["POST"])
@login_required
def update_password():
    current_password = request.form.get("current_password", "")
    new_password = request.form.get("new_password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not current_password or not new_password or not confirm_password:
        return respond(False, "All password fields are required.", status=422)

    if not current_user.check_password(current_password):
        return respond(False, "Your current password is incorrect.", status=401)

    if len(new_password) < 6:
        return respond(False, "New password must be at least 6 characters.", status=422)

    if new_password != confirm_password:
        return respond(False, "New password and confirmation do not match.", status=422)

    current_user.set_password(new_password)
    db.session.commit()

    return respond(True, "Password updated successfully.", url_for("profile.account"))


@profile_bp.route("/account/delete", methods=["POST"])
@login_required
def delete_account():
    password = request.form.get("password", "")
    confirm_text = request.form.get("confirm_text", "").strip()

    if confirm_text != "DELETE":
        return respond(False, "Type DELETE to confirm account deletion.", status=422)

    if not current_user.check_password(password):
        return respond(False, "Password is incorrect.", status=401)

    user = current_user._get_current_object()

    logout_user()

    db.session.delete(user)
    db.session.commit()

    return respond(True, "Account deleted successfully.", url_for("auth.signup"))