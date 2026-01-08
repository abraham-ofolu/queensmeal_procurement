@finance_bp.route("/payments/create/<int:procurement_id>", methods=["GET", "POST"])
@login_required
def create_payment(procurement_id):
    from app.models import ProcurementRequest, Payment
    from app.extensions import db
    from datetime import datetime

    pr = ProcurementRequest.query.get_or_404(procurement_id)

    if request.method == "POST":
        payment = Payment(
            procurement_id=pr.id,
            amount=pr.amount,
            method=request.form.get("method"),
            reference=request.form.get("reference"),
            created_at=datetime.utcnow()
        )

        db.session.add(payment)
        db.session.commit()

        flash("Payment recorded successfully", "success")
        return redirect(url_for("finance.list_payments"))

    return render_template(
        "finance/create_payment.html",
        pr=pr
    )
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required