import os
from datetime import datetime
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, current_app, send_from_directory
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app import db
from app.models import Payment, ProcurementRequest

finance_bp = Blueprint("finance", __name__, url_prefix="/finance")


@finance_bp.route("/payments")
@login_required
def list_payments():
    payments = Payment.query.order_by(Payment.created_at.desc()).all()
    return render_template("finance/payments_list.html", payments=payments)


@finance_bp.route("/payments/create/<int:request_id>", methods=["GET", "POST"])
@login_required
def make_payment(request_id):
    pr = ProcurementRequest.query.get_or_404(request_id)

    if request.method == "POST":
        receipt_file = request.files.get("receipt")
        receipt_filename = None

        if receipt_file and receipt_file.filename:
            filename = secure_filename(receipt_file.filename)
            upload_dir = os.path.join(
                current_app.root_path, "static", "uploads", "receipts"
            )
            os.makedirs(upload_dir, exist_ok=True)
            receipt_file.save(os.path.join(upload_dir, filename))
            receipt_filename = filename

        payment = Payment(
            procurement_request_id=pr.id,
            amount=float(request.form.get("amount")),
            method=request.form.get("method"),
            receipt=receipt_filename,
            paid_by=current_user.username,
            paid_at=datetime.utcnow(),
            created_at=datetime.utcnow()
        )

        db.session.add(payment)
        db.session.commit()

        flash("Payment recorded successfully", "success")
        return redirect(url_for("procurement.view_request", request_id=pr.id))

    return render_template("finance/pay.html", pr=pr)


@finance_bp.route("/receipt/<path:filename>")
@login_required
def view_receipt(filename):
    upload_dir = os.path.join(
        current_app.root_path, "static", "uploads", "receipts"
    )
    return send_from_directory(upload_dir, filename)
