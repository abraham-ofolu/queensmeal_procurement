from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime

from app.extensions import db
from app.models.procurement import ProcurementRequest
from app.models.vendor import Vendor

procurement_bp = Blueprint("procurement", __name__)

@procurement_bp.route("/")
@login_required
def index():
    requests = ProcurementRequest.query.order_by(
        ProcurementRequest.created_at.desc()
    ).all()
    return render_template("procurement/index.html", requests=requests)

@procurement_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_request():
    vendors = Vendor.query.all()

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        amount = request.form.get("amount")
        vendor_id = request.form.get("vendor_id")

        if not title or not amount or not vendor_id:
            flash("Title, Amount and Vendor are required", "danger")
            return redirect(url_for("procurement.create_request"))

        pr = ProcurementRequest(
            title=title,
            description=description,
            amount=float(amount),
            vendor_id=int(vendor_id),
            created_by_id=current_user.id,
            created_at=datetime.utcnow(),
        )

        db.session.add(pr)
        db.session.commit()

        flash("Procurement request created successfully", "success")
        return redirect(url_for("procurement.index"))

    return render_template(
        "procurement/create.html",
        vendors=vendors,
    )
