from flask import Flask
from .extensions import db, login_manager
from .models import User
from config import Config


def _ensure_default_users():
    """
    Creates default users if they don't exist.
    Default passwords = same as username (change later).
    """
    defaults = [
        ("director", "director"),
        ("procurement", "procurement"),
        ("finance", "finance"),
        ("audit", "audit"),
    ]

    for username, role in defaults:
        u = User.query.filter_by(username=username).first()
        if not u:
            u = User(username=username, role=role)
            u.set_password(username)  # password = username
            db.session.add(u)
    db.session.commit()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints (keep your existing structure)
    from .routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    # IMPORTANT: create tables on boot (fixes "no such table: users")
    with app.app_context():
        db.create_all()
        _ensure_default_users()

    return app
