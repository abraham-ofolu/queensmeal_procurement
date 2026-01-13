from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.extensions import db
from app.models.procurement_request import ProcurementRequest

finance_bp = Blueprint("finance", __name__, url_prefix="/finance")

FINANCE_LIMIT = 500000


@finance_bp.route("/payments")
@login_required
def payments():
    payments_list = (
        ProcurementRequest.query
        .filter_by(status="approved")
        .order_by(ProcurementRequest.created_at.desc())
        .all()
    )
    return render_template(
        "finance/payments.html",
        payments=payments_list,
        limit=FINANCE_LIMIT
    )


@finance_bp.route("/pay/<int:request_id>", methods=["POST"])
@login_required
def pay(request_id):
    req = ProcurementRequest.query.get_or_404(request_id)

    if req.amount > FINANCE_LIMIT:
        flash("Amount exceeds Finance limit. Director payment required.", "danger")
        return redirect(url_for("finance.payments"))
    


    req.status = "paid"
    db.session.commit()
    flash("Payment completed successfully.", "success")
    return redirect(url_for("finance.payments"))
