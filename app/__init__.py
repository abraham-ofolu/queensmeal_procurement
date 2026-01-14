import os
from flask import Flask
from app.extensions import db, migrate, login_manager
from app.models import *  # noqa

def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-key")

    # 🔴 THIS IS THE CRITICAL LINE
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if not app.config["SQLALCHEMY_DATABASE_URI"]:
        raise RuntimeError("DATABASE_URL is not set")

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.procurement import procurement_bp
    from app.routes.director import director_bp
    from app.routes.finance import finance_bp
    from app.routes.vendors import vendors_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(procurement_bp, url_prefix="/procurement")
    app.register_blueprint(director_bp, url_prefix="/director")
    app.register_blueprint(finance_bp, url_prefix="/finance")
    app.register_blueprint(vendors_bp, url_prefix="/vendors")

    return app
