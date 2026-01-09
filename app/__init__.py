from flask import Flask
from app.extensions import db, login_manager
from app.models.user import User
import os

def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret")

    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.routes.auth import auth_bp
    from app.routes.procurement import procurement_bp
    from app.routes.vendors import vendors_bp
    from app.routes.finance import finance_bp
    from app.routes.reports import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(procurement_bp, url_prefix="/procurement")
    app.register_blueprint(vendors_bp, url_prefix="/vendors")
    app.register_blueprint(finance_bp, url_prefix="/finance")
    app.register_blueprint(reports_bp, url_prefix="/reports")

    # 🔑 CREATE TABLES ON FIRST BOOT
    with app.app_context():
        db.create_all()
        seed_default_users()

    return app


def seed_default_users():
    from app.models.user import User
    if not User.query.first():
        users = [
            User.create("procurement", "procurement", "procurement"),
            User.create("director", "director", "director"),
            User.create("finance", "finance", "finance"),
            User.create("audit", "audit", "audit"),
        ]
        db.session.add_all(users)
        db.session.commit()
