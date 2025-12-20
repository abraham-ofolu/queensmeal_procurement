from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.vendor import Vendor
from app.models.procurement import ProcurementRequest
from sqlalchemy import func

dash_bp = Blueprint("dashboard", __name__)


@dash_bp.route("/")
@login_required
def home():
    total_vendors = Vendor.query.count()
    approved_vendors = Vendor.query.filter_by(status="approved").count()
    total_requests = ProcurementRequest.query.count()

    pending_requests = ProcurementRequest.query.filter(
        ProcurementRequest.status == "submitted"
    ).count()

    # ---- STATUS CHART DATA (SAFE) ----
    status_data = (
        ProcurementRequest.query
        .with_entities(ProcurementRequest.status, func.count())
        .group_by(ProcurementRequest.status)
        .all()
    )

    status_labels = [row[0].title() for row in status_data] if status_data else []
    status_values = [row[1] for row in status_data] if status_data else []

    # ---- TREND CHART DATA (SAFE) ----
    recent_requests = (
        ProcurementRequest.query
        .order_by(ProcurementRequest.id.desc())
        .limit(7)
        .all()
    )

    recent_requests.reverse()

    trend_labels = [f"#{r.id}" for r in recent_requests] if recent_requests else []
    trend_values = list(range(1, len(recent_requests) + 1)) if recent_requests else []

    return render_template(
        "dashboard.html",
        total_vendors=total_vendors,
        approved_vendors=approved_vendors,
        total_requests=total_requests,
        pending_requests=pending_requests,
        status_labels=status_labels,
        status_values=status_values,
        trend_labels=trend_labels,
        trend_values=trend_values,
        recent_requests=recent_requests,
        role=current_user.role,
    )
