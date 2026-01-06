from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.utils.cloudinary import init_cloudinary
import os

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Cloudinary config
    app.config["CLOUDINARY_CLOUD_NAME"] = os.environ.get("CLOUDINARY_CLOUD_NAME")
    app.config["CLOUDINARY_API_KEY"] = os.environ.get("CLOUDINARY_API_KEY")
    app.config["CLOUDINARY_API_SECRET"] = os.environ.get("CLOUDINARY_API_SECRET")

    db.init_app(app)
    login_manager.init_app(app)
    init_cloudinary(app)

    from app.routes.auth import auth_bp
    from app.routes.procurement import procurement_bp
    from app.routes.vendors import vendors_bp
    from app.routes.finance import finance_bp
    from app.routes.reports import reports_bp
    from app.routes.audit import audit_bp
    from app.utils.cloudinary import init_cloudinary

    app.register_blueprint(auth_bp)
    app.register_blueprint(procurement_bp)
    app.register_blueprint(vendors_bp)
    app.register_blueprint(finance_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(audit_bp)
    

    return app
