from flask import Flask
from flask_login import LoginManager
from app.extensions import db
from app.models.user import User

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")
    login_manager.init_app(app)


    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

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

    return app
