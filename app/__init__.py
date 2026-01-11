from flask import Flask
from flask_login import LoginManager
from app.extensions import db
from app.models.user import User


def create_app():
    app = Flask(__name__)

    # =========================
    # Core Config
    # =========================
    app.config["SECRET_KEY"] = app.config.get("SECRET_KEY", "change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config.get("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # =========================
    # Extensions
    # =========================
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    # =========================
    # 🔑 THIS IS THE MISSING PIECE
    # =========================
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # =========================
    # Blueprints
    # =========================
    from app.routes.auth import auth_bp
    from app.routes.procurement import procurement_bp
    from app.routes.vendors import vendors_bp
    from app.routes.finance import finance_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(procurement_bp, url_prefix="/procurement")
    app.register_blueprint(vendors_bp, url_prefix="/vendors")
    app.register_blueprint(finance_bp, url_prefix="/finance")

    return app
