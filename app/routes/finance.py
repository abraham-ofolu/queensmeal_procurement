from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from datetime import datetime

from app.extensions import db
from app.models.payment import Payment
from app.models.procurement_request import ProcurementRequest

finance_bp = Blueprint("finance", __name__, url_prefix="/finance")


@finance_bp.route("/payments")
@login_required
def list_payments():
    payments = Payment.query.order_by(Payment.created_at.desc()).all()
    return render_template("finance/payments.html", payments=payments)


@finance_bp.route("/payments/create/<int:request_id>", methods=["GET", "POST"])
@login_required
def make_payment(request_id):
    pr = ProcurementRequest.query.get_or_404(request_id)

    if request.method == "POST":
        try:
            amount = float(request.form.get("amount"))
            method = request.form.get("method")

            payment = Payment(
                procurement_request_id=pr.id,
                amount=amount,
                method=method,
                paid_by=current_user.username,
                paid_at=datetime.utcnow(),
                created_at=datetime.utcnow(),
            )

            db.session.add(payment)
            db.session.commit()

            flash("Payment recorded successfully", "success")
            return redirect(url_for("finance.list_payments"))

        except Exception as e:
            db.session.rollback()
            flash("Payment failed. Please check inputs.", "danger")

    return render_template("finance/create_payment.html", pr=pr)
