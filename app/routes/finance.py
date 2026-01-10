from flask import Blueprint, render_template
from flask_login import login_required, current_user

from app.extensions import db
from app.models.payment import Payment
from app.models.procurement import ProcurementRequest

finance_bp = Blueprint(
    "finance",
    __name__,
    url_prefix="/finance"
)

@finance_bp.route("/payments", methods=["GET"])
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
