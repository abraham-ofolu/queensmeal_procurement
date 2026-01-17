from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app.models.user import User
from app.extensions import db

users_bp = Blueprint("users", __name__, url_prefix="/director/users")


def is_director():
    return getattr(current_user, "role", "").lower() == "director"


@users_bp.route("/")
@login_required
def index():
    if not is_director():
        flash("Access denied.", "danger")
        return redirect(url_for("procurement.index"))

    # ✅ SAFE: User model does NOT have created_at
    users = User.query.order_by(User.id.desc()).all()
    return render_template("users/index.html", users=users)


@users_bp.route("/delete/<int:user_id>", methods=["
