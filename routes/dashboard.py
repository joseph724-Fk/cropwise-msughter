from datetime import datetime

from flask import Blueprint, render_template
from flask_login import login_required, current_user

from models.crop import Crop

dashboard_bp = Blueprint("dashboard", __name__)


def water_score_for_month(month, water_requirement):
    """
    Lagos farming logic:
    - Rainy season supports high/medium water crops better.
    - Dry season favors low-water crops unless irrigation is available.
    """

    rainy_months = [3, 4, 5, 6, 7, 9, 10, 11]
    dry_months = [12, 1, 2]

    if month in rainy_months:
        scores = {
            "high": 1.0,
            "medium": 0.85,
            "low": 0.65,
        }
    elif month in dry_months:
        scores = {
            "low": 1.0,
            "medium": 0.65,
            "high": 0.35,
        }
    else:
        scores = {
            "medium": 0.8,
            "low": 0.7,
            "high": 0.55,
        }

    return scores.get(water_requirement, 0.5)


def soil_match_score(crop_soil, user_soil):
    crop_soil = (crop_soil or "").lower()
    user_soil = (user_soil or "").lower()

    if not user_soil:
        return 0.5

    if user_soil in crop_soil:
        return 1.0

    return 0.35


def crop_score(crop, user_soil, current_month, max_yield):
    planting_months = crop.planting_months or []

    try:
        planting_months = [int(month) for month in planting_months]
    except Exception:
        planting_months = []

    month_match = 1.0 if current_month in planting_months else 0.0
    soil_match = soil_match_score(crop.soil_type, user_soil)
    water_match = water_score_for_month(current_month, crop.water_requirement)
    yield_score = crop.avg_yield_kg_per_ha / max_yield if max_yield else 0.0

    final_score = (
        0.45 * month_match +
        0.25 * soil_match +
        0.20 * water_match +
        0.10 * yield_score
    )

    return round(final_score, 3)


def recommendation_reason(crop, user_soil, current_month, month_name):
    reasons = []

    planting_months = crop.planting_months or []

    try:
        planting_months = [int(month) for month in planting_months]
    except Exception:
        planting_months = []

    if current_month in planting_months:
        reasons.append(f"{month_name} is within its recommended planting period")
    else:
        reasons.append(f"{month_name} is not its strongest planting month, but it may still be considered with proper management")

    if user_soil and user_soil.lower() in (crop.soil_type or "").lower():
        reasons.append(f"it matches your {user_soil.title()} soil profile")
    else:
        reasons.append(f"it prefers {crop.soil_type} soil")

    reasons.append(f"it has a {crop.water_requirement} water requirement")
    reasons.append(f"expected harvest is about {crop.harvest_weeks} weeks")

    return "; ".join(reasons) + "."


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    now = datetime.now()
    current_month = now.month
    month_name = now.strftime("%B")

    crops = Crop.query.all()
    max_yield = max([crop.avg_yield_kg_per_ha for crop in crops], default=1)

    scored_crops = []

    for crop in crops:
        score = crop_score(
            crop=crop,
            user_soil=current_user.soil_type,
            current_month=current_month,
            max_yield=max_yield,
        )

        # Dashboard should focus on current month.
        # Crop must either match current month or score strongly enough.
        planting_months = crop.planting_months or []

        try:
            planting_months = [int(month) for month in planting_months]
        except Exception:
            planting_months = []

        is_current_month_crop = current_month in planting_months

        if is_current_month_crop and score >= 0.55:
            scored_crops.append({
                "crop": crop,
                "score": score,
                "reason": recommendation_reason(
                    crop=crop,
                    user_soil=current_user.soil_type,
                    current_month=current_month,
                    month_name=month_name,
                ),
            })

    scored_crops.sort(key=lambda item: item["score"], reverse=True)

    recommended = scored_crops[:6]

    return render_template(
        "dashboard.html",
        title=f"{month_name} Crop Recommendations — CropWise",
        recommended=recommended,
        month_name=month_name,
        current_month=current_month,
    )