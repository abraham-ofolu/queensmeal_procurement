import os
from flask import Flask, redirect, url_for
from flask_login import LoginManager
from dotenv import load_dotenv

from app.extensions import db, migrate
from app.models.user import User

load_dotenv()

login_manager = LoginManager()
login_manager.login_view = "auth.login"


def _normalize_pg_url(url: str) -> str:
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL is not set")
    app.config["SQLALCHEMY_DATABASE_URI"] = _normalize_pg_url(db_url)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Blueprints
    from app.routes.auth import auth_bp
    from app.routes.procurement import procurement_bp
    from app.routes.vendors import vendors_bp
    from app.routes.finance import finance_bp
    from app.routes.director import director_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(procurement_bp)
    app.register_blueprint(vendors_bp)
    app.register_blueprint(finance_bp)
    app.register_blueprint(director_bp)

    @app.route("/")
    def home():
        return redirect(url_for("procurement.index"))

    with app.app_context():
        if os.getenv("AUTO_CREATE_TABLE", "1") == "1":
            db.create_all()
            _seed_default_users()

    return app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def _seed_default_users():
    from werkzeug.security import generate_password_hash

    users = [
        ("procurement", "procurement", "procurement123"),
        ("director", "director", "director123"),
        ("finance", "finance", "finance123"),
    ]

    for username, role, pwd in users:
        u = User.query.filter_by(username=username).first()
        if not u:
            u = User(username=username, role=role)
            if hasattr(u, "password_hash"):
                u.password_hash = generate_password_hash(pwd)
            else:
                u.password = generate_password_hash(pwd)
            db.session.add(u)

    db.session.commit()
