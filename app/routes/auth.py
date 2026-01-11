# app/routes/auth.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.routing import BuildError

from app.models.user import User

auth_bp = Blueprint("auth", __name__)


def safe_redirect(endpoint, fallback_path="/"):
    try:
        return redirect(url_for(endpoint))
    except BuildError:
        return redirect(fallback_path)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        # Already logged in — send based on role
        role = getattr(current_user, "role", "")
        if role == "finance":
            return safe_redirect("finance.payments", "/finance/payments")
        if role == "director":
            return safe_redirect("procurement.index", "/procurement/")
        return safe_redirect("procurement.index", "/procurement/")

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)

            role = user.role
            if role == "finance":
                return safe_redirect("finance.payments", "/finance/payments")
            if role == "director":
                return safe_redirect("procurement.index", "/procurement/")
            return safe_redirect("procurement.index", "/procurement/")

        flash("Invalid username or password", "danger")
        return render_template("login.html"), 200

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
