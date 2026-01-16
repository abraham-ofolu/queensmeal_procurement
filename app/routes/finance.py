import os
from decimal import Decimal, InvalidOperation
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app.extensions import db
from app.models.procurement_request import ProcurementRequest
from app.models.payment import Payment

# Optional: Cloudinary receipt upload (won't break app if Cloudinary isn't installed)
try:
    import cloudinary.uploader
    CLOUDINARY_OK = True
except Exception:
    CLOUDINARY_OK = False


finance_bp = Blueprint("finance", __name__, url_prefix="/finance")


def _role():
    return (getattr(current_user, "role", "") or "").lower()


def _finance_limit():
    # You can set this in Render ENV as FINANCE_PAYMENT_LIMIT (example: 500000)
    raw = os.getenv("FINANCE_PAYMENT_LIMIT", "500000")
    try:
        return Decimal(raw)
    except Exception:
        return Decimal("500000")


@finance_bp.route("/payments", methods=["GET"])
@login_required
def payments():
    if _role() != "finance":
        flash("Access denied.", "danger")
        return redirect(url_for("procurement.index"))

    approved = ProcurementRequest.query.filter(
        ProcurementRequest.status == "approved"
    ).order_by(ProcurementRequest.created_at.desc()).all()

    return render_template(
        "finance/payments.html",
        requests=approved,
        finance_limit=_finance_limit()
    )


@finance_bp.route("/pay/<int:request_id>", methods=["POST"])
@login_required
def pay(request_id):
    if _role() != "finance":
        flash("Access denied.", "danger")
        return redirect(url_for("procurement.index"))

    req = ProcurementRequest.query.get_or_404(request_id)

    if req.status != "approved":
        flash("Only APPROVED requests can be paid.", "danger")
        return redirect(url_for("finance.payments"))

    # enforce finance limit
    try:
        req_amount = Decimal(str(req.amount))
    except Exception:
        flash("Invalid request amount.", "danger")
        return redirect(url_for("finance.payments"))

    if req_amount > _finance_limit():
        flash("This request is ABOVE Finance limit. Director must pay.", "warning")
        return redirect(url_for("finance.payments"))

    receipt_file = request.files.get("receipt")
    notes = (request.form.get("notes") or "").strip() or None

    receipt_url = None
    if receipt_file and receipt_file.filename:
        if not CLOUDINARY_OK:
            flash("Receipt upload not available (Cloudinary not configured).", "warning")
        else:
            try:
                res = cloudinary.uploader.upload(
                    receipt_file,
                    resource_type="auto",
                    folder="queensmeal/procurement/receipts"
                )
                receipt_url = res.get("secure_url")
            except Exception as e:
                flash(f"Receipt upload failed: {e}", "danger")
                return redirect(url_for("finance.payments"))

    try:
        payment = Payment(
            procurement_request_id=req.id,
            amount_paid=req_amount,
            paid_by_user_id=getattr(current_user, "id", None),
            paid_by_role="finance",
            receipt_url=receipt_url,
            receipt_uploaded_at=datetime.utcnow() if receipt_url else None,
            notes=notes,
            paid_at=datetime.utcnow(),
        )
        db.session.add(payment)

        # Mark request as PAID
        req.status = "paid"

        db.session.commit()
        flash("Payment recorded and request marked as PAID.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Could not save payment: {e}", "danger")

    return redirect(url_for("finance.payments"))
