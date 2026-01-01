from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user

from app.extensions import db
from app.models.user import User

users_bp = Blueprint("users", __name__, url_prefix="/users")


@users_bp.route("/")
@login_required
def list_users():
    if current_user.role != "director":
        flash("Access denied", "danger")
        return redirect(url_for("dashboard.home"))

    users = User.query.order_by(User.id.asc()).all()
    return render_template("users/list.html", users=users)


@users_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_user():
    if current_user.role != "director":
        flash("Access denied", "danger")
        return redirect(url_for("dashboard.home"))

    if request.method == "POST":
        username = request.form["username"]
        role = request.form["role"]
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            flash("Username already exists", "warning")
            return redirect(url_for("users.create_user"))

        user = User(username=username, role=role)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash("User created successfully", "success")
        return redirect(url_for("users.list_users"))

    return render_template("users/create.html")
