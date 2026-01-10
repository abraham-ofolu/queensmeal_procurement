from flask import Flask
from flask_login import LoginManager
from app.extensions import db
from app.models.user import User

def create_app():
    app = Flask(__name__)

    app.config.from_mapping(
        SECRET_KEY="dev-secret",
        SQLALCHEMY_DATABASE_URI=app.config.get("SQLALCHEMY_DATABASE_URI"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    db.init_app(app)

    # ✅ LOGIN MANAGER (THIS WAS MISSING / BROKEN)
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ✅ BLUEPRINTS
    from app.routes.auth import auth_bp
    from app.routes.procurement import procurement_bp
    from app.routes.vendors import vendors_bp
    from app.routes.finance import finance_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(procurement_bp)
    app.register_blueprint(vendors_bp)
    app.register_blueprint(finance_bp)

    return app
