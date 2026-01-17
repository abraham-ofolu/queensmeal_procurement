from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models.user import User

users_bp = Blueprint("users", __name__, url_prefix="/director/users")


def _is_director():
    return getattr(current_user, "role", "") == "director"


@users_bp.before_request
@login_required
def restrict_to_director():
    if not _is_director():
        flash("Director access only.", "danger")
        return redirect(url_for("procurement.index"))


@users_bp.route("/")
def index():
    users = User.query.order_by(User.id.desc()).all()
    return render_template("users/index.html", users=users)


@users_bp.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        role = request.form.get("role")

        if not username or not password or not role:
            flash("All fields are required.", "danger")
            return redirect(url_for("users.create"))

        if role not in ["procurement", "finance", "audit", "director"]:
            flash("Invalid role.", "danger")
            return redirect(url_for("users.create"))

        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "danger")
            return redirect(url_for("users.create"))

        user = User(
            username=username,
            role=role,
            password_hash=generate_password_hash(password),
            is_active=True,
        )

        db.session.add(user)
        db.session.commit()

        flash("User created successfully.", "success")
        return redirect(url_for("users.index"))

    return render_template("users/create.html")


@users_bp.route("/toggle/<int:user_id>", methods=["POST"])
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)

    if user.username == current_user.username:
        flash("You cannot disable yourself.", "danger")
        return redirect(url_for("users.index"))

    user.is_active = not user.is_active
    db.session.commit()

    flash("User status updated.", "success")
    return redirect(url_for("users.index"))


@users_bp.route("/delete/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    if user.username == current_user.username:
        flash("You cannot delete yourself.", "danger")
        return redirect(url_for("users.index"))

    db.session.delete(user)
    db.session.commit()

    flash("User deleted.", "success")
    return redirect(url_for("users.index"))
