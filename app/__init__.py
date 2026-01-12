import os
from flask import Flask
from flask_login import LoginManager
from app.extensions import db
from app.models.user import User


def create_app():
    app = Flask(__name__)

    # -------------------
    # CONFIG
    # -------------------
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL"
    ).replace("postgres://", "postgresql://")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # -------------------
    # INIT EXTENSIONS
    # -------------------
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    def create_app():
    app = Flask(__name__)

    # -------------------
    # USER LOADER (THIS IS WHAT WAS MISSING)
    # -------------------
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # -------------------
    # BLUEPRINTS
    # -------------------
    from app.routes.auth import auth_bp
    from app.routes.procurement import procurement_bp
    from app.routes.vendors import vendors_bp
    from app.routes.finance import finance_bp
    from app.routes.director import director_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(director_bp)
    app.register_blueprint(procurement_bp, url_prefix="/procurement")
    app.register_blueprint(vendors_bp, url_prefix="/vendors")
    app.register_blueprint(finance_bp, url_prefix="/finance")

    with app.app_context():
        if os.environ.get("AUTO_CREATE_TABLE") == "1":
            db.create_all()

    return app
