from flask import Blueprint, render_template, request
from flask_login import login_required
from models.crop import Crop

crops_bp = Blueprint("crops", __name__)


@crops_bp.route("/crops")
@login_required
def crops():
    keyword = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()

    query = Crop.query

    if keyword:
        search = f"%{keyword}%"
        query = query.filter(
            (Crop.common_name.like(search)) |
            (Crop.botanical_name.like(search)) |
            (Crop.description.like(search))
        )

    if category:
        query = query.filter(Crop.category == category)

    crops_list = query.order_by(Crop.common_name.asc()).all()

    categories = [
        item[0]
        for item in Crop.query.with_entities(Crop.category).distinct().order_by(Crop.category.asc()).all()
    ]

    return render_template(
        "crops.html",
        crops=crops_list,
        categories=categories,
        keyword=keyword,
        selected_category=category,
    )


@crops_bp.route("/crops/<uuid:crop_uuid>")
@login_required
def crop_detail(crop_uuid):
    crop = Crop.query.filter_by(uuid=str(crop_uuid)).first_or_404()
    return render_template("crop_detail.html", crop=crop)