from __future__ import annotations

from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models.user import User


users_bp = Blueprint("users", __name__, url_prefix="/director/users")


def _role() -> str:
    return (getattr(current_user, "role", "") or "").lower()


def _require_director():
    if _role() != "director":
        flash("You are not allowed to access that page.", "danger")
        return False
    return True


def _get_active_field_name(user: User) -> str | None:
    """
    Supports different user models without breaking:
    - is_active
    - active
    - is_enabled
    - enabled
    """
    for field in ("is_active", "active", "is_enabled", "enabled"):
        if hasattr(user, field):
            return field
    return None


def _is_user_active(user: User) -> bool:
    field = _get_active_field_name(user)
    if not field:
        # If your model doesn't have an active flag, assume active.
        return True
    return bool(getattr(user, field))


def _set_user_active(user: User, value: bool) -> None:
    field = _get_active_field_name(user)
    if not field:
        return
    setattr(user, field, bool(value))


@users_bp.route("/", methods=["GET"])
@login_required
def index():
    if not _require_director():
        return redirect(url_for("procurement.index"))

    users = User.query.order_by(User.id.asc()).all()
    return render_template("director/users/index.html", users=users, is_user_active=_is_user_active)


@users_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if not _require_director():
        return redirect(url_for("procurement.index"))

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = (request.form.get("password") or "").strip()
        role = (request.form.get("role") or "").strip().lower()

        allowed_roles = {"procurement", "finance", "audit", "director"}

        if not username or not password or role not in allowed_roles:
            flash("Username, Password, and a valid Role are required.", "danger")
            return redirect(url_for("users.create"))

        existing = User.query.filter_by(username=username).first()
        if existing:
            flash("That username already exists. Choose another.", "danger")
            return redirect(url_for("users.create"))

        try:
            new_user = User(
                username=username,
                role=role,
            )

            # Password hashing (must match your login check_password_hash)
            if hasattr(new_user, "password_hash"):
                new_user.password_hash = generate_password_hash(password)
            elif hasattr(new_user, "password"):
                # fallback if your model uses password field (not recommended, but supported)
                new_user.password = generate_password_hash(password)
            else:
                flash("User model is missing password_hash/password field.", "danger")
                return redirect(url_for("users.create"))

            # Enable user (if model supports it)
            _set_user_active(new_user, True)

            # Optional timestamps if your model has them
            if hasattr(new_user, "created_at") and getattr(new_user, "created_at") is None:
                new_user.created_at = datetime.utcnow()

            db.session.add(new_user)
            db.session.commit()

            flash(f"User '{username}' created successfully.", "success")
            return redirect(url_for("users.index"))
        except Exception as e:
            db.session.rollback()
            flash(f"Could not create user: {e}", "danger")
            return redirect(url_for("users.create"))

    return render_template("director/users/create.html")


@users_bp.route("/<int:user_id>/toggle", methods=["POST"])
@login_required
def toggle(user_id: int):
    if not _require_director():
        return redirect(url_for("procurement.index"))

    user = User.query.get_or_404(user_id)

    # Prevent director locking themselves out
    if getattr(current_user, "id", None) == user.id:
        flash("You cannot disable your own account.", "danger")
        return redirect(url_for("users.index"))

    try:
        current_state = _is_user_active(user)
        _set_user_active(user, not current_state)
        db.session.commit()

        if _is_user_active(user):
            flash(f"User '{user.username}' is now ACTIVE.", "success")
        else:
            flash(f"User '{user.username}' has been DISABLED.", "warning")

    except Exception as e:
        db.session.rollback()
        flash(f"Could not update user status: {e}", "danger")

    return redirect(url_for("users.index"))
