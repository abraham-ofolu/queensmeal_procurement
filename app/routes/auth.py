from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required

from ..models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip().lower()
        password = request.form.get("password") or ""

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            next_url = request.args.get("next")
            return redirect(next_url or url_for("auth.after_login"))

        flash("Invalid username or password", "danger")
        return redirect(url_for("auth.login"))

    return render_template("login.html")


@auth_bp.route("/after-login")
@login_required
def after_login():
    # Keep it simple: send everyone to finance payments for now
    # (you can change to role-based routing later)
    return redirect("/finance/payments")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
