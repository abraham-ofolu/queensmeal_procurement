import os
from decimal import Decimal
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


director_bp = Blueprint("director", __name__, url_prefix="/director")


def _role():
    return (getattr(current_user, "role", "") or "").lower()


def _finance_limit():
    raw = os.getenv("FINANCE_PAYMENT_LIMIT", "500000")
    try:
        return Decimal(raw)
    except Exception:
        return Decimal("500000")


@director_bp.route("/approvals")
@login_required
def approvals():
    if _role() != "director":
        flash("Access denied.", "danger")
        return redirect(url_for("procurement.index"))

    requests_list = ProcurementRequest.query.order_by(
        ProcurementRequest.created_at.desc()
    ).all()

    return render_template(
        "director/approvals.html",
        requests=requests_list,
        finance_limit=_finance_limit()
    )


@director_bp.route("/approve/<int:request_id>")
@login_required
def approve(request_id):
    if _role() != "director":
        flash("Access denied.", "danger")
        return redirect(url_for("procurement.index"))

    req = ProcurementRequest.query.get_or_404(request_id)
    if req.status != "pending":
        flash("Only PENDING requests can be approved.", "warning")
        return redirect(url_for("director.approvals"))

    req.status = "approved"
    db.session.commit()

    flash("Request approved.", "success")
    return redirect(url_for("director.approvals"))


@director_bp.route("/reject/<int:request_id>")
@login_required
def reject(request_id):
    if _role() != "director":
        flash("Access denied.", "danger")
        return redirect(url_for("procurement.index"))

    req = ProcurementRequest.query.get_or_404(request_id)
    if req.status != "pending":
        flash("Only PENDING requests can be rejected.", "warning")
        return redirect(url_for("director.approvals"))

    req.status = "rejected"
    db.session.commit()

    flash("Request rejected.", "warning")
    return redirect(url_for("director.approvals"))


@director_bp.route("/pay/<int:request_id>", methods=["POST"])
@login_required
def pay(request_id):
    if _role() != "director":
        flash("Access denied.", "danger")
        return redirect(url_for("procurement.index"))

    req = ProcurementRequest.query.get_or_404(request_id)

    if req.status != "approved":
        flash("Only APPROVED requests can be paid.", "danger")
        return redirect(url_for("director.approvals"))

    try:
        req_amount = Decimal(str(req.amount))
    except Exception:
        flash("Invalid request amount.", "danger")
        return redirect(url_for("director.approvals"))

    # Enforce rule: Director pays ONLY above finance limit
    if req_amount <= _finance_limit():
        flash("This request is within Finance limit. Finance should pay this one.", "warning")
        return redirect(url_for("director.approvals"))

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
                return redirect(url_for("director.approvals"))

    try:
        payment = Payment(
            procurement_request_id=req.id,
            amount_paid=req_amount,
            paid_by_user_id=getattr(current_user, "id", None),
            paid_by_role="director",
            receipt_url=receipt_url,
            receipt_uploaded_at=datetime.utcnow() if receipt_url else None,
            notes=notes,
            paid_at=datetime.utcnow(),
        )
        db.session.add(payment)

        req.status = "paid"

        db.session.commit()
        flash("Director payment recorded and request marked as PAID.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Could not save payment: {e}", "danger")

    return redirect(url_for("director.approvals"))
