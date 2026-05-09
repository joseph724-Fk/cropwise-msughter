from datetime import datetime

from flask import Blueprint, render_template
from flask_login import current_user
from models.crop import Crop

home_bp = Blueprint("home", __name__)


def seasonal_water_score(month, water_requirement):
    first_rainy = month in [3, 4, 5, 6, 7]
    second_rainy = month in [9, 10, 11]
    dry_season = month in [12, 1, 2]

    if first_rainy or second_rainy:
        scores = {
            "high": 1.0,
            "medium": 0.85,
            "low": 0.65,
        }
    elif dry_season:
        scores = {
            "low": 1.0,
            "medium": 0.60,
            "high": 0.30,
        }
    else:
        scores = {
            "medium": 0.75,
            "low": 0.65,
            "high": 0.55,
        }

    return scores.get(water_requirement, 0.5)


def public_crop_score(crop, current_month, max_yield):
    month_score = 1 if current_month in crop.planting_months else 0
    water_score = seasonal_water_score(current_month, crop.water_requirement)
    yield_score = crop.avg_yield_kg_per_ha / max_yield if max_yield > 0 else 0

    final_score = (
        0.55 * month_score +
        0.25 * water_score +
        0.20 * yield_score
    )

    return round(final_score, 3)


@home_bp.route("/")
def home():
    now = datetime.now()
    current_month = now.month
    month_name = now.strftime("%B")

    crops = Crop.query.all()
    max_yield = max([crop.avg_yield_kg_per_ha for crop in crops], default=1)

    scored = []

    for crop in crops:
        score = public_crop_score(
            crop=crop,
            current_month=current_month,
            max_yield=max_yield,
        )

        if score >= 0.50:
            scored.append({
                "crop": crop,
                "score": score,
            })

    scored.sort(key=lambda item: item["score"], reverse=True)

    best_crops = scored[:6]

    return render_template(
        "home.html",
        title="CropWise — Smart Crop Advisory by Msughter Sulega",
        month_name=month_name,
        current_month=current_month,
        best_crops=best_crops,
    )
