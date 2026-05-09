import uuid as uuid_lib
from models import db


class Crop(db.Model):
    __tablename__ = "crops"

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(
        db.String(36),
        unique=True,
        nullable=False,
        index=True,
        default=lambda: str(uuid_lib.uuid4())
    )

    common_name = db.Column(db.String(100), nullable=False, index=True)
    botanical_name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False, index=True)
    planting_months = db.Column(db.JSON, nullable=False)
    soil_type = db.Column(db.String(100), nullable=False)
    water_requirement = db.Column(db.Enum("low", "medium", "high"), nullable=False)
    harvest_weeks = db.Column(db.Integer, nullable=False)
    fertilizer_days = db.Column(db.JSON, nullable=True)
    weeding_days = db.Column(db.JSON, nullable=True)
    avg_yield_kg_per_ha = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)
    care_notes = db.Column(db.Text, nullable=True)
    image_filename = db.Column(db.String(200), nullable=True)

    farm_records = db.relationship("FarmRecord", back_populates="crop")

    def ensure_uuid(self):
        if not self.uuid:
            self.uuid = str(uuid_lib.uuid4())