from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    lga = db.Column(db.String(100), nullable=False)
    soil_type = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    farm_records = db.relationship(
        "FarmRecord",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def first_name(self):
        return self.full_name.split()[0] if self.full_name else "Farmer"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))