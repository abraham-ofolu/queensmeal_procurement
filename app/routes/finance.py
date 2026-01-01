# app/routes/finance.py
import os
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, send_from_directory
from flask_login import login_required, current_user

from app.extensions import db
from app.constants import FINANCE_LIMIT
from app.models.payment import Payment
from app.models.procurement_request import ProcurementRequest
from app.models.audit_log import AuditLog

finance_bp = Blueprint("finance", __name__, url_prefix="/finance")


def _log(action, entity_type=None, entity_id=None, details=None):
    db.session.add(
        AuditLog(
            username=getattr(current_user, "username", None),
            role=getattr(current_user, "role", None),
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
        )
    )


@finance_bp.route("/payments")
@login_required
def list_payments():
    payments = Payment.query.order_by(Payment.created_at.desc()).all()
    return render_template("finance/list.html", payments=payments)


@finance_bp.route("/payments/receipt/<path:filename>")
@login_required
def view_receipt(filename):
    upload_dir = os.path.join(current_app.root_path, "static", "uploads", "receipts")
    return send_from_directory(upload_dir, filename, as_attachment=False)


@finance_bp.route("/payments/create/<int:request_id>", methods=["GET", "POST"])
@login_required
def make_payment(request_id):
    pr = ProcurementRequest.query.get_or_404(request_id)

    # must be approved to pay
    if pr.status != "approved":
        flash("Only approved requests can be paid.", "warning")
        return redirect(url_for("procurement.view_request", request_id=pr.id))

    # role rules:
    # finance can pay only within limit, director can pay any, procurement can pay only within limit
    role = current_user.role
    if role not in ("finance", "director", "procurement"):
        flash("Access denied", "danger")
        return redirect(url_for("finance.list_payments"))

    if request.method == "POST":
        amount = request.form.get("amount", "").strip()
        method = request.form.get("method") or None
        reference = request.form.get("reference") or None

        if not amount:
            flash("Amount is required.", "danger")
            return render_template("finance/create.html", pr=pr, finance_limit=FINANCE_LIMIT)

        # enforce limit for finance/procurement
        try:
            amt_value = float(amount)
        except Exception:
            flash("Invalid amount.", "danger")
            return render_template("finance/create.html", pr=pr, finance_limit=FINANCE_LIMIT)

        if role in ("finance", "procurement") and amt_value > float(FINANCE_LIMIT):
            flash(f"{role.title()} can only pay up to ₦{FINANCE_LIMIT:,.0f}. Director must pay above limit.", "danger")
            return render_template("finance/create.html", pr=pr, finance_limit=FINANCE_LIMIT)

        # receipt upload
        receipt_file = request.files.get("receipt")
        receipt_filename = None
        if receipt_file and receipt_file.filename:
            upload_dir = os.path.join(current_app.root_path, "static", "uploads", "receipts")
            os.makedirs(upload_dir, exist_ok=True)
            safe_name = f"PAY_{int(datetime.utcnow().timestamp())}_{receipt_file.filename}".replace(" ", "_")
            receipt_path = os.path.join(upload_dir, safe_name)
            receipt_file.save(receipt_path)
            receipt_filename = safe_name

        payment = Payment(
            procurement_request_id=pr.id,
            amount=amt_value,
            method=method,
            reference=reference,
            receipt=receipt_filename,
            paid_by=current_user.username,
            paid_at=datetime.utcnow(),
        )
        db.session.add(payment)
        db.session.flush()

        _log("PAYMENT_CREATE", "Payment", payment.id, f"request_id={pr.id}, amount={amt_value}, paid_by={current_user.username}")
        db.session.commit()

        flash("Payment recorded successfully.", "success")
        return redirect(url_for("procurement.view_request", request_id=pr.id))

    return render_template("finance/create.html", pr=pr, finance_limit=FINANCE_LIMIT)
