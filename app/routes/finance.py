import os
from datetime import datetime
from decimal import Decimal

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


def _role() -> str:
    return (getattr(current_user, "role", "") or "").lower()


def _require_role(*roles) -> bool:
    if _role() not in [r.lower() for r in roles]:
        flash("You are not allowed to access that page.", "danger")
        return False
    return True


def _finance_limit() -> Decimal:
    # Set this on Render as env var if you want:
    # FINANCE_PAYMENT_LIMIT=200000
    raw = os.environ.get("FINANCE_PAYMENT_LIMIT", "200000")
    try:
        return Decimal(str(raw).replace(",", "").strip())
    except Exception:
        return Decimal("200000")


@finance_bp.route("/payments")
@login_required
def payments():
    if not _require_role("finance"):
        return redirect(url_for("procurement.index"))

    limit = _finance_limit()

    # Show APPROVED requests that are NOT PAID and within finance limit
    payable_requests = (
        ProcurementRequest.query
        .filter(ProcurementRequest.status == "approved")
        .order_by(ProcurementRequest.created_at.desc())
        .all()
    )

    payable_requests = [r for r in payable_requests if (r.amount or 0) <= limit]

    # Recent payments list
    recent_payments = (
        Payment.query
        .order_by(Payment.paid_at.desc().nullslast(), Payment.created_at.desc())
        .limit(50)
        .all()
    )

    return render_template(
        "finance/payments.html",
        payable_requests=payable_requests,
        recent_payments=recent_payments,
        limit=limit
    )


@finance_bp.route("/pay/<int:request_id>", methods=["GET", "POST"])
@login_required
def pay(request_id: int):
    if not _require_role("finance"):
        return redirect(url_for("procurement.index"))

    req = ProcurementRequest.query.get_or_404(request_id)
    limit = _finance_limit()

    # Only approved can be paid
    if req.status != "approved":
        flash("Only APPROVED requests can be paid.", "warning")
        return redirect(url_for("finance.payments"))

    # Finance limit enforcement
    if (req.amount or 0) > limit:
        flash("This request is above Finance limit. Director must pay.", "danger")
        return redirect(url_for("finance.payments"))

    if request.method == "POST":
        # default pay amount = request amount
        amount_paid = Payment.normalize_amount(request.form.get("amount_paid") or req.amount)
        notes = (request.form.get("notes") or "").strip() or None
        receipt_file = request.files.get("receipt")

        receipt_url = None
        receipt_public_id = None
        receipt_uploaded_at = None

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
                    receipt_public_id = res.get("public_id")
                    receipt_uploaded_at = datetime.utcnow()
                except Exception as e:
                    flash(f"Receipt upload failed: {e}", "danger")
                    return redirect(url_for("finance.pay", request_id=req.id))

        # Create payment record
        try:
            payer_name = getattr(current_user, "username", None) or getattr(current_user, "name", None) or "finance"
            payment = Payment(
                procurement_request_id=req.id,

                # Your DB requires `amount` NOT NULL
                amount=amount_paid,

                # Keep also `amount_paid` for the newer design
                amount_paid=amount_paid,

                paid_by_role="finance",
                paid_by_name=str(payer_name),

                paid_by_user_id=getattr(current_user, "id", None),

                receipt_url=receipt_url,
                receipt_public_id=receipt_public_id,
                receipt_uploaded_at=receipt_uploaded_at,

                notes=notes,
                status="paid",
                paid_at=datetime.utcnow(),
                created_at=datetime.utcnow(),
            )

            db.session.add(payment)

            # Update request status
            req.status = "paid"
            db.session.commit()

            flash("Payment saved successfully.", "success")
            return redirect(url_for("finance.payments"))

        except Exception as e:
            db.session.rollback()
            flash(f"Could not save payment: {e}", "danger")
            return redirect(url_for("finance.pay", request_id=req.id))

    return render_template("finance/pay.html", req=req, limit=limit, payer_role="finance")
