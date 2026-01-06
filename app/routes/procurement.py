import os
import uuid
from datetime import datetime

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, current_app, send_from_directory
)
from flask_login import login_required
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.procurement_request import ProcurementRequest
from app.models.vendor import Vendor
from app.models.payment import Payment

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
# CREATE REQUEST  ✅ FIXED
# =========================
@procurement_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_request():
    vendors = Vendor.query.order_by(Vendor.name.asc()).all()

    if request.method == "POST":
        pr = ProcurementRequest(
            title=request.form.get("title"),
            description=request.form.get("description"),
            amount=float(request.form.get("amount")),
            vendor_id=int(request.form.get("vendor_id")),
            status="pending",
            created_at=datetime.utcnow()
        )

        # QUOTATION UPLOAD
        file = request.files.get("quotation")
        if file and file.filename:
            filename = secure_filename(file.filename)
            unique_name = f"PR_{uuid.uuid4()}_{filename}"

            upload_dir = os.path.join(
                current_app.root_path,
                "static",
                "uploads",
                "quotations"
            )
            os.makedirs(upload_dir, exist_ok=True)
            file.save(os.path.join(upload_dir, unique_name))
            pr.quotation = unique_name

        db.session.add(pr)
        db.session.commit()

        flash("Procurement request created", "success")
        return redirect(url_for("procurement.view_request", request_id=pr.id))

    return render_template("procurement/create.html", vendors=vendors)


# =========================
# VIEW REQUEST
# =========================
@procurement_bp.route("/<int:request_id>")
@login_required
def view_request(request_id):
    pr = ProcurementRequest.query.get_or_404(request_id)
    payments = Payment.query.filter_by(
        procurement_request_id=pr.id
    ).all()
    total_paid = sum(p.amount for p in payments)

    return render_template(
        "procurement/view.html",
        pr=pr,
        payments=payments,
        total_paid=total_paid
    )


# =========================
# VIEW QUOTATION
# =========================
@procurement_bp.route("/quotation/<path:filename>")
@login_required
def view_quotation(filename):
    upload_dir = os.path.join(
        current_app.root_path,
        "static",
        "uploads",
        "quotations"
    )
    return send_from_directory(upload_dir, filename)


# =========================
# DELETE QUOTATION
# =========================
@procurement_bp.route("/<int:request_id>/delete-quotation", methods=["POST"])
@login_required
def delete_quotation(request_id):
    pr = ProcurementRequest.query.get_or_404(request_id)

    if pr.quotation:
        path = os.path.join(
            current_app.root_path,
            "static",
            "uploads",
            "quotations",
            pr.quotation
        )
        if os.path.exists(path):
            os.remove(path)

        pr.quotation = None
        db.session.commit()
        flash("Quotation deleted", "success")

    return redirect(url_for("procurement.view_request", request_id=pr.id))
