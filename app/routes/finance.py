from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models.payment import Payment
from app.models.procurement_request import ProcurementRequest

finance_bp = Blueprint("finance", __name__, url_prefix="/finance")


@finance_bp.route("/payments")
@login_required
def list_payments():
    payments = Payment.query.order_by(Payment.created_at.desc()).all()
    return render_template("finance/payments_list.html", payments=payments)


@finance_bp.route("/payments/create/<int:procurement_id>", methods=["GET", "POST"])
@login_required
def make_payment(procurement_id):
    pr = ProcurementRequest.query.get_or_404(procurement_id)

    if request.method == "POST":
        amount = float(request.form.get("amount", 0))
        method = request.form.get("method")
        description = request.form.get("description") or "Payment recorded"
        reference = request.form.get("reference") or None

        payment = Payment(
            procurement_request_id=pr.id,
            amount=amount,
            method=method,
            description=description,   # 🔒 NEVER NULL
            reference=reference,
            paid_by=current_user.role,
            paid_at=datetime.utcnow()
        )

        db.session.add(payment)
        db.session.commit()

        flash("Payment recorded successfully", "success")
        return redirect(url_for("procurement.view_request", request_id=pr.id))

    return render_template("finance/pay.html", pr=pr)
