from flask import Blueprint, render_template, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # If already logged in, show dashboard directly
    if current_user.is_authenticated:
        return render_template(
            "dashboard/home.html",
            user=current_user
        )

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)

            # 🔒 DO NOT REDIRECT — render dashboard directly
            return render_template(
                "dashboard/home.html",
                user=user
            )

        flash("Invalid username or password", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return render_template("auth/login.html")
