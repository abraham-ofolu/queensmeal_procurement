import os
from datetime import datetime

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user

from app.extensions import db
from app.models.procurement_request import ProcurementRequest
from app.models.payment import Payment
from app.utils.cloudinary_service import upload_file

director_bp = Blueprint("director", __name__, url_prefix="/director")


def _role() -> str:
    return (getattr(current_user, "role", "") or "").lower()


def _is_director() -> bool:
    return _role() == "director"


def _limit() -> float:
    # Finance can pay up to this amount; director pays above this amount
    try:
        return float(os.getenv("FINANCE_PAYMENT_LIMIT", "500000"))
    except Exception:
        return 500000.0


@director_bp.route("/approvals", methods=["GET"], endpoint="approvals")
@login_required
def approvals():
    if not _is_director():
        abort(403)

    pending = ProcurementRequest.query.filter_by(status="pending_director").order_by(
        ProcurementRequest.created_at.desc()
    ).all()

    approved = ProcurementRequest.query.filter_by(status="approved").order_by(
        ProcurementRequest.created_at.desc()
    ).all()

    return render_template(
        "director/approvals.html",
        pending=pending,
        approved=approved,
        limit=_limit(),
    )


@director_bp.route("/approve/<int:req_id>", methods=["POST"], endpoint="approve")
@login_required
def approve(req_id: int):
    if not _is_director():
        abort(403)

    req_obj = ProcurementRequest.query.get_or_404(req_id)
    if (req_obj.status or "").lower() != "pending_director":
        flash("This request is not awaiting director approval.", "warning")
        return redirect(url_for("director.approvals"))

    req_obj.status = "approved"
    db.session.commit()

    flash("Request approved.", "success")
    return redirect(url_for("director.approvals"))


@director_bp.route("/reject/<int:req_id>", methods=["POST"], endpoint="reject")
@login_required
def reject(req_id: int):
    if not _is_director():
        abort(403)

    req_obj = ProcurementRequest.query.get_or_404(req_id)
    if (req_obj.status or "").lower() != "pending_director":
        flash("This request is not awaiting director approval.", "warning")
        return redirect(url_for("director.approvals"))

    req_obj.status = "rejected"
    db.session.commit()

    flash("Request rejected.", "success")
    return redirect(url_for("director.approvals"))


@director_bp.route("/pay/<int:req_id>", methods=["GET", "POST"], endpoint="pay")
@login_required
def pay(req_id: int):
    """
    Director payment is ONLY allowed when:
    - request is approved
    - amount is ABOVE finance limit
    """
    if not _is_director():
        abort(403)

    req_obj = ProcurementRequest.query.get_or_404(req_id)

    if (req_obj.status or "").lower() != "approved":
        flash("Only APPROVED requests can be paid.", "warning")
        return redirect(url_for("director.approvals"))

    if float(req_obj.amount or 0) <= _limit():
        flash("This request is within Finance limit. Finance must pay it.", "danger")
        return redirect(url_for("director.approvals"))

    if request.method == "POST":
        receipt = request.files.get("receipt")
        if not receipt or not receipt.filename:
            flash("Upload a payment receipt.", "danger")
            return redirect(url_for("director.pay", req_id=req_id))

        receipt_url, receipt_public_id = upload_file(receipt, folder="queensmeal/receipts")

        payment = Payment(
            procurement_request_id=req_obj.id,
            amount=float(req_obj.amount or 0),
            paid_by_role="director",
            paid_by_name=getattr(current_user, "username", None) or getattr(current_user, "email", None),
            receipt_url=receipt_url,
            receipt_public_id=receipt_public_id,
            status="paid",
            created_at=datetime.utcnow(),
        )
        db.session.add(payment)

        req_obj.status = "paid"
        db.session.commit()

        flash("Payment recorded successfully (Director).", "success")
        return redirect(url_for("director.approvals"))

    return render_template("director/pay.html", req=req_obj, limit=_limit())
