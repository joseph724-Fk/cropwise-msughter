import re
from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from models.crop import Crop
from models.farm_record import FarmRecord
from routes.dashboard import crop_score

bot_bp = Blueprint("bot", __name__)


def normalize(text):
    return " ".join((text or "").lower().strip().split())


def tokenize(text):
    return re.findall(r"[a-zA-Z0-9]+", normalize(text))


def contains_any(text, phrases):
    return any(phrase in text for phrase in phrases)


def has_greeting(text):
    words = set(tokenize(text))
    greeting_words = {"hi", "hello", "hey", "morning", "afternoon", "evening"}
    greeting_phrases = {
        "good morning",
        "good afternoon",
        "good evening",
        "hello cropwise",
        "hey cropwise",
        "hi cropwise",
    }

    if text in greeting_phrases:
        return True

    return bool(words.intersection(greeting_words)) and len(words) <= 5


def find_crop_in_message(message):
    crops = Crop.query.all()
    words = set(tokenize(message))

    for crop in crops:
        if crop.common_name.lower() in message:
            return crop

    for crop in crops:
        crop_words = set(tokenize(crop.common_name))
        if crop_words and crop_words.issubset(words):
            return crop

    for crop in crops:
        crop_words = set(tokenize(crop.common_name))
        if crop_words and words.intersection(crop_words):
            return crop

    return None


def water_meaning(value):
    meanings = {
        "low": "low water requirement, meaning it can tolerate relatively drier conditions better than high-water crops.",
        "medium": "medium water requirement, meaning it needs steady moisture but not waterlogged conditions.",
        "high": "high water requirement, meaning it performs best where rainfall, irrigation, or soil moisture is reliable.",
    }

    return meanings.get(value, "unknown water requirement.")


def format_months(months):
    names = {
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December",
    }

    try:
        values = [int(month) for month in months]
    except Exception:
        return "not specified"

    return ", ".join(names.get(month, str(month)) for month in values)


def crop_brief(crop):
    return (
        f"{crop.common_name} ({crop.botanical_name}) is a {crop.category.lower()} crop.\n\n"
        f"Soil suitability: {crop.soil_type}.\n"
        f"Water need: {water_meaning(crop.water_requirement)}\n"
        f"Planting months: {format_months(crop.planting_months)}.\n"
        f"Harvest time: about {crop.harvest_weeks} weeks.\n"
        f"Average yield: about {crop.avg_yield_kg_per_ha:,.0f} kg/ha.\n\n"
        f"{crop.description}"
    )


def recommendation_reply(limit=6):
    now = datetime.now()
    current_month = now.month
    month_name = now.strftime("%B")

    crops = Crop.query.all()

    if not crops:
        return "There are no crops in the CropWise database yet. Seed the crops table first."

    max_yield = max([crop.avg_yield_kg_per_ha for crop in crops], default=1)

    scored = []

    for crop in crops:
        score = crop_score(
            crop=crop,
            user_soil=current_user.soil_type,
            current_month=current_month,
            max_yield=max_yield,
        )

        if score >= 0.60:
            scored.append((crop, score))

    scored.sort(key=lambda item: item[1], reverse=True)
    top = scored[:limit]

    if not top:
        return (
            f"I could not find crops scoring 60% or above for {month_name} based on "
            f"{current_user.soil_type} soil in {current_user.lga}. Try checking the crop library "
            f"or update your soil profile."
        )

    lines = [
        f"For {month_name}, based on your {current_user.soil_type} soil in {current_user.lga}, I recommend:"
    ]

    for crop, score in top:
        lines.append(
            f"• {crop.common_name}: {round(score * 100)}% match, {crop.water_requirement} water need, "
            f"harvest in about {crop.harvest_weeks} weeks."
        )

    lines.append("\nThese rankings use planting month, soil suitability, water need, and yield reliability.")

    return "\n".join(lines)


def farm_summary_reply():
    records = (
        FarmRecord.query
        .filter_by(user_id=current_user.id)
        .order_by(FarmRecord.created_at.desc())
        .limit(6)
        .all()
    )

    if not records:
        return (
            "You do not have farm records yet. Open Farm Tracker, choose a crop, "
            "enter the planting date, and CropWise will calculate the expected harvest date."
        )

    lines = ["Here are your latest farm records:"]

    for record in records:
        lines.append(
            f"• {record.crop.common_name}: planted on {record.date_planted}, "
            f"expected harvest {record.expected_harvest}, status: {record.status}."
        )

    return "\n".join(lines)


def crop_list_by_water(level):
    crops = (
        Crop.query
        .filter_by(water_requirement=level)
        .order_by(Crop.common_name.asc())
        .limit(12)
        .all()
    )

    if not crops:
        return f"I could not find {level}-water crops in the database."

    return (
        f"Examples of {level}-water crops in CropWise are:\n"
        + "\n".join(f"• {crop.common_name}" for crop in crops)
    )


def crop_list_by_soil(soil):
    crops = (
        Crop.query
        .filter(Crop.soil_type.like(f"%{soil}%"))
        .order_by(Crop.common_name.asc())
        .limit(12)
        .all()
    )

    if not crops:
        return f"I could not find crops suitable for {soil} soil."

    return (
        f"Examples of crops suitable for {soil} soil are:\n"
        + "\n".join(f"• {crop.common_name}" for crop in crops)
    )


def category_reply(category):
    crops = (
        Crop.query
        .filter(Crop.category.like(f"%{category}%"))
        .order_by(Crop.common_name.asc())
        .limit(12)
        .all()
    )

    if not crops:
        return f"I could not find crops under the {category} category."

    return (
        f"Here are some {category.lower()} crops in the database:\n"
        + "\n".join(f"• {crop.common_name}" for crop in crops)
    )


def calculate_expression(message):
    safe = re.sub(r"[^0-9+\-*/(). ]", "", message)

    if not safe.strip():
        return None

    if not re.search(r"\d+\s*[\+\-\*/]\s*\d+", safe):
        return None

    try:
        result = eval(safe, {"__builtins__": {}}, {})
        return f"The answer is {result}."
    except Exception:
        return None


def explain_score():
    return (
        "CropWise ranks crops using this formula:\n\n"
        "Score = 0.40 × planting month match + 0.30 × soil match + "
        "0.20 × water suitability + 0.10 × yield reliability.\n\n"
        "Only crops scoring 60% and above are shown on the dashboard."
    )


@bot_bp.route("/bot/message", methods=["POST"])
@login_required
def bot_message():
    message = normalize(request.form.get("message", ""))

    if not message:
        return jsonify({"ok": False, "message": "Message cannot be empty."}), 422

    # Math / computation
    math_reply = calculate_expression(message)
    if math_reply:
        return jsonify({"ok": True, "reply": math_reply})

    recommendation_keywords = [
        "recommend",
        "recommendation",
        "what should i plant",
        "what to plant",
        "tell me what to plant",
        "plant this month",
        "best crop",
        "best crops",
        "crop for this month",
        "which crop",
        "which crops",
        "what can i grow",
        "what should i grow",
        "suggest crop",
        "suggest crops",
    ]

    farm_keywords = [
        "my farm",
        "farm tracker",
        "my crops",
        "what did i plant",
        "my planted crops",
        "my harvest",
        "farm summary",
        "show farm",
        "show my farm",
    ]

    if contains_any(message, recommendation_keywords):
        return jsonify({"ok": True, "reply": recommendation_reply()})

    if contains_any(message, farm_keywords):
        return jsonify({"ok": True, "reply": farm_summary_reply()})

    if "score" in message or "formula" in message or "ranking" in message or "rank" in message:
        return jsonify({"ok": True, "reply": explain_score()})

    if has_greeting(message):
        return jsonify({
            "ok": True,
            "reply": (
                f"Hello {current_user.first_name}. I am CropWise Assistant. "
                f"You can ask me what to plant this month, ask about any crop, check water needs, "
                f"ask about soil suitability, calculate simple values, or view your farm tracker summary."
            )
        })

    if "my lga" in message or "location" in message or "where am i" in message:
        return jsonify({
            "ok": True,
            "reply": f"Your CropWise profile is set to {current_user.lga} LGA with {current_user.soil_type} soil."
        })

    if "my soil" in message or "soil type" in message:
        return jsonify({
            "ok": True,
            "reply": (
                f"Your soil profile is set to {current_user.soil_type}. "
                f"CropWise uses this to rank crop suitability."
            )
        })

    if "low water" in message or "low-water" in message:
        return jsonify({"ok": True, "reply": crop_list_by_water("low")})

    if "medium water" in message or "medium-water" in message:
        return jsonify({"ok": True, "reply": crop_list_by_water("medium")})

    if "high water" in message or "high-water" in message:
        return jsonify({"ok": True, "reply": crop_list_by_water("high")})

    if "sandy" in message:
        return jsonify({"ok": True, "reply": crop_list_by_soil("sandy")})

    if "loamy" in message:
        return jsonify({"ok": True, "reply": crop_list_by_soil("loamy")})

    if "clay" in message:
        return jsonify({"ok": True, "reply": crop_list_by_soil("clay")})

    if "vegetable" in message or "vegetables" in message:
        return jsonify({"ok": True, "reply": category_reply("Vegetable")})

    if "fruit" in message or "fruits" in message:
        return jsonify({"ok": True, "reply": category_reply("Fruit")})

    if "tuber" in message or "tubers" in message:
        return jsonify({"ok": True, "reply": category_reply("Tuber")})

    if "cereal" in message or "cereals" in message:
        return jsonify({"ok": True, "reply": category_reply("Cereal")})

    if "legume" in message or "legumes" in message:
        return jsonify({"ok": True, "reply": category_reply("Legume")})

    matched_crop = find_crop_in_message(message)

    if matched_crop:
        if "harvest" in message or "how long" in message or "duration" in message:
            return jsonify({
                "ok": True,
                "reply": f"{matched_crop.common_name} usually takes about {matched_crop.harvest_weeks} weeks from planting to harvest."
            })

        if "water" in message:
            return jsonify({
                "ok": True,
                "reply": f"{matched_crop.common_name} has {water_meaning(matched_crop.water_requirement)}"
            })

        if "soil" in message:
            return jsonify({
                "ok": True,
                "reply": f"{matched_crop.common_name} is suitable for {matched_crop.soil_type} soil."
            })

        return jsonify({"ok": True, "reply": crop_brief(matched_crop)})

    if "help" in message or "what can you do" in message:
        return jsonify({
            "ok": True,
            "reply": (
                "You can ask me:\n"
                "• What should I plant this month?\n"
                "• Tell me about banana\n"
                "• How long does cassava take to harvest?\n"
                "• Which crops need low water?\n"
                "• Which crops grow in loamy soil?\n"
                "• Show my farm tracker summary\n"
                "• How does CropWise score crops?\n"
                "• Calculate 25 * 4"
            )
        })

    return jsonify({
        "ok": True,
        "reply": (
            "I can answer from the CropWise database, but I did not understand that exact question. "
            "Try asking about crop recommendations, crop names, water needs, soil type, harvest time, "
            "farm tracker, or the scoring formula."
        )
    })