from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime

from app.extensions import db
from app.models.procurement import ProcurementRequest
from app.models.payment import Payment

finance_bp = Blueprint(
    "finance",
    __name__,
    url_prefix="/finance"
)

# =========================
# LIST PAYMENTS / REQUESTS
# =========================
@finance_bp.route("/payments")
@login_required
def payments():
    requests = ProcurementRequest.query.order_by(
        ProcurementRequest.created_at.desc()
    ).all()

    return render_template(
        "finance/payments.html",
        requests=requests
    )

# =========================
# MARK AS PAID
# =========================
@finance_bp.route("/pay/<int:request_id>")
@login_required
def pay_request(request_id):
    req = ProcurementRequest.query.get_or_404(request_id)

    if req.status == "paid":
        flash("This request is already paid", "warning")
        return redirect(url_for("finance.payments"))

    payment = Payment(
        procurement_id=req.id,
        amount=req.amount,
        paid_by=current_user.id,
        status="paid",
        created_at=datetime.utcnow()
    )

    req.status = "paid"

    db.session.add(payment)
    db.session.commit()

    flash("Payment recorded successfully", "success")
    return redirect(url_for("finance.payments"))
