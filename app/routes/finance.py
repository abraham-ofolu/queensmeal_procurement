from datetime import datetime
from decimal import Decimal

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app.extensions import db
from app.models.procurement_request import ProcurementRequest
from app.models.payment import Payment

try:
    import cloudinary.uploader
    CLOUDINARY_OK = True
except Exception:
    CLOUDINARY_OK = False


finance_bp = Blueprint("finance", __name__, url_prefix="/finance")


def _role():
    return (getattr(current_user, "role", "") or "").lower()


@finance_bp.route("/payments")
@login_required
def payments():
    if _role() not in ["finance", "director"]:
        flash("Access denied.", "danger")
        return redirect(url_for("procurement.index"))

    requests = ProcurementRequest.query.order_by(
        ProcurementRequest.created_at.desc()
    ).all()

    return render_template("finance/payments.html", requests=requests)


@finance_bp.route("/pay/<int:request_id>", methods=["POST"])
@login_required
def pay(request_id):
    req = ProcurementRequest.query.get_or_404(request_id)

    amount_paid = request.form.get("amount_paid")
    receipt = request.files.get("receipt")

    if not amount_paid:
        flash("Amount is required.", "danger")
        return redirect(url_for("finance.payments"))

    receipt_url = None
    receipt_public_id = None

    if receipt and receipt.filename:
        if not CLOUDINARY_OK:
            flash("Receipt upload not available.", "danger")
            return redirect(url_for("finance.payments"))

        res = cloudinary.uploader.upload(
            receipt,
            folder="queensmeal/procurement/receipts",
            resource_type="auto",
        )
        receipt_url = res.get("secure_url")
        receipt_public_id = res.get("public_id")

    payment = Payment(
        procurement_request_id=req.id,
        amount=req.amount,                    # ✅ REQUIRED
        amount_paid=Decimal(amount_paid),
        paid_by_role="finance",
        paid_by_name=current_user.username,
        receipt_url=receipt_url,
        receipt_public_id=receipt_public_id,
        receipt_uploaded_at=datetime.utcnow() if receipt_url else None,
        status="paid",
        created_at=datetime.utcnow(),
        paid_at=datetime.utcnow(),
    )

    try:
        db.session.add(payment)
        req.status = "paid"
        db.session.commit()
        flash("Payment recorded.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Payment failed: {e}", "danger")

    return redirect(url_for("finance.payments"))
