import os
from flask import Flask
from app.extensions import db, login_manager

def create_app():
    app = Flask(__name__)

    # Config
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///app.db").replace(
        "postgres://", "postgresql://"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # Import models so SQLAlchemy sees them
    from app.models.user import User  # noqa
    from app.models.procurement_request import ProcurementRequest  # noqa
    from app.models.payment import Payment  # noqa

    # Register routes (blueprints)
    from app.routes.auth import auth_bp
    from app.routes.procurement import procurement_bp
    from app.routes.finance import finance_bp
    from app.routes.vendors import vendors_bp
    from app.routes.director import director_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(procurement_bp)
    app.register_blueprint(finance_bp)
    app.register_blueprint(vendors_bp)
    app.register_blueprint(director_bp)

    # Create tables
    with app.app_context():
        db.create_all()

        # Optional: seed users if they don't exist (only if your User model has username/password_hash/role)
        # If you already seeded users elsewhere, leave this as-is.
        try:
            if not User.query.filter_by(username="procurement").first():
                u = User(username="procurement", role="procurement")
                u.set_password("procurement123")
                db.session.add(u)

            if not User.query.filter_by(username="director").first():
                u = User(username="director", role="director")
                u.set_password("director123")
                db.session.add(u)

            if not User.query.filter_by(username="finance").first():
                u = User(username="finance", role="finance")
                u.set_password("finance123")
                u.set_password("finance123")
                db.session.add(u)

            db.session.commit()
        except Exception:
            # If your User model fields differ, you can remove the seeding.
            db.session.rollback()

    return app
