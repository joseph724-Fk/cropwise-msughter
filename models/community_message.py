import uuid as uuid_lib
from models import db


class CommunityMessage(db.Model):
    __tablename__ = "community_messages"

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(
        db.String(36),
        unique=True,
        nullable=False,
        index=True,
        default=lambda: str(uuid_lib.uuid4())
    )

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    lga = db.Column(db.String(100), nullable=False, index=True)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship("User")