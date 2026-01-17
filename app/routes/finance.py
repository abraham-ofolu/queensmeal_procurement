from datetime import datetime
from decimal import Decimal

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app.extensions import db
from app.models.procurement_request import ProcurementRequest
from app.models.payment import Payment

finance_bp = Blueprint("finance", __name__, url_prefix="/finance")


def _role():
    return (getattr(current_user, "role", "") or "").lower()


@finance_bp.route("/payments")
@login_required
def payments():
    if _role() not in ["finance", "director"]:
        flash("Access denied.", "danger")
        return redirect(url_for("procurement.index"))

    requests = ProcurementRequest.query.order_by(
        ProcurementRequest.created_at.desc()
    ).all()

    return render_template(
        "finance/payments.html",
        requests=requests,
    )


@finance_bp.route("/pay/<int:request_id>", methods=["POST"])
@login_required
def pay(request_id):
    if _role() not in ["finance", "director"]:
        flash("Access denied.", "danger")
        return redirect(url_for("finance.payments"))

    req = ProcurementRequest.query.get_or_404(request_id)

    amount_paid = request.form.get("amount_paid")
    notes = request.form.get("notes")

    if not amount_paid:
        flash("Amount is required.", "danger")
        return redirect(url_for("finance.payments"))

    payment = Payment(
        procurement_request_id=req.id,
        amount_paid=Decimal(amount_paid),
        paid_by_role=_role(),
        paid_by_name=current_user.username,
        status="paid",
        paid_at=datetime.utcnow(),
        notes=notes,
    )

    try:
        db.session.add(payment)
        req.status = "paid"
        db.session.commit()
        flash("Payment recorded successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Could not save payment: {e}", "danger")

    return redirect(url_for("finance.payments"))
