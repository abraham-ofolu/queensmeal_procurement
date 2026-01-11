import os
import uuid
from datetime import datetime
from flask import Blueprint, current_app, render_template, redirect, url_for, flash, request, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from ..extensions import db
from ..models.procurement_request import ProcurementRequest
from ..models.payment import Payment

finance_bp = Blueprint("finance", __name__)

@finance_bp.route("/payments", methods=["GET"])
@login_required
def payments():
    # If table exists, this works. If missing, AUTO_CREATE_TABLES will recreate.
    payments = Payment.query.order_by(Payment.created_at.desc()).all()
    reqs = ProcurementRequest.query.order_by(ProcurementRequest.created_at.desc()).all()
    return render_template("finance/payments.html", payments=payments, requests=reqs)

@finance_bp.route("/pay/<int:req_id>", methods=["POST"])
@login_required
def pay_request(req_id):
    pr = ProcurementRequest.query.get_or_404(req_id)

    # Only finance or director can pay (your rule)
    if current_user.role not in ("finance", "director"):
        flash("You are not allowed to make payments.", "danger")
        return redirect(url_for("finance.payments"))

    amount = request.form.get("amount", None)
    if not amount:
        flash("Amount is required.", "danger")
        return redirect(url_for("finance.payments"))

    pay = Payment(
        procurement_request_id=pr.id,
        amount=amount,
        paid_by=current_user.role,
        status="approved",
        created_at=datetime.utcnow(),
    )

    # receipt optional
    receipt = request.files.get("receipt")
    if receipt and receipt.filename.strip():
        filename = secure_filename(receipt.filename)
        unique_name = f"{uuid.uuid4()}_{filename}"
        save_path = os.path.join(current_app.config["RECEIPTS_FOLDER"], unique_name)
        receipt.save(save_path)
        pay.receipt_path = unique_name

    db.session.add(pay)
    db.session.commit()

    flash("Payment recorded.", "success")
    return redirect(url_for("finance.payments"))

@finance_bp.route("/receipt/<path:filename>", methods=["GET"])
@login_required
def view_receipt(filename):
    return send_from_directory(current_app.config["RECEIPTS_FOLDER"], filename, as_attachment=False)
