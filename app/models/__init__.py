import os
from app.extensions import db

from app.models.user import User
from app.models.vendor import Vendor
from app.models.procurement import ProcurementRequest
from app.models.audit_log import AuditLog

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs("instance", exist_ok=True)
    os.makedirs("uploads/vendors", exist_ok=True)
    os.makedirs("uploads/requests", exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.dashboard import dash_bp
    from app.routes.procurement import procurement_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dash_bp)
    app.register_blueprint(procurement_bp, url_prefix="/procurement")

    with app.app_context():
        db.create_all()
        from app.models.user import User
        if not User.query.filter_by(username="director").first():
            u = User(username="director", role="director")
            u.set_password("director123")
            db.session.add(u)
            db.session.commit()

    return app
