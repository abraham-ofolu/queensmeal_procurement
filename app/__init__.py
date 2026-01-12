from flask_login import LoginManager
from app.models.user import User

login_manager = LoginManager()
login_manager.login_view = "auth.login"

def create_app():
    app = Flask(__name__)

    # config
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # register blueprints BELOW this
    from app.routes.auth import auth_bp
    from app.routes.procurement import procurement_bp
    from app.routes.finance import finance_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(procurement_bp, url_prefix="/procurement")
    app.register_blueprint(finance_bp, url_prefix="/finance")

    return app
