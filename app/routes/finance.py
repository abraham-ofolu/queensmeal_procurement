import os
from datetime import datetime

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user

from app.extensions import db
from app.models.procurement_request import ProcurementRequest
from app.models.payment import Payment
from app.utils.cloudinary_service import upload_file

finance_bp = Blueprint("finance", __name__, url_prefix="/finance")


def _role() -> str:
    return (getattr(current_user, "role", "") or "").lower()


def _is_finance() -> bool:
    return _role() == "finance"


def _limit() -> float:
    try:
        return float(os.getenv("FINANCE_PAYMENT_LIMIT", "500000"))
    except Exception:
        return 500000.0


@finance_bp.route("/payments", methods=["GET"], endpoint="payments")
@login_required
def payments():
    if _role() not in {"finance", "director"}:
        abort(403)

    payments_list = Payment.query.order_by(Payment.created_at.desc()).all()
    return render_template("finance/payments.html", payments=payments_list, limit=_limit())


@finance_bp.route("/to-pay", methods=["GET"], endpoint="to_pay")
@login_required
def to_pay():
    if not _is_finance():
        abort(403)

    # finance sees approved items within limit (finance is responsible for these)
    reqs = ProcurementRequest.query.filter_by(status="approved").order_by(
        ProcurementRequest.created_at.desc()
    ).all()

    within = [r for r in reqs if float(r.amount or 0) <= _limit()]
    above = [r for r in reqs if float(r.amount or 0) > _limit()]

    return render_template("finance/to_pay.html", within=within, above=above, limit=_limit())


@finance_bp.route("/pay/<int:req_id>", methods=["GET", "POST"], endpoint="pay")
@login_required
def pay(req_id: int):
    """
    Finance payment is ONLY allowed when:
    - request is approved
    - amount is <= finance limit
    """
    if not _is_finance():
        abort(403)

    req_obj = ProcurementRequest.query.get_or_404(req_id)

    if (req_obj.status or "").lower() != "approved":
        flash("Only APPROVED requests can be paid.", "warning")
        return redirect(url_for("finance.to_pay"))

    if float(req_obj.amount or 0) > _limit():
        flash("This request is above the Finance limit. Director must pay it.", "danger")
        return redirect(url_for("finance.to_pay"))

    if request.method == "POST":
        receipt = request.files.get("receipt")
        if not receipt or not receipt.filename:
            flash("Upload a payment receipt.", "danger")
            return redirect(url_for("finance.pay", req_id=req_id))

        receipt_url, receipt_public_id = upload_file(receipt, folder="queensmeal/receipts")

        payment = Payment(
            procurement_request_id=req_obj.id,
            amount=float(req_obj.amount or 0),
            paid_by_role="finance",
            paid_by_name=getattr(current_user, "username", None) or getattr(current_user, "email", None),
            receipt_url=receipt_url,
            receipt_public_id=receipt_public_id,
            status="paid",
            created_at=datetime.utcnow(),
        )
        db.session.add(payment)

        req_obj.status = "paid"
        db.session.commit()

        flash("Payment recorded successfully (Finance).", "success")
        return redirect(url_for("finance.to_pay"))

    return render_template("finance/pay.html", req=req_obj, limit=_limit())
