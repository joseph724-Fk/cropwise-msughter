import uuid as uuid_lib
from datetime import timedelta
from models import db


class FarmRecord(db.Model):
    __tablename__ = "farm_records"

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(
        db.String(36),
        unique=True,
        nullable=False,
        index=True,
        default=lambda: str(uuid_lib.uuid4())
    )

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    crop_id = db.Column(db.Integer, db.ForeignKey("crops.id"), nullable=False, index=True)

    date_planted = db.Column(db.Date, nullable=False)
    expected_harvest = db.Column(db.Date, nullable=False)

    status = db.Column(
        db.Enum("active", "harvested", "failed"),
        default="active",
        nullable=False
    )

    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship("User", back_populates="farm_records")
    crop = db.relationship("Crop", back_populates="farm_records")

    def ensure_uuid(self):
        if not self.uuid:
            self.uuid = str(uuid_lib.uuid4())

    @staticmethod
    def calculate_expected_harvest(date_planted, harvest_weeks):
        return date_planted + timedelta(weeks=harvest_weeks)