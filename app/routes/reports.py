from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy import func

from app.models.vendor import Vendor
from app.models.procurement import ProcurementRequest

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


@reports_bp.route("/dashboard")
@login_required
def dashboard():
    total_vendors = Vendor.query.count()
    approved_vendors = Vendor.query.filter_by(status="approved").count()
    total_requests = ProcurementRequest.query.count()

    pending_requests = ProcurementRequest.query.filter(
        ProcurementRequest.status == "submitted"
    ).count()

    # Status chart data
    status_data = (
        ProcurementRequest.query
        .with_entities(ProcurementRequest.status, func.count())
        .group_by(ProcurementRequest.status)
        .all()
    )

    status_labels = [s[0].title() for s in status_data] if status_data else []
    status_values = [s[1] for s in status_data] if status_data else []

    # Trend (last 7)
    recent_requests = (
        ProcurementRequest.query
        .order_by(ProcurementRequest.id.desc())
        .limit(7)
        .all()
    )[::-1]

    trend_labels = [f"#{r.id}" for r in recent_requests] if recent_requests else []
    trend_values = list(range(1, len(recent_requests) + 1)) if recent_requests else []

    return render_template(
        "reports/dashboard.html",
        total_vendors=total_vendors,
        approved_vendors=approved_vendors,
        total_requests=total_requests,
        pending_requests=pending_requests,
        status_labels=status_labels,
        status_values=status_values,
        trend_labels=trend_labels,
        trend_values=trend_values,
        recent_requests=recent_requests,
    )
