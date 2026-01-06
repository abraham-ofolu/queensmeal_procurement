from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.utils.cloudinary import init_cloudinary

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    app.config.from_object("config.Config")

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    init_cloudinary(app)

    from app.routes.auth import auth_bp
    from app.routes.procurement import procurement_bp
    from app.routes.finance import finance_bp
    from app.routes.vendors import vendors_bp
    from app.routes.reports import reports_bp
    from app.routes.audit import audit_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(procurement_bp)
    app.register_blueprint(finance_bp)
    app.register_blueprint(vendors_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(audit_bp)

    return app
