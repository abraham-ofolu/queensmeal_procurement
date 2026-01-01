from flask import Blueprint, render_template
from flask_login import login_required
from app.models.payment import Payment
from app.utils.permissions import require_roles

payments_bp = Blueprint(
    "payments",
    __name__,
    url_prefix="/finance/payments"
)


@payments_bp.route("/")
@login_required
@require_roles("finance", "director")
def list_payments():

    payments = (
        Payment
        .query
        .order_by(Payment.paid_at.desc())
        .all()
    )

    return render_template(
        "payments/list.html",
        payments=payments
    )
