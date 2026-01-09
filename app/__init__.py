import os
from flask import Flask
from flask_login import LoginManager

from app.extensions import db
from app.models.user import User

login_manager = LoginManager()
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id: str):
    try:
        return User.query.get(int(user_id))
    except Exception:
        return None


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")

    # DATABASE
    database_url = os.getenv("DATABASE_URL")
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url or "sqlite:///app.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # INIT EXTENSIONS (IMPORTANT: exactly one db instance from app.extensions)
    db.init_app(app)
    login_manager.init_app(app)

    # ROUTES
    from app.routes import (
        main_bp,
        auth_bp,
        procurement_bp,
        vendors_bp,
        finance_bp,
        reports_bp,
    )

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(procurement_bp, url_prefix="/procurement")
    app.register_blueprint(vendors_bp, url_prefix="/vendors")
    app.register_blueprint(finance_bp, url_prefix="/finance")
    app.register_blueprint(reports_bp, url_prefix="/reports")

    # CREATE TABLES
    with app.app_context():
        db.create_all()

    return app
