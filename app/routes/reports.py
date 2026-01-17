from datetime import datetime, timedelta
import csv
from io import StringIO

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    Response,
)
from flask_login import login_required, current_user
from sqlalchemy import func

from app.extensions import db
from app.models.procurement_request import ProcurementRequest
from app.models.payment import Payment

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


def _role():
    return (getattr(current_user, "role", "") or "").lower()


def _require_role(*roles):
    if _role() not in [r.lower() for r in roles]:
        flash("You are not allowed to access reports.", "danger")
        return False
    return True


@reports_bp.route("/", methods=["GET"])
@login_required
def index():
    if not _require_role("director", "finance", "audit"):
        return redirect(url_for("procurement.index"))

    # ---------------- Filters (SAFE DEFAULTS) ----------------
    role_filter = request.args.get("paid_by_role") or "all"
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d") if start_date else datetime.utcnow() - timedelta(days=29)
        end_dt = datetime.strptime(end_date, "%Y-%m-%d") if end_date else datetime.utcnow()
    except ValueError:
        start_dt = datetime.utcnow() - timedelta(days=29)
        end_dt = datetime.utcnow()

    # ---------------- KPIs ----------------
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

    paid_expr = func.coalesce(Payment.amount_paid, Payment.amount)

    payments_q = Payment.query.filter(
        func.coalesce(Payment.paid_at, Payment.created_at) >= start_dt,
        func.coalesce(Payment.paid_at, Payment.created_at) <= end_dt,
    )

    if role_filter != "all":
        payments_q = payments_q.filter(func.lower(Payment.paid_by_role) == role_filter.lower())

    total_paid = payments_q.with_entities(func.coalesce(func.sum(paid_expr), 0)).scalar() or 0

    # ---------------- Charts ----------------

    # Requests per day
    day_rows = (
        db.session.query(
            func.date(ProcurementRequest.created_at).label("day"),
            func.count(ProcurementRequest.id),
        )
        .filter(
            ProcurementRequest.created_at >= start_dt,
            ProcurementRequest.created_at <= end_dt,
        )
        .group_by(func.date(ProcurementRequest.created_at))
        .order_by(func.date(ProcurementRequest.created_at))
        .all()
    )

    day_map = {str(r[0]): int(r[1]) for r in day_rows}
    days = [
        (start_dt.date() + timedelta(days=i)).isoformat()
        for i in range((end_dt.date() - start_dt.date()).days + 1)
    ]
    day_values = [day_map.get(d, 0) for d in days]

    # Payments by role
    role_rows = (
        payments_q.with_entities(
            func.lower(Payment.paid_by_role),
            func.sum(paid_expr),
        )
        .group_by(func.lower(Payment.paid_by_role))
        .all()
    )

    role_labels = [r[0] or "unknown" for r in role_rows]
    role_values = [float(r[1] or 0) for r in role_rows]

    # Monthly spend  ✅ FIXED GROUP BY
    month_expr = func.to_char(
        func.date_trunc("month", func.coalesce(Payment.paid_at, Payment.created_at)),
        "YYYY-MM",
    )

    month_rows = (
        payments_q.with_entities(
            month_expr,
            func.sum(paid_expr),
        )
        .group_by(month_expr)
        .order_by(month_expr)
        .all()
    )

    month_labels = [m[0] for m in month_rows]
    month_values = [float(m[1] or 0) for m in month_rows]

    return render_template(
        "reports/index.html",
        kpis=dict(
            total_requests=total_requests,
            approved_requests=approved_requests,
            pending_requests=pending_requests,
            rejected_requests=rejected_requests,
            total_paid=float(total_paid),
        ),
        charts=dict(
            requests_daily=dict(labels=days, values=day_values),
            payments_by_role=dict(labels=role_labels, values=role_values),
            monthly_spend=dict(labels=month_labels, values=month_values),
        ),
        filters=dict(
            start_date=start_dt.date().isoformat(),
            end_date=end_dt.date().isoformat(),
            role=role_filter,
        ),
    )


@reports_bp.route("/export.csv", methods=["GET"])
@login_required
def export_csv():
    if not _require_role("director", "finance", "audit"):
        return redirect(url_for("procurement.index"))

    role_filter = request.args.get("paid_by_role") or "all"
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    start_dt = datetime.strptime(start_date, "%Y-%m-%d") if start_date else datetime.utcnow() - timedelta(days=29)
    end_dt = datetime.strptime(end_date, "%Y-%m-%d") if end_date else datetime.utcnow()

    q = Payment.query.filter(
        func.coalesce(Payment.paid_at, Payment.created_at) >= start_dt,
        func.coalesce(Payment.paid_at, Payment.created_at) <= end_dt,
    )

    if role_filter != "all":
        q = q.filter(func.lower(Payment.paid_by_role) == role_filter.lower())

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Payment ID",
        "Procurement Request ID",
        "Amount",
        "Paid By Role",
        "Paid By Name",
        "Paid At",
        "Receipt URL",
    ])

    for p in q.order_by(Payment.created_at.desc()).all():
        writer.writerow([
            p.id,
            p.procurement_request_id,
            p.amount_paid or p.amount,
            p.paid_by_role,
            p.paid_by_name,
            p.paid_at,
            p.receipt_url,
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=payments_report.csv"},
    )
