import os
from flask import Flask
from flask_login import LoginManager
from app.extensions import db, login_manager

def create_app():
    app = Flask(__name__)

    # =========================
    # BASIC CONFIG
    # =========================
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")

    # =========================
    # DATABASE CONFIG (THIS WAS MISSING / BROKEN)
    # =========================
    database_url = os.environ.get("SQLALCHEMY_DATABASE_URI")

    if not database_url:
        raise RuntimeError(
            "SQLALCHEMY_DATABASE_URI is not set in environment variables"
        )

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # =========================
    # INIT EXTENSIONS (ORDER MATTERS)
    # =========================
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # =========================
    # BLUEPRINTS
    # =========================
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

    return app
