from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime

from app.extensions import db
from app.models.procurement import ProcurementRequest
from app.models.vendor import Vendor

# ✅ Blueprint MUST be defined first
procurement_bp = Blueprint(
    "procurement",
    __name__,
    url_prefix="/procurement"
)

# =========================
# LIST PROCUREMENT REQUESTS
# =========================
@procurement_bp.route("/", methods=["GET"])
@login_required
def index():
    requests = ProcurementRequest.query.order_by(
        ProcurementRequest.created_at.desc()
    ).all()

    return render_template(
        "procurement/index.html",
        requests=requests
    )

# =========================
# CREATE PROCUREMENT REQUEST
# =========================
@procurement_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_request():
    vendors = Vendor.query.all()

    if request.method == "POST":
        title = request.form["title"]
        description = request.form.get("description")
        amount = request.form["amount"]
        vendor_id = request.form.get("vendor_id")

        pr = ProcurementRequest(
            title=title,
            description=description,
            amount=amount,
            vendor_id=vendor_id if vendor_id else None,
            created_by=current_user.id
        )

        db.session.add(pr)
        db.session.commit()

        flash("Procurement request created successfully", "success")
        return redirect(url_for("procurement.index"))

    return render_template(
        "procurement/create.html",
        vendors=vendors
    )
