from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime

from app.extensions import db
from app.models.procurement import ProcurementRequest
from app.models.vendor import Vendor

procurement_bp = Blueprint(
    "procurement",
    __name__,
    url_prefix="/procurement"
)

@procurement_bp.route("/")
@login_required
def index():
    requests = (
        ProcurementRequest.query
        .order_by(ProcurementRequest.created_at.desc())
        .all()
    )
    return render_template("procurement/index.html", requests=requests)

@procurement_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_request():
    vendors = Vendor.query.order_by(Vendor.name.asc()).all()

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        amount = request.form.get("amount")
        vendor_id = request.form.get("vendor_id")

        if not title or not amount or not vendor_id:
            flash("Title, amount and vendor are required", "danger")
            return redirect(url_for("procurement.create_request"))

        pr = ProcurementRequest(
            title=title,
            description=description,
            amount=amount,
            vendor_id=vendor_id,
            created_by_id=current_user.id,
            status="pending",
            created_at=datetime.utcnow()
        )

        db.session.add(pr)
        db.session.commit()

        flash("Procurement request submitted successfully", "success")
        return redirect(url_for("procurement.index"))

    return render_template(
        "procurement/create.html",
        vendors=vendors
    )
