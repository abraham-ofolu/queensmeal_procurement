from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import ProcurementRequest

import cloudinary
import cloudinary.uploader

from app.extensions import db
from app.models import Payment, ProcurementRequest

finance_bp = Blueprint("finance", __name__, url_prefix="/finance")


def _upload_to_cloudinary(file_storage, folder: str) -> str | None:
    """Uploads a werkzeug FileStorage to Cloudinary and returns secure_url."""
    if not file_storage or file_storage.filename == "":
        return None

    res = cloudinary.uploader.upload(
        file_storage,
        folder=folder,
        resource_type="auto",
        unique_filename=True,
        overwrite=False,
    )
    return res.get("secure_url")


@finance_bp.route("/payments", methods=["GET"])
@login_required
def list_payments():
    payments = Payment.query.order_by(Payment.created_at.desc()).all()
    return render_template("finance/payments.html", payments=payments)


@finance_bp.route("/payments/create/<int:procurement_id>", methods=["GET", "POST"])
@login_required
def create_payment(procurement_id: int):
    pr = ProcurementRequest.query.get_or_404(procurement_id)

    # Only allow payment creation when request is approved (match your rules if needed)
    if pr.status != "approved":
        flash("Only approved procurement requests can proceed to payment.", "warning")
        return redirect(url_for("procurement.view_request", request_id=pr.id))

    if request.method == "POST":
        amount = request.form.get("amount", "").strip()
        paid_by = request.form.get("paid_by", "").strip()

        # Receipt is optional here; you can restrict to director only:
        receipt_file = request.files.get("receipt")
        receipt_url = None

        if receipt_file and receipt_file.filename:
            if current_user.role != "director":
                flash("Only Director can upload payment receipts.", "danger")
                return redirect(url_for("finance.create_payment", procurement_id=pr.id))

            receipt_url = _upload_to_cloudinary(receipt_file, folder="queensmeal/receipts")

        pay = Payment(
            procurement_id=pr.id,
            amount=float(amount) if amount else 0.0,
            paid_by=paid_by or current_user.username,
            receipt_url=receipt_url,
            created_at=datetime.utcnow(),
        )

        db.session.add(pay)
        db.session.commit()

        flash("Payment recorded successfully.", "success")
        return redirect(url_for("finance.list_payments"))

    return render_template("finance/create_payment.html", pr=pr)
