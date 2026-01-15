from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime

from app.extensions import db
from app.models.procurement_request import ProcurementRequest
from app.models.vendor import Vendor

procurement_bp = Blueprint("procurement", __name__, url_prefix="/procurement")


@procurement_bp.route("/")
@login_required
def index():
    requests = ProcurementRequest.query.order_by(
        ProcurementRequest.created_at.desc()
    ).all()
    return render_template("procurement/index.html", requests=requests)


@procurement_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        item = request.form.get("item")
        quantity = request.form.get("quantity")
        amount = request.form.get("amount")
        vendor_id = request.form.get("vendor_id")
        is_urgent = True if request.form.get("is_urgent") == "on" else False

        if not item or not quantity or not amount or not vendor_id:
            flash("All fields are required", "danger")
            return redirect(url_for("procurement.create"))

        new_request = ProcurementRequest(
            item=item,
            quantity=int(quantity),
            amount=float(amount),
            vendor_id=int(vendor_id),
            is_urgent=is_urgent,
            status="pending",
            created_by=current_user.id,
            created_at=datetime.utcnow(),
        )

        db.session.add(new_request)
        db.session.commit()

        flash("Procurement request submitted successfully", "success")
        return redirect(url_for("procurement.index"))

    vendors = Vendor.query.order_by(Vendor.name.asc()).all()
    return render_template("procurement/create.html", vendors=vendors)
