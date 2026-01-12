from flask import Flask
from flask_login import LoginManager

from app.config import Config
from app.extensions import db

from app.routes.auth import auth_bp
from app.routes.procurement import procurement_bp
from app.routes.finance import finance_bp
from app.routes.vendors import vendors_bp


login_manager = LoginManager()
login_manager.login_view = "auth.login"


def create_app():
    app = Flask(__name__)

    # 🔴 THIS IS THE CRITICAL LINE YOU WERE MISSING
    app.config.from_object(Config)

    # SAFETY CHECK (PREVENTS SILENT FAILURE)
    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        raise RuntimeError("SQLALCHEMY_DATABASE_URI is NOT SET")

    db.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(procurement_bp, url_prefix="/procurement")
    app.register_blueprint(finance_bp, url_prefix="/finance")
    app.register_blueprint(vendors_bp, url_prefix="/vendors")

    return app
