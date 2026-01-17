from flask import Flask
from flask_login import LoginManager

from app.extensions import db
from app.config import Config

# Blueprints
from app.routes.auth import auth_bp
from app.routes.procurement import procurement_bp
from app.routes.vendors import vendors_bp
from app.routes.director import director_bp
from app.routes.finance import finance_bp
from app.routes.audit import audit_bp
from app.routes.users import (users_bp)


def create_app():
    app = Flask(__name__)

    # ✅ Load config FIRST
    app.config.from_object(Config)

    # Safety check
    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        raise RuntimeError("SQLALCHEMY_DATABASE_URI is missing")

    # ✅ Init DB
    db.init_app(app)

    # ✅ INIT LOGIN MANAGER (THIS WAS MISSING)
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    # User loader
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    app.register_blueprint(users_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(procurement_bp)
    app.register_blueprint(vendors_bp)
    app.register_blueprint(director_bp)
    app.register_blueprint(finance_bp)
    app.register_blueprint(audit_bp)

    # Init audit (safe, never fatal)
    try:
        from app.audit import init_audit
        init_audit(app)
    except Exception as e:
        app.logger.warning(f"AUDIT DISABLED: {e}")

    return app
