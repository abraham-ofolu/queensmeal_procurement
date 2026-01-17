from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import func

from app.extensions import db
from app.models.procurement_request import ProcurementRequest
from app.models.payment import Payment
from app.models.vendor import Vendor

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


def allowed():
    return current_user.role in ["director", "audit"]


@reports_bp.before_request
@login_required
def restrict_access():
    if not allowed():
        return render_template("403.html"), 403


@reports_bp.route("/")
def index():
    procurement_stats = (
        db.session.query(
            func.count(ProcurementRequest.id),
            func.sum(ProcurementRequest.amount),
        ).first()
    )

    payment_stats = (
        db.session.query(
            func.sum(Payment.amount_paid)
        ).first()
    )

    vendor_count = db.session.query(func.count(Vendor.id)).scalar()

    return render_template(
        "reports/index.html",
        total_requests=procurement_stats[0] or 0,
        total_requested=procurement_stats[1] or 0,
        total_paid=payment_stats[0] or 0,
        vendor_count=vendor_count or 0,
    )
