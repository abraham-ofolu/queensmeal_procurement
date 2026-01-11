from flask import Flask
from app.extensions import db, login_manager
from app.models.user import User
import os


def create_app():
    app = Flask(__name__)

    # --------------------
    # CONFIG
    # --------------------
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret")

    database_url = os.environ.get("DATABASE_URL")
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://")

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # --------------------
    # INIT EXTENSIONS
    # --------------------
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # --------------------
    # BLUEPRINTS
    # --------------------
    from app.routes.auth import auth_bp
    from app.routes.procurement import procurement_bp
    from app.routes.vendors import vendors_bp
    from app.routes.finance import finance_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(procurement_bp)
    app.register_blueprint(vendors_bp)
    app.register_blueprint(finance_bp)

    # --------------------
    # CREATE TABLES
    # --------------------
    with app.app_context():
        db.create_all()

    return app
