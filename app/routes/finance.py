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
from app.models.payment import Payment
from app.models.procurement_request import ProcurementRequest

finance_bp = Blueprint("finance", __name__, url_prefix="/finance")


@finance_bp.route("/payments")
@login_required
def list_payments():
    payments = Payment.query.order_by(Payment.paid_at.desc()).all()
    return render_template("finance/payments_list.html", payments=payments)


@finance_bp.route("/payments/create/<int:request_id>", methods=["GET", "POST"])
@login_required
def make_payment(request_id):
    pr = ProcurementRequest.query.get_or_404(request_id)

    if request.method == "POST":
        amount = float(request.form.get("amount"))
        method = request.form.get("method")

        payment = Payment(
            procurement_request_id=pr.id,
            amount=amount,
            method=method,
            paid_at=datetime.utcnow()
        )

        db.session.add(payment)
        db.session.commit()

        flash("Payment recorded. Upload receipt below.", "success")
        return redirect(
            url_for("finance.upload_receipt", payment_id=payment.id)
        )

    return render_template("finance/pay.html", pr=pr)


# =========================
# RECEIPT UPLOAD
# =========================
@finance_bp.route("/payments/<int:payment_id>/upload-receipt", methods=["GET", "POST"])
@login_required
def upload_receipt(payment_id):
    payment = Payment.query.get_or_404(payment_id)

    if request.method == "POST":
        file = request.files.get("receipt")
        if not file or file.filename == "":
            flash("No file selected", "danger")
            return redirect(request.url)

        filename = secure_filename(file.filename)
        unique_name = f"RCPT_{uuid.uuid4()}_{filename}"

        upload_dir = os.path.join(
            current_app.root_path, "static", "uploads", "receipts"
        )
        os.makedirs(upload_dir, exist_ok=True)

        file.save(os.path.join(upload_dir, unique_name))
        payment.receipt = unique_name
        db.session.commit()

        flash("Receipt uploaded", "success")
        return redirect(
            url_for("procurement.view_request",
                    request_id=payment.procurement_request_id)
        )

    return render_template("finance/upload_receipt.html", payment=payment)


# =========================
# VIEW RECEIPT
# =========================
@finance_bp.route("/receipt/<path:filename>")
@login_required
def view_receipt(filename):
    upload_dir = os.path.join(
        current_app.root_path, "static", "uploads", "receipts"
    )
    return send_from_directory(upload_dir, filename)


# =========================
# DELETE RECEIPT
# =========================
@finance_bp.route("/payments/<int:payment_id>/delete-receipt", methods=["POST"])
@login_required
def delete_receipt(payment_id):
    payment = Payment.query.get_or_404(payment_id)

    if payment.receipt:
        path = os.path.join(
            current_app.root_path,
            "static",
            "uploads",
            "receipts",
            payment.receipt
        )
        if os.path.exists(path):
            os.remove(path)

        payment.receipt = None
        db.session.commit()
        flash("Receipt deleted", "success")

    return redirect(
        url_for("procurement.view_request",
                request_id=payment.procurement_request_id)
    )
