from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime

from app.extensions import db
from app.models.payment import Payment
from app.models.procurement import ProcurementRequest

finance_bp = Blueprint(
    "finance",
    __name__,
    url_prefix="/finance"
)


@finance_bp.route("/payments")
@login_required
def payments():
    payments = Payment.query.order_by(
        Payment.created_at.desc()
    ).all()

    return render_template(
        "finance/payments.html",
        payments=payments
    )


@finance_bp.route("/pay/<int:procurement_id>")
@login_required
def pay_request(procurement_id):
    req = ProcurementRequest.query.get_or_404(procurement_id)

    # 🔒 Block double payment
    existing = Payment.query.filter_by(
        procurement_id=req.id
    ).first()
    if existing:
        flash("This request has already been paid.", "warning")
        return redirect(url_for("finance.payments"))

    payment = Payment(
        procurement_id=req.id,
        amount=req.amount,
        paid_by=current_user.role
    )

    req.status = "paid"

    db.session.add(payment)
    db.session.commit()

    flash("Payment recorded successfully.", "success")
    return redirect(url_for("finance.payments"))
