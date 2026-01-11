from flask import Flask
from flask_login import LoginManager
from app.extensions import db, migrate
from app.models.user import User


login_manager = LoginManager()
login_manager.login_view = "auth.login"


def create_app():
    app = Flask(__name__)

    # ================= CONFIG =================
    app.config["SECRET_KEY"] = "change-this-secret"
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "postgresql+psycopg2://"
        + app.config.get("DATABASE_URL", "")
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # ================= INIT =================
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # ================= USER LOADER =================
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ================= BLUEPRINTS =================
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

    # ================= ROOT =================
    @app.route("/")
    def index():
        return "Queensmeal Procurement System – Live"

    return app
