from flask import Blueprint, render_template
from flask_login import login_required

from app.models.payment import Payment

finance_bp = Blueprint(
    "finance",
    __name__,
    url_prefix="/finance"
)

@finance_bp.route("/payments")
@login_required
def payments():
    payments = (
        Payment.query
        .order_by(Payment.created_at.desc())
        .all()
    )

    return render_template(
        "finance/payments.html",
        payments=payments
    )
