from flask import Flask, redirect, url_for
from .extensions import db, login_manager
from .models import User
from config import Config


def _ensure_default_users():
    defaults = [
        ("director", "director"),
        ("procurement", "procurement"),
        ("finance", "finance"),
        ("audit", "audit"),
    ]

    for username, role in defaults:
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(username=username, role=role)
            user.set_password(username)
            db.session.add(user)

    db.session.commit()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    # 🔹 ROOT ROUTE FIX (THIS IS WHAT WAS MISSING)
    @app.route("/")
    def index():
        return redirect(url_for("auth.login"))

    # Blueprints
    from .routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    # Create tables + seed users
    with app.app_context():
        db.create_all()
        _ensure_default_users()

    return app
