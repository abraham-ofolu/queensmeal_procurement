import os
from flask import Flask

from app.extensions import db, login_manager

def create_app():
    app = Flask(__name__)

    # -----------------------
    # CONFIG
    # -----------------------
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")

    database_url = os.getenv("SQLALCHEMY_DATABASE_URI")
    if not database_url:
        raise RuntimeError("SQLALCHEMY_DATABASE_URI is not set")

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # -----------------------
    # INIT EXTENSIONS
    # -----------------------
    db.init_app(app)
    login_manager.init_app(app)

    # -----------------------
    # USER LOADER (CRITICAL)
    # -----------------------
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # -----------------------
    # BLUEPRINTS
    # -----------------------
    from app.routes.auth import auth_bp
    from app.routes.procurement import procurement_bp
    from app.routes.vendors import vendors_bp
    from app.routes.finance import finance_bp
    from app.routes.reports import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(procurement_bp)
    app.register_blueprint(vendors_bp)
    app.register_blueprint(finance_bp)
    app.register_blueprint(reports_bp)

    return app
