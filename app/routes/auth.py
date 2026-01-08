from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.models.user import User

auth_bp = Blueprint("auth", __name__)

def verify_password(user, input_password):
    """
    Free-render-safe password check.
    Adapts to existing DB schema without migrations.
    """

    # Case 1: hashed password column
    if hasattr(user, "password_hash") and user.password_hash:
        return user.password_hash == input_password

    # Case 2: plain password column
    if hasattr(user, "password_plain") and user.password_plain:
        return user.password_plain == input_password

    # Case 3: legacy text password
    if hasattr(user, "password_text") and user.password_text:
        return user.password_text == input_password

    # Case 4: last-resort fallback (no crash)
    return False


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and verify_password(user, password):
            login_user(user)
            return redirect(url_for("finance.list_payments"))

        flash("Invalid username or password", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
