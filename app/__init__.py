from flask import Flask
from app.extensions import db

# Blueprints
from app.routes.auth import auth_bp
from app.routes.procurement import procurement_bp
from app.routes.vendors import vendors_bp
from app.routes.director import director_bp
from app.routes.finance import finance_bp
from app.routes.audit import audit_bp

from app.audit import init_audit


def create_app():
    app = Flask(__name__)

    # Basic config
    app.config["SECRET_KEY"] = app.config.get("SECRET_KEY") or "change-me"
    # SQLALCHEMY_DATABASE_URI should already be coming from env/config in your project:
    # do NOT hardcode it here if you already set it in Render environment variables.

    # Init db
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(procurement_bp)
    app.register_blueprint(vendors_bp)
    app.register_blueprint(director_bp)
    app.register_blueprint(finance_bp)
    app.register_blueprint(audit_bp)

    # Init audit trail (captures actor + listens for model changes)
    init_audit(app)

    return app
