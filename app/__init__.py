from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"


def create_app():
    app = Flask(__name__)

    # --- BASIC CONFIG ---
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

    database_url = os.getenv("SQLALCHEMY_DATABASE_URI")
    if not database_url:
        raise RuntimeError("SQLALCHEMY_DATABASE_URI is not set in environment variables")

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # --- INIT EXTENSIONS ---
    db.init_app(app)
    login_manager.init_app(app)
    Migrate(app, db)

    # --- USER LOADER (THIS FIXES YOUR ERROR) ---
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # --- REGISTER BLUEPRINTS ---
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
