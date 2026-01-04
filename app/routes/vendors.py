from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from app.extensions import db
from app.models.vendor import Vendor

vendors_bp = Blueprint("vendors", __name__, url_prefix="/vendors")


@vendors_bp.route("/")
@login_required
def list_vendors():
    vendors = Vendor.query.order_by(Vendor.name.asc()).all()
    return render_template("vendors/list.html", vendors=vendors)


@vendors_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_vendor():
    if request.method == "POST":
        name = request.form.get("name", "").strip()

        if not name:
            flash("Vendor name is required", "danger")
            return redirect(url_for("vendors.create_vendor"))

        vendor = Vendor(
            name=name,
            category=request.form.get("category") or None,
            phone=request.form.get("phone") or None,
            email=request.form.get("email") or None,
            bank_name=request.form.get("bank_name") or None,
            account_name=request.form.get("account_name") or None,
            account_number=request.form.get("account_number") or None,
        )

        db.session.add(vendor)
        db.session.commit()

        flash("Vendor created successfully", "success")
        return redirect(url_for("vendors.list_vendors"))

    return render_template("vendors/create.html")
