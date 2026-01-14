from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from flask_login import LoginManager

# ✅ THIS WAS MISSING
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("procurement.index"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("procurement.index"))

        flash("Invalid username or password", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@auth_bp.route("/_fix_procurement_user")
def fix_procurement_user():
    from werkzeug.security import generate_password_hash
    from app.models.user import User
    from app.extensions import db

    user = User.query.filter_by(username="procurement").first()

    if not user:
        user = User(
            username="procurement",
            role="procurement",
            password_hash=generate_password_hash("procurement123")
        )
        db.session.add(user)
    else:
        user.password_hash = generate_password_hash("procurement123")

    db.session.commit()
    return "Procurement user fixed"
