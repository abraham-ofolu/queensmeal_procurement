from datetime import datetime, timedelta

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import func

from app.extensions import db

# Models (do NOT change these models; just read from them)
from app.models.procurement_request import ProcurementRequest
from app.models.payment import Payment


reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


def _role() -> str:
    return (getattr(current_user, "role", "") or "").lower()


def _require_role(*roles: str) -> bool:
    allowed = [r.lower() for r in roles]
    if _role() not in allowed:
        flash("You are not allowed to access that page.", "danger")
        return False
    return True


@reports_bp.route("/", methods=["GET"])
@login_required
def index():
    # Reports should be view-only for Director + Finance (safe mode)
    if not _require_role("director", "finance", "audit"):
        return redirect(url_for("procurement.index"))

    # Time window (last 30 days) — safe defaults
    today = datetime.utcnow().date()
    start_day = today - timedelta(days=29)

    # -------- KPIs (SAFE: read-only) --------
    total_requests = db.session.query(func.count(ProcurementRequest.id)).scalar() or 0

    approved_requests = (
        db.session.query(func.count(ProcurementRequest.id))
        .filter(func.lower(ProcurementRequest.status) == "approved")
        .scalar()
        or 0
    )

    pending_requests = (
        db.session.query(func.count(ProcurementRequest.id))
        .filter(func.lower(ProcurementRequest.status) == "pending")
        .scalar()
        or 0
    )

    rejected_requests = (
        db.session.query(func.count(ProcurementRequest.id))
        .filter(func.lower(ProcurementRequest.status) == "rejected")
        .scalar()
        or 0
    )

    # Spend: use Payment.amount_paid if present else Payment.amount (your schema has both)
    paid_amount_expr = func.coalesce(Payment.amount_paid, Payment.amount)

    total_paid = db.session.query(func.coalesce(func.sum(paid_amount_expr), 0)).scalar() or 0

    # -------- Charts Data --------

    # 1) Requests per day (last 30 days)
    daily_rows = (
        db.session.query(func.date(ProcurementRequest.created_at).label("day"), func.count(ProcurementRequest.id))
        .filter(func.date(ProcurementRequest.created_at) >= start_day)
        .group_by(func.date(ProcurementRequest.created_at))
        .order_by(func.date(ProcurementRequest.created_at).asc())
        .all()
    )

    daily_counts_map = {str(r[0]): int(r[1]) for r in daily_rows}
    day_labels = [(start_day + timedelta(days=i)).isoformat() for i in range(30)]
    day_values = [daily_counts_map.get(d, 0) for d in day_labels]

    # 2) Payments split by role (director vs finance) — based on paid_by_role
    role_rows = (
        db.session.query(func.lower(Payment.paid_by_role).label("role"), func.coalesce(func.sum(paid_amount_expr), 0))
        .group_by(func.lower(Payment.paid_by_role))
        .all()
    )
    role_labels = []
    role_values = []
    for role, amt in role_rows:
        role_labels.append(role or "unknown")
        # convert Decimal/None safely
        role_values.append(float(amt or 0))

    # 3) Monthly spend (last 6 months)
    # Uses date_trunc('month', paid_at) where paid_at exists; fallback to created_at
    month_key = func.to_char(func.date_trunc("month", func.coalesce(Payment.paid_at, Payment.created_at)), "YYYY-MM")
    month_rows = (
        db.session.query(month_key.label("month"), func.coalesce(func.sum(paid_amount_expr), 0))
        .filter(func.coalesce(Payment.paid_at, Payment.created_at) >= (datetime.utcnow() - timedelta(days=183)))
        .group_by(month_key)
        .order_by(month_key.asc())
        .all()
    )
    month_labels = [m[0] for m in month_rows]
    month_values = [float(m[1] or 0) for m in month_rows]

    return render_template(
        "reports/index.html",
        kpis={
            "total_requests": int(total_requests),
            "approved_requests": int(approved_requests),
            "pending_requests": int(pending_requests),
            "rejected_requests": int(rejected_requests),
            "total_paid": float(total_paid),
        },
        charts={
            "requests_daily": {"labels": day_labels, "values": day_values},
            "payments_by_role": {"labels": role_labels, "values": role_values},
            "monthly_spend": {"labels": month_labels, "values": month_values},
        },
    )
