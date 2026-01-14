from flask import Flask
from app.extensions import db, migrate, login_manager
from app.models.user import User


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = app.config.get("SECRET_KEY", "change-this")
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config.get(
        "SQLALCHEMY_DATABASE_URI"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # ✅ THIS IS THE MISSING PIECE
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Blueprints
    from app.routes.auth import auth_bp
    from app.routes.procurement import procurement_bp
    from app.routes.director import director_bp
    from app.routes.finance import finance_bp
    from app.routes.vendors import vendors_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(procurement_bp)
    app.register_blueprint(director_bp)
    app.register_blueprint(finance_bp)
    app.register_blueprint(vendors_bp)

    return app
