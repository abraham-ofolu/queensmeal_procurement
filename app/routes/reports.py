# app/routes/reports.py
from flask import Blueprint, render_template
from flask_login import login_required

from app.extensions import db
from app.models.procurement_request import ProcurementRequest
from app.models.payment import Payment

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


@reports_bp.route("/")
@login_required
def index():
    # status counts
    status_counts = (
        db.session.query(ProcurementRequest.status, db.func.count(ProcurementRequest.id))
        .group_by(ProcurementRequest.status)
        .all()
    )
    status_labels = [s[0] for s in status_counts]
    status_values = [int(s[1]) for s in status_counts]

    # monthly payments (last 6 months approx by created_at)
    # works even if some are null
    monthly = (
        db.session.query(
            db.func.to_char(Payment.created_at, "YYYY-MM"),
            db.func.coalesce(db.func.sum(Payment.amount), 0),
        )
        .group_by(db.func.to_char(Payment.created_at, "YYYY-MM"))
        .order_by(db.func.to_char(Payment.created_at, "YYYY-MM").desc())
        .limit(6)
        .all()
    )
    monthly = list(reversed(monthly))
    month_labels = [m[0] for m in monthly]
    month_values = [float(m[1] or 0) for m in monthly]

    total_requests = ProcurementRequest.query.count()
    total_paid = float(db.session.query(db.func.coalesce(db.func.sum(Payment.amount), 0)).scalar() or 0)

    return render_template(
        "reports/index.html",
        status_labels=status_labels,
        status_values=status_values,
        month_labels=month_labels,
        month_values=month_values,
        total_requests=total_requests,
        total_paid=total_paid,
    )
