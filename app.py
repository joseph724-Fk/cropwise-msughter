from datetime import datetime

from flask import Flask, render_template
from config import Config
from models import db, login_manager
from models.community_message import CommunityMessage

from routes.home import home_bp
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.crops import crops_bp
from routes.farm import farm_bp
from routes.profile import profile_bp
from routes.bot import bot_bp
from routes.about import about_bp
from routes.community import community_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please login to continue."
    login_manager.login_message_category = "warning"

    from models.user import User
    from models.crop import Crop
    from models.farm_record import FarmRecord

    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(crops_bp)
    app.register_blueprint(farm_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(bot_bp)
    app.register_blueprint(about_bp)
    app.register_blueprint(community_bp)

    @app.context_processor
    def inject_globals():
        return {"current_year": datetime.now().year}

    @app.route("/offline")
    def offline():
        return render_template("offline.html")

    with app.app_context():
        db.create_all()

        for crop in Crop.query.filter((Crop.uuid == None) | (Crop.uuid == "")).all():
            crop.ensure_uuid()

        for record in FarmRecord.query.filter((FarmRecord.uuid == None) | (FarmRecord.uuid == "")).all():
            record.ensure_uuid()

        db.session.commit()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)