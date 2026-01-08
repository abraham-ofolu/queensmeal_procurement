from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from datetime import datetime
from cloudinary.uploader import upload 

from app.extensions import db
from app.models import ProcurementRequest, Payment

file = request.files.get("receipt")
if file:
    result = upload(file,
                    folder="queensmeal/receipts"
                     )
    receipt_url = result["secure_url"]
else:
    receipt_url = None



# -------------------------------------------------
# BLUEPRINT MUST BE DEFINED FIRST
# -------------------------------------------------
finance_bp = Blueprint("finance", __name__, url_prefix="/finance")

# -------------------------------------------------
# LIST PAYMENTS
# -------------------------------------------------
@finance_bp.route("/payments")
@login_required
def list_payments():
    payments = Payment.query.order_by(Payment.created_at.desc()).all()
    return render_template("finance/payments.html", payments=payments)

# -------------------------------------------------
# CREATE PAYMENT (FROM PROCUREMENT)
# -------------------------------------------------
@finance_bp.route("/payments/create/<int:procurement_id>", methods=["GET", "POST"])
@login_required
def create_payment(procurement_id):
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
