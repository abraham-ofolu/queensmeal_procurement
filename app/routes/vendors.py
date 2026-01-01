from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user

from app.extensions import db
from app.models.vendor import Vendor

vendors_bp = Blueprint("vendors", __name__, url_prefix="/vendors")


def _can_manage_vendors():
    # Procurement + Director can create/edit vendors
    return current_user.is_authenticated and current_user.role in ("procurement", "director")


@vendors_bp.route("/")
@login_required
def list_vendors():
    vendors = Vendor.query.order_by(Vendor.created_at.desc()).all()
    return render_template("vendors/list.html", vendors=vendors)


@vendors_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_vendor():
    if not _can_manage_vendors():
        flash("Access denied.", "danger")
        return redirect(url_for("vendors.list_vendors"))

    if request.method == "POST":
        v = Vendor(
            name=request.form.get("name", "").strip(),
            category=request.form.get("category") or None,
            phone=request.form.get("phone") or None,
            email=request.form.get("email") or None,
            contact_person=request.form.get("contact_person") or None,
            address=request.form.get("address") or None,
            bank_name=request.form.get("bank_name") or None,
            account_name=request.form.get("account_name") or None,
            account_number=request.form.get("account_number") or None,
            bank_code=request.form.get("bank_code") or None,
            notes=request.form.get("notes") or None,
        )

        if not v.name:
            flash("Vendor name is required.", "danger")
            return render_template("vendors/create.html")

        db.session.add(v)
        db.session.commit()

        flash("Vendor created successfully.", "success")
        return redirect(url_for("vendors.list_vendors"))

    return render_template("vendors/create.html")


@vendors_bp.route("/<int:vendor_id>")
@login_required
def view_vendor(vendor_id):
    vendor = Vendor.query.get_or_404(vendor_id)
    return render_template("vendors/view.html", vendor=vendor)


@vendors_bp.route("/<int:vendor_id>/edit", methods=["GET", "POST"])
@login_required
def edit_vendor(vendor_id):
    if not _can_manage_vendors():
        flash("Access denied.", "danger")
        return redirect(url_for("vendors.list_vendors"))

    vendor = Vendor.query.get_or_404(vendor_id)

    if request.method == "POST":
        vendor.name = request.form.get("name", "").strip()
        vendor.category = request.form.get("category") or None
        vendor.phone = request.form.get("phone") or None
        vendor.email = request.form.get("email") or None
        vendor.contact_person = request.form.get("contact_person") or None
        vendor.address = request.form.get("address") or None
        vendor.bank_name = request.form.get("bank_name") or None
        vendor.account_name = request.form.get("account_name") or None
        vendor.account_number = request.form.get("account_number") or None
        vendor.bank_code = request.form.get("bank_code") or None
        vendor.notes = request.form.get("notes") or None

        if not vendor.name:
            flash("Vendor name is required.", "danger")
            return render_template("vendors/edit.html", vendor=vendor)

        db.session.commit()
        flash("Vendor updated successfully.", "success")
        return redirect(url_for("vendors.view_vendor", vendor_id=vendor.id))

    return render_template("vendors/edit.html", vendor=vendor)
