import os
from flask import Flask

from app.extensions import db, login_manager
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure upload folder exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # INIT EXTENSIONS
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # REGISTER BLUEPRINTS
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.vendors import vendors_bp
    from app.routes.procurement import procurement_bp
    from app.routes.finance import finance_bp
    from app.routes.reports import reports_bp
    from app.routes.users import users_bp
    from app.routes.audit import audit_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(vendors_bp)
    app.register_blueprint(procurement_bp)
    app.register_blueprint(finance_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(audit_bp)

    # USER LOADER
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
