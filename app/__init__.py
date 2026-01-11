import os
from flask import Flask
from .extensions import db, login_manager

def _normalize_db_url(url: str) -> str:
    # Render sometimes gives postgres:// which SQLAlchemy wants as postgresql://
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # --- Core config ---
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")

    db_url = os.getenv("SQLALCHEMY_DATABASE_URI") or os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL or SQLALCHEMY_DATABASE_URI must be set.")
    app.config["SQLALCHEMY_DATABASE_URI"] = _normalize_db_url(db_url)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Upload root (use Render Disk if available)
    upload_root = os.getenv("UPLOAD_ROOT") or os.path.join(app.instance_path, "uploads")
    app.config["UPLOAD_ROOT"] = upload_root
    app.config["QUOTATIONS_FOLDER"] = os.path.join(upload_root, "quotations")
    app.config["RECEIPTS_FOLDER"] = os.path.join(upload_root, "receipts")

    # Ensure instance path exists
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["QUOTATIONS_FOLDER"], exist_ok=True)
    os.makedirs(app.config["RECEIPTS_FOLDER"], exist_ok=True)

    # --- Init extensions ---
    db.init_app(app)
    login_manager.init_app(app)

    # --- Import models so SQLAlchemy sees them ---
    from .models.user import User  # noqa: F401
    from .models.procurement_request import ProcurementRequest  # noqa: F401
    from .models.procurement_quotation import ProcurementQuotation  # noqa: F401
    from .models.payment import Payment  # noqa: F401

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # --- Blueprints ---
    from .routes.auth import auth_bp
    from .routes.procurement import procurement_bp
    from .routes.vendors import vendors_bp
    from .routes.finance import finance_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(procurement_bp, url_prefix="/procurement")
    app.register_blueprint(vendors_bp, url_prefix="/vendors")
    app.register_blueprint(finance_bp, url_prefix="/finance")

    # --- One-time DB bootstrap (Option A fix) ---
    # This recreates missing tables (like payments) without dropping others.
    if os.getenv("AUTO_CREATE_TABLES") == "1":
        with app.app_context():
            db.create_all()

    return app
