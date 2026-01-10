import os
from flask import Flask
from flask_login import LoginManager
from app.extensions import db
from app.models.user import User

def create_app():
    app = Flask(__name__)

    # ✅ READ DATABASE FROM RENDER ENV
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")

    # Render uses postgres://, SQLAlchemy wants postgresql://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://", "postgresql://", 1
        )

    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret"),
        SQLALCHEMY_DATABASE_URI=database_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    # =====================
    # EXTENSIONS
    # =====================
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    # ✅ REQUIRED FOR FLASK-LOGIN (THIS FIXES LOGIN CRASH)
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # =====================
    # BLUEPRINTS
    # =====================
    from app.routes.auth import auth_bp
    from app.routes.procurement import procurement_bp
    from app.routes.vendors import vendors_bp
    from app.routes.finance import finance_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(procurement_bp)
    app.register_blueprint(vendors_bp)
    app.register_blueprint(finance_bp)

    return app
