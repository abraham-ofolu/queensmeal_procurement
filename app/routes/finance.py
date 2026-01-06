from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models import Payment, ProcurementRequest, AuditLog
from app.utils.cloudinary import upload_file, delete_file

finance_bp = Blueprint("finance", __name__, url_prefix="/finance")


@finance_bp.route("/payments")
@login_required
def list_payments():
    payments = Payment.query.order_by(Payment.paid_at.desc()).all()
    return render_template("finance/payments_list.html", payments=payments)


@finance_bp.route("/payments/create/<int:request_id>", methods=["GET", "POST"])
@login_required
def make_payment(request_id):
    if current_user.role not in ["finance", "director"]:
        abort(403)

    pr = ProcurementRequest.query.get_or_404(request_id)

    if request.method == "POST":
        amount = request.form.get("amount")
        method = request.form.get("method")
        receipt = request.files.get("receipt")

        payment = Payment(
            procurement_request_id=pr.id,
            amount=amount,
            method=method,
            paid_at=datetime.utcnow()
        )

        if receipt:
            payment.receipt = upload_file(receipt, folder="receipts")

        db.session.add(payment)
        db.session.add(AuditLog(
            user_id=current_user.id,
            action="CREATE_PAYMENT",
            entity="Payment",
            entity_id=payment.id
        ))
        db.session.commit()

        flash("Payment recorded", "success")
        return redirect(url_for("procurement.view_request", request_id=pr.id))

    return render_template("finance/pay.html", pr=pr)


@finance_bp.route("/payments/upload-receipt/<int:payment_id>", methods=["POST"])
@login_required
def upload_receipt(payment_id):
    if current_user.role != "finance":
        abort(403)

    payment = Payment.query.get_or_404(payment_id)
    file = request.files.get("receipt")

    if not file:
        flash("No file selected", "danger")
        return redirect(url_for("procurement.view_request", request_id=payment.procurement_request_id))

    if payment.receipt:
        delete_file(payment.receipt)

    payment.receipt = upload_file(file, folder="receipts")

    db.session.add(AuditLog(
        user_id=current_user.id,
        action="UPLOAD_RECEIPT",
        entity="Payment",
        entity_id=payment.id
    ))
    db.session.commit()

    flash("Receipt uploaded", "success")
    return redirect(url_for("procurement.view_request", request_id=payment.procurement_request_id))


@finance_bp.route("/payments/delete-receipt/<int:payment_id>", methods=["POST"])
@login_required
def delete_receipt(payment_id):
    if current_user.role != "finance":
        abort(403)

    payment = Payment.query.get_or_404(payment_id)

    if payment.receipt:
        delete_file(payment.receipt)
        payment.receipt = None

        db.session.add(AuditLog(
            user_id=current_user.id,
            action="DELETE_RECEIPT",
            entity="Payment",
            entity_id=payment.id
        ))
        db.session.commit()

    flash("Receipt deleted", "success")
    return redirect(url_for("procurement.view_request", request_id=payment.procurement_request_id))
