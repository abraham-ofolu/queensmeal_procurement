from flask import Flask
from flask_login import LoginManager

from app.extensions import db
from app.models import User
from app.utils.cloudinary import init_cloudinary

# Blueprints
from app.routes.auth import auth_bp
from app.routes.procurement import procurement_bp
from app.routes.vendors import vendors_bp
from app.routes.finance import finance_bp
from app.routes.reports import reports_bp
from app.routes.finance import finance_bp
from app.utils.cloudinary import init_cloudinary

login_manager = LoginManager()
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def create_app():
    app = Flask(__name__)
    ...
    init_cloudinary(app)

    # =========================
    # CONFIG
    # =========================
    app.config.from_object("config.Config")

    # =========================
    # EXTENSIONS
    # =========================
    db.init_app(app)
    login_manager.init_app(app)

    # =========================
    # CLOUDINARY
    # =========================
    init_cloudinary(app)

    # =========================
    # BLUEPRINTS
    # =========================
    app.register_blueprint(auth_bp)
    app.register_blueprint(procurement_bp, url_prefix="/procurement")
    app.register_blueprint(vendors_bp, url_prefix="/vendors")
    app.register_blueprint(finance_bp, url_prefix="/finance")
    app.register_blueprint(reports_bp, url_prefix="/reports")

    return app
