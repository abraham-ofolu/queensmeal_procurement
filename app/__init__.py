from flask import Flask
from app.extensions import db, login_manager
from werkzeug.security import generate_password_hash

def create_app():
    app = Flask(__name__)

    app.config.from_object("app.config.Config")

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.procurement import procurement_bp
    from app.routes.finance import finance_bp
    from app.routes.vendors import vendors_bp
    from app.routes.reports import reports_bp
    from app.routes.users import users_bp
    from app.routes.audit import audit_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(procurement_bp, url_prefix="/procurement")
    app.register_blueprint(finance_bp, url_prefix="/finance")
    app.register_blueprint(vendors_bp, url_prefix="/vendors")
    app.register_blueprint(reports_bp, url_prefix="/reports")
    app.register_blueprint(users_bp, url_prefix="/users")
    app.register_blueprint(audit_bp, url_prefix="/audit")

    # 🔑 AUTO-SEED DIRECTOR (RUNS ONCE)
    with app.app_context():
        from app.models.user import User

        if not User.query.filter_by(username="director").first():
            director = User(
                username="director",
                role="director",
                password_hash=generate_password_hash("director123")
            )
            db.session.add(director)
            db.session.commit()
            print("✅ Director user auto-created")

    return app
