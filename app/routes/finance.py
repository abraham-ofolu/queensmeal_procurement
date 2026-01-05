import os
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_from_directory
from flask_login import login_required, current_user

from app.extensions import db
from app.models.payment import Payment
from app.models.procurement_request import ProcurementRequest

finance_bp = Blueprint("finance", __name__, url_prefix="/finance")


@finance_bp.route("/payments")
@login_required
def list_payments():
    payments = Payment.query.order_by(Payment.created_at.desc()).all()
    return render_template("finance/payments_list.html", payments=payments)


@finance_bp.route("/payments/create/<int:procurement_id>", methods=["GET", "POST"])
@login_required
def make_payment(procurement_id):
    pr = ProcurementRequest.query.get_or_404(procurement_id)

    if request.method == "POST":
        amount = float(request.form.get("amount", 0))
        method = request.form.get("method")
        description = request.form.get("description")

        receipt_file = request.files.get("receipt")
        receipt_filename = None

        if receipt_file and receipt_file.filename:
            upload_dir = os.path.join(current_app.root_path, "static/uploads/receipts")
            os.makedirs(upload_dir, exist_ok=True)

            timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            receipt_filename = f"{timestamp}_{receipt_file.filename}"
            receipt_file.save(os.path.join(upload_dir, receipt_filename))

        payment = Payment(
            procurement_request_id=pr.id,
            amount=amount,
            method=method,
            description=description,
            receipt=receipt_filename,
            paid_by=current_user.username,
            paid_at=datetime.utcnow(),
        )

        db.session.add(payment)
        db.session.commit()

        flash("Payment recorded successfully.", "success")
        return redirect(url_for("finance.list_payments"))

    return render_template("finance/payment_create.html", procurement=pr)


@finance_bp.route("/payments/receipt/<filename>")
@login_required
def view_receipt(filename):
    upload_dir = os.path.join(current_app.root_path, "static/uploads/receipts")
    return send_from_directory(upload_dir, filename)
