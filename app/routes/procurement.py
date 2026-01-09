from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime

from app.extensions import db
from app.models.procurement import ProcurementRequest
from app.models.vendor import Vendor

procurement_bp = Blueprint("procurement", __name__, url_prefix="/procurement")


@procurement_bp.route("/")
@login_required
def list_requests():
    requests = ProcurementRequest.query.order_by(
        ProcurementRequest.created_at.desc()
    ).all()
    return render_template("procurement/list.html", requests=requests)


@procurement_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_request():
    vendors = Vendor.query.order_by(Vendor.name.asc()).all()

    if request.method == "POST":
        item_name = request.form.get("item_name")
        quantity = request.form.get("quantity")
        vendor_id = request.form.get("vendor_id")

        if not item_name or not quantity or not vendor_id:
            flash("All fields are required", "danger")
            return redirect(url_for("procurement.create_request"))

        pr = ProcurementRequest(
            item_name=item_name,   # ✅ MATCHES MODEL
            quantity=int(quantity),
            vendor_id=int(vendor_id),
            status="PENDING_DIRECTOR",
            created_at=datetime.utcnow(),
        )

        db.session.add(pr)
        db.session.commit()

        flash("Procurement request submitted successfully", "success")
        return redirect(url_for("procurement.list_requests"))

    return render_template(
        "procurement/create.html",
        vendors=vendors
    )
