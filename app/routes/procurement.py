from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from datetime import datetime
from app.extensions import db
from app.models import ProcurementRequest, Vendor

procurement_bp = Blueprint("procurement", __name__, url_prefix="/procurement")


# =========================
# LIST REQUESTS
# =========================
@procurement_bp.route("/")
@login_required
def list_requests():
    requests = ProcurementRequest.query.order_by(
        ProcurementRequest.created_at.desc()
    ).all()
    return render_template("procurement/list.html", requests=requests)


# =========================
# CREATE REQUEST  ✅ THIS WAS MISSING
# =========================
@procurement_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_request():
    vendors = Vendor.query.order_by(Vendor.name.asc()).all()

    if request.method == "POST":
        pr = ProcurementRequest(
            item_name=request.form.get("item_name"),
            description=request.form.get("description"),
            amount=request.form.get("amount"),
            vendor_id=request.form.get("vendor_id"),
            status="pending",
            created_by=current_user.id,
            created_at=datetime.utcnow()
        )

        db.session.add(pr)
        db.session.commit()

        flash("Procurement request created successfully", "success")
        return redirect(url_for("procurement.list_requests"))

    return render_template("procurement/create.html", vendors=vendors)


# =========================
# VIEW REQUEST
# =========================
@procurement_bp.route("/<int:request_id>")
@login_required
def view_request(request_id):
    pr = ProcurementRequest.query.get_or_404(request_id)
    return render_template("procurement/view.html", pr=pr)
