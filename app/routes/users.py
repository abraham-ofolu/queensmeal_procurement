from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app.extensions import db
from app.models.user import User

users_bp = Blueprint("users", __name__, url_prefix="/director/users")


def is_director():
    return getattr(current_user, "role", "").lower() == "director"


@users_bp.route("/")
@login_required
def index():
    if not is_director():
        flash("Access denied.", "danger")
        return redirect(url_for("procurement.index"))

    # User model does NOT have created_at — use id safely
    users = User.query.order_by(User.id.desc()).all()
    return render_template("users/index.html", users=users)


@users_bp.route("/delete/<int:user_id>", methods=["POST"])
@login_required
def delete_user(user_id):
    if not is_director():
        flash("Access denied.", "danger")
        return redirect(url_for("procurement.index"))

    user = User.query.get_or_404(user_id)

    if user.role.lower() == "director":
        flash("You cannot delete the Director account.", "danger")
        return redirect(url_for("users.index"))

    db.session.delete(user)
    db.session.commit()

    flash("User deleted successfully.", "success")
    return redirect(url_for("users.index"))
