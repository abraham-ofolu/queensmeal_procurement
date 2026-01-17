from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models.user import User

users_bp = Blueprint("users", __name__, url_prefix="/director/users")


def director_only():
    return getattr(current_user, "role", "").lower() == "director"


@users_bp.before_request
@login_required
def restrict_to_director():
    if not director_only():
        flash("Access denied.", "danger")
        return redirect(url_for("procurement.index"))


@users_bp.route("/")
def index():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("users/index.html", users=users)


@users_bp.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        role = request.form.get("role", "").strip().lower()

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
            password_hash=generate_password_hash(password),
            role=role,
            is_active=True
        )

        db.session.add(user)
        db.session.commit()

        flash("User created successfully.", "success")
        return redirect(url_for("users.index"))

    return render_template("users/create.html")


@users_bp.route("/<int:user_id>/disable", methods=["POST"])
def disable(user_id):
    user = User.query.get_or_404(user_id)

    if user.role == "director":
        flash("You cannot disable a Director account.", "danger")
        return redirect(url_for("users.index"))

    user.is_active = False
    db.session.commit()

    flash("User disabled.", "success")
    return redirect(url_for("users.index"))
