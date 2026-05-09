from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models import db
from models.user import User

auth_bp = Blueprint("auth", __name__)


def is_ajax():
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            message = "Email and password are required."
            if is_ajax():
                return jsonify({"ok": False, "message": message}), 422
            flash(message, "error")
            return render_template("login.html")

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)

            if is_ajax():
                return jsonify({
                    "ok": True,
                    "message": "Login successful. Redirecting...",
                    "redirect": url_for("dashboard.dashboard")
                })

            return redirect(url_for("dashboard.dashboard"))

        message = "Invalid email or password."

        if is_ajax():
            return jsonify({"ok": False, "message": message}), 401

        flash(message, "error")

    return render_template("login.html")


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        lga = request.form.get("lga", "").strip()
        soil_type = request.form.get("soil_type", "").strip().lower()

        allowed_soils = {"sandy", "loamy", "clay"}
        allowed_lgas = {"Ikorodu", "Epe", "Badagry"}

        def fail(message, status=422):
            if is_ajax():
                return jsonify({"ok": False, "message": message}), status
            flash(message, "error")
            return render_template("signup.html")

        if not full_name or not email or not password or not lga or not soil_type:
            return fail("All fields are required.")

        if len(password) < 6:
            return fail("Password must be at least 6 characters.")

        if lga not in allowed_lgas:
            return fail("Please select a supported Lagos LGA.")

        if soil_type not in allowed_soils:
            return fail("Please select a valid soil type.")

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return fail("An account already exists with that email.", 409)

        user = User(
            full_name=full_name,
            email=email,
            lga=lga,
            soil_type=soil_type,
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        login_user(user)

        if is_ajax():
            return jsonify({
                "ok": True,
                "message": "Account created successfully. Redirecting...",
                "redirect": url_for("dashboard.dashboard")
            })

        return redirect(url_for("dashboard.dashboard"))

    return render_template("signup.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))