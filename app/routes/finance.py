from flask import Blueprint, render_template
from flask_login import login_required
from app.models.payment import Payment

finance_bp = Blueprint("finance", __name__, url_prefix="/finance")

@finance_bp.route("/payments")
@login_required
def list_payments():
    payments = Payment.query.all()
    return render_template("finance/payments.html", payments=payments)
