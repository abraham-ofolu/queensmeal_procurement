from flask import Flask
from app.extensions import db
from app.config import Config

# Blueprints
from app.routes.auth import auth_bp
from app.routes.procurement import procurement_bp
from app.routes.vendors import vendors_bp
from app.routes.director import director_bp
from app.routes.finance import finance_bp
from app.routes.audit import audit_bp


def create_app():
    app = Flask(__name__)

    # ✅ LOAD CONFIG FIRST (THIS WAS MISSING)
    app.config.from_object(Config)

    # 🔴 HARD FAIL if DB URI missing (prevents silent loops)
    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        raise RuntimeError("SQLALCHEMY_DATABASE_URI is NOT loaded into Flask config")

    # Init DB AFTER config
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(procurement_bp)
    app.register_blueprint(vendors_bp)
    app.register_blueprint(director_bp)
    app.register_blueprint(finance_bp)
    app.register_blueprint(audit_bp)

    # Init audit safely (never blocks boot)
    try:
        from app.audit import init_audit
        init_audit(app)
    except Exception as e:
        app.logger.warning(f"AUDIT DISABLED: {e}")

    return app
