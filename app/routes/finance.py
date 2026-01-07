import os
from flask import Blueprint, render_template, redirect, url_for, current_app, send_from_directory
from flask_login import login_required

from app.extensions import db
from app.models import Payment, ProcurementRequest, AuditLog

finance_bp = Blueprint("finance", __name__, url_prefix="/finance")


@finance_bp.route("/payments")
@login_required
def list_payments():
    payments = Payment.query.order_by(Payment.created_at.desc()).all()
    return render_template("finance/list.html", payments=payments)


@finance_bp.route("/receipt/<path:filename>")
@login_required
def view_receipt(filename):
    upload_dir = os.path.join(
        current_app.root_path,
        "static",
        "uploads",
        "receipts"
    )
    return send_from_directory(upload_dir, filename, as_attachment=False)
