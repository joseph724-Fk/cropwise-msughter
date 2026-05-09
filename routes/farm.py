from datetime import datetime, date, timedelta

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user

from models import db
from models.crop import Crop
from models.farm_record import FarmRecord

farm_bp = Blueprint("farm", __name__)


def is_ajax():
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


def get_task_status(due_date):
    today = date.today()

    if due_date < today:
        return "overdue"

    if due_date == today:
        return "due-today"

    return "upcoming"


def build_care_tasks(record):
    """
    Builds fertilizer, weeding, and harvest schedule for one farm record.
    """

    tasks = []
    today = date.today()

    crop = record.crop

    if not crop:
        return tasks

    fertilizer_days = crop.fertilizer_days or []
    weeding_days = crop.weeding_days or []

    # Fertilizer tasks
    for day in fertilizer_days:
        try:
            day_number = int(day)
        except (TypeError, ValueError):
            continue

        due_date = record.date_planted + timedelta(days=day_number)
        status = get_task_status(due_date)

        tasks.append({
            "type": "Fertilizer",
            "label": f"Apply fertilizer {day_number} days after planting",
            "due_date": due_date,
            "status": status,
            "days_left": (due_date - today).days,
        })

    # Weeding tasks
    for day in weeding_days:
        try:
            day_number = int(day)
        except (TypeError, ValueError):
            continue

        due_date = record.date_planted + timedelta(days=day_number)
        status = get_task_status(due_date)

        tasks.append({
            "type": "Weeding",
            "label": f"Weed farm {day_number} days after planting",
            "due_date": due_date,
            "status": status,
            "days_left": (due_date - today).days,
        })

    # Harvest task
    harvest_due_date = record.expected_harvest
    harvest_status = get_task_status(harvest_due_date)

    tasks.append({
        "type": "Harvest",
        "label": f"Expected harvest for {crop.common_name}",
        "due_date": harvest_due_date,
        "status": harvest_status,
        "days_left": (harvest_due_date - today).days,
    })

    tasks.sort(key=lambda item: item["due_date"])

    return tasks
    """
    Builds fertilizer and weeding schedule for one farm record.

    It uses:
    - record.date_planted
    - record.crop.fertilizer_days
    - record.crop.weeding_days

    Example:
    fertilizer_days = [14, 35]
    weeding_days = [14, 28, 42]
    """

    tasks = []
    today = date.today()

    crop = record.crop

    if not crop:
        return tasks

    fertilizer_days = crop.fertilizer_days or []
    weeding_days = crop.weeding_days or []

    for day in fertilizer_days:
        try:
            day_number = int(day)
        except (TypeError, ValueError):
            continue

        due_date = record.date_planted + timedelta(days=day_number)
        status = get_task_status(due_date)

        tasks.append({
            "type": "Fertilizer",
            "label": f"Apply fertilizer {day_number} days after planting",
            "due_date": due_date,
            "status": status,
            "days_left": (due_date - today).days,
        })

    for day in weeding_days:
        try:
            day_number = int(day)
        except (TypeError, ValueError):
            continue

        due_date = record.date_planted + timedelta(days=day_number)
        status = get_task_status(due_date)

        tasks.append({
            "type": "Weeding",
            "label": f"Weed farm {day_number} days after planting",
            "due_date": due_date,
            "status": status,
            "days_left": (due_date - today).days,
        })

    tasks.sort(key=lambda item: item["due_date"])

    return tasks


@farm_bp.route("/farm")
@login_required
def farm_tracker():
    records = (
        FarmRecord.query
        .filter_by(user_id=current_user.id)
        .order_by(FarmRecord.created_at.desc())
        .all()
    )

    crops = Crop.query.order_by(Crop.common_name.asc()).all()

    record_care_tasks = {
        record.uuid: build_care_tasks(record)
        for record in records
    }

    return render_template(
        "farm_tracker.html",
        records=records,
        crops=crops,
        record_care_tasks=record_care_tasks,
        title="Farm Tracker — CropWise",
    )


@farm_bp.route("/farm/add", methods=["POST"])
@login_required
def add_farm_record():
    crop_uuid = request.form.get("crop_uuid", "").strip()
    crop_id = request.form.get("crop_id", "").strip()
    date_planted_raw = request.form.get("date_planted", "").strip()
    notes = request.form.get("notes", "").strip()

    def fail(message, status=422):
        if is_ajax():
            return jsonify({"ok": False, "message": message}), status

        flash(message, "error")
        return redirect(url_for("farm.farm_tracker"))

    if not date_planted_raw:
        return fail("Planting date is required.")

    crop = None

    if crop_uuid:
        crop = Crop.query.filter_by(uuid=crop_uuid).first()
    elif crop_id:
        crop = Crop.query.get(crop_id)

    if not crop:
        return fail("Selected crop does not exist.", 404)

    try:
        date_planted = datetime.strptime(date_planted_raw, "%Y-%m-%d").date()
    except ValueError:
        return fail("Invalid planting date.")

    expected_harvest = FarmRecord.calculate_expected_harvest(
        date_planted=date_planted,
        harvest_weeks=crop.harvest_weeks,
    )

    record = FarmRecord(
        user_id=current_user.id,
        crop_id=crop.id,
        date_planted=date_planted,
        expected_harvest=expected_harvest,
        status="active",
        notes=notes,
    )

    db.session.add(record)
    db.session.commit()

    if is_ajax():
        return jsonify({
            "ok": True,
            "message": "Farm record added successfully.",
            "redirect": url_for("farm.farm_tracker"),
        })

    flash("Farm record added successfully.", "success")
    return redirect(url_for("farm.farm_tracker"))


@farm_bp.route("/farm/update/<uuid:record_uuid>", methods=["POST"])
@login_required
def update_farm_status(record_uuid):
    record = FarmRecord.query.filter_by(
        uuid=str(record_uuid),
        user_id=current_user.id,
    ).first_or_404()

    status = request.form.get("status", "").strip()

    if status not in ["active", "harvested", "failed"]:
        if is_ajax():
            return jsonify({"ok": False, "message": "Invalid farm status."}), 422

        flash("Invalid farm status.", "error")
        return redirect(url_for("farm.farm_tracker"))

    record.status = status
    db.session.commit()

    if is_ajax():
        return jsonify({
            "ok": True,
            "message": "Farm status updated.",
            "redirect": url_for("farm.farm_tracker"),
        })

    flash("Farm status updated.", "success")
    return redirect(url_for("farm.farm_tracker"))