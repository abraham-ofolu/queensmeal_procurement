import os

from flask import Flask
from flask_login import LoginManager

from app.extensions import db, migrate
from app.models import User

# IMPORTANT: import at module level (NOT inside create_app)
from app.utils.cloudinary import init_cloudinary


login_manager = LoginManager()
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def create_app():
    app = Flask(__name__)

    # -----------------------------
    # Config
    # -----------------------------
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///app.db").replace(
        "postgres://", "postgresql://"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Cloudinary env vars (Render → Environment)
    app.config["CLOUDINARY_CLOUD_NAME"] = os.environ.get("CLOUDINARY_CLOUD_NAME")
    app.config["CLOUDINARY_API_KEY"] = os.environ.get("CLOUDINARY_API_KEY")
    app.config["CLOUDINARY_API_SECRET"] = os.environ.get("CLOUDINARY_API_SECRET")

    # -----------------------------
    # Extensions
    # -----------------------------
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # -----------------------------
    # Cloudinary init (safe)
    # -----------------------------
    # Only init if credentials exist
    if (
        app.config.get("CLOUDINARY_CLOUD_NAME")
        and app.config.get("CLOUDINARY_API_KEY")
        and app.config.get("CLOUDINARY_API_SECRET")
    ):
        init_cloudinary(app)

    # -----------------------------
    # Blueprints
    # -----------------------------
    from app.routes.auth import auth_bp
    from app.routes.procurement import procurement_bp
    from app.routes.vendors import vendors_bp
    from app.routes.finance import finance_bp
    from app.routes.reports import reports_bp
    from app.routes.audit import audit_bp
    from app.routes.users import users_bp
    from app.routes.main import main_bp


    app.register_blueprint(auth_bp)
    app.register_blueprint(procurement_bp, url_prefix="/procurement")
    app.register_blueprint(vendors_bp, url_prefix="/vendors")
    app.register_blueprint(finance_bp, url_prefix="/finance")
    app.register_blueprint(reports_bp, url_prefix="/reports")
    app.register_blueprint(audit_bp, url_prefix="/audit")
    app.register_blueprint(users_bp, url_prefix="/users")
    app.register_blueprint(main_bp)

    return app
