import os
from decimal import Decimal

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app.extensions import db
from app.models.procurement_request import ProcurementRequest

finance_bp = Blueprint("finance", __name__, url_prefix="/finance")


def _role() -> str:
    return (getattr(current_user, "role", "") or "").lower()


def _pay_limit() -> Decimal:
    # You can set FINANCE_PAY_LIMIT on Render env vars (example: 500000)
    raw = os.getenv("FINANCE_PAY_LIMIT", "500000")
    try:
        return Decimal(raw)
    except Exception:
        return Decimal("500000")


@finance_bp.route("/payments", methods=["GET"])
@login_required
def payments():
    if _role() not in {"finance", "director"}:
        flash("Only Finance/Director can access payments.", "danger")
        return redirect(url_for("procurement.index"))

    approved = (
        ProcurementRequest.query.filter_by(status="approved")
        .order_by(ProcurementRequest.created_at.desc())
        .all()
    )
    return render_template("finance/payments.html", requests=approved, pay_limit=_pay_limit())


@finance_bp.route("/mark-paid/<int:req_id>", methods=["POST"])
@login_required
def mark_paid(req_id: int):
    if _role() not in {"finance", "director"}:
        flash("Not allowed.", "danger")
        return redirect(url_for("finance.payments"))

    pr = ProcurementRequest.query.get_or_404(req_id)

    if pr.status != "approved":
        flash("Only approved requests can be paid.", "warning")
        return redirect(url_for("finance.payments"))

    limit = _pay_limit()

    # Rules:
    # - If amount <= limit: Finance can pay
    # - If amount > limit: ONLY Director can pay
    if pr.amount is not None and pr.amount > limit and _role() != "director":
        flash(f"Over limit. Only Director can mark as paid. (Limit: {limit})", "danger")
        return redirect(url_for("finance.payments"))

    pr.status = "paid"
    db.session.commit()
    flash("Marked as paid.", "success")
    return redirect(url_for("finance.payments"))
