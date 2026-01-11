from flask import Flask
from flask_login import LoginManager
from app.extensions import db
from app.models.user import User

# Blueprints
from app.routes.auth import auth_bp
from app.routes.procurement import procurement_bp
from app.routes.finance import finance_bp
from app.routes.vendors import vendors_bp


login_manager = LoginManager()
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def create_app():
    app = Flask(__name__)

    # 🔐 CONFIG
    app.config["SECRET_KEY"] = "change-this-in-production"

    # DATABASE
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config.get(
        "SQLALCHEMY_DATABASE_URI"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # INIT EXTENSIONS
    db.init_app(app)
    login_manager.init_app(app)

    # REGISTER BLUEPRINTS
    app.register_blueprint(auth_bp)
    app.register_blueprint(procurement_bp, url_prefix="/procurement")
    app.register_blueprint(finance_bp, url_prefix="/finance")
    app.register_blueprint(vendors_bp, url_prefix="/vendors")

    return app
