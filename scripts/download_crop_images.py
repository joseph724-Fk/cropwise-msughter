from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
IMAGE_DIR = ROOT / "static" / "images" / "crops"
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

connection = pymysql.connect(
    host=os.getenv("DB_HOST", "127.0.0.1"),
    port=int(os.getenv("DB_PORT", "3306")),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", ""),
    database=os.getenv("DB_NAME", "cropwise_db"),
    cursorclass=pymysql.cursors.DictCursor,
)

def make_placeholder(filename, crop_name):
    path = IMAGE_DIR / filename

    if path.exists():
        return

    img = Image.new("RGB", (1200, 800), color=(226, 246, 219))
    draw = ImageDraw.Draw(img)

    title = crop_name[:28]
    subtitle = "CropWise"

    draw.rectangle([0, 0, 1200, 800], fill=(226, 246, 219))
    draw.ellipse([760, -130, 1180, 290], fill=(244, 162, 97))
    draw.ellipse([-120, 520, 280, 920], fill=(45, 106, 79))

    try:
        font_big = ImageFont.truetype("arial.ttf", 96)
        font_small = ImageFont.truetype("arial.ttf", 34)
    except Exception:
        font_big = ImageFont.load_default()
        font_small = ImageFont.load_default()

    draw.text((90, 270), title, fill=(27, 67, 50), font=font_big)
    draw.text((94, 390), subtitle, fill=(45, 106, 79), font=font_small)

    img.save(path, quality=92)

with connection:
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, common_name, image_filename FROM crops ORDER BY id ASC")
        crops = cursor.fetchall()

        for crop in crops:
            filename = crop["image_filename"] or f"crop_{crop['id']}.jpg"
            make_placeholder(filename, crop["common_name"])

print(f"Done. Images stored in: {IMAGE_DIR}")