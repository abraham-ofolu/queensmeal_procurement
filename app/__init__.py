from flask import Flask
from flask_login import LoginManager
from app.extensions import db, mail
from app.models.user import User

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    # Init extensions
    db.init_app(app)
    mail.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dash_bp
    from app.routes.vendors import vendors_bp
    from app.routes.procurement import procurement_bp
    from app.routes.reports import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dash_bp)
    app.register_blueprint(vendors_bp)
    app.register_blueprint(procurement_bp)
    app.register_blueprint(reports_bp)

    # Create DB tables
    with app.app_context():
        db.create_all()

    return app
