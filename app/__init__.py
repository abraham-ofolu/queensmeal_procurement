from flask import Flask
from app.extensions import db, login_manager
from app.models.user import User
from app.routes.auth import auth_bp
from app.routes.procurement import procurement_bp
from app.routes.finance import finance_bp
from app.routes.vendors import vendors_bp
from app.routes.reports import reports_bp
import os

def create_app():
    app = Flask(__name__)

   

    RESET_DB = os.getenv("RESET_DB", "False").lower() == "true"
    if RESET_DB:
        with app.app_context():
            db.drop_all()
            db.create_all()

    app.config["SECRET_KEY"] = "super-secret-key"
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config.get(
        "DATABASE_URL",
        "sqlite:///app.db"
    ).replace("postgres://", "postgresql://")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    app.register_blueprint(auth_bp)
    app.register_blueprint(procurement_bp, url_prefix="/procurement")
    app.register_blueprint(finance_bp, url_prefix="/finance")
    app.register_blueprint(vendors_bp, url_prefix="/vendors")
    app.register_blueprint(reports_bp, url_prefix="/reports")

    with app.app_context():
        db.create_all()
        _ensure_default_users()

    return app


def _ensure_default_users():
    users = {
        "procurement": "procurement123",
        "finance": "finance123",
        "director": "director123",
        "audit": "audit123",
    }

    for username, password in users.items():
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(username=username)
            db.session.add(user)

        user.password_hash = password  # simple & stable for now

    db.session.commit()
