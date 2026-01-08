from flask import Flask
from flask_login import LoginManager
from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models.user import User


login_manager = LoginManager()
login_manager.login_view = "auth.login"


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = "change-this-secret"
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///app.db" if app.config.get("ENV") != "production"
        else app.config.get("DATABASE_URL")
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)

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

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()

        # ---- CREATE DEFAULT USERS (ONLY IF MISSING) ----
        if not User.query.first():
            users = [
                User(
                    username="procurement",
                    password_hash=generate_password_hash("procurement123"),
                    role="procurement",
                ),
                User(
                    username="finance",
                    password_hash=generate_password_hash("finance123"),
                    role="finance",
                ),
                User(
                    username="director",
                    password_hash=generate_password_hash("director123"),
                    role="director",
                ),
                User(
                    username="audit",
                    password_hash=generate_password_hash("audit123"),
                    role="audit",
                ),
            ]
            db.session.add_all(users)
            db.session.commit()

    return app
