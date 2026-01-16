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


director_bp = Blueprint("director", __name__, url_prefix="/director")


def _role() -> str:
    return (getattr(current_user, "role", "") or "").lower()


def _require_role(*roles) -> bool:
    if _role() not in [r.lower() for r in roles]:
        flash("You are not allowed to access that page.", "danger")
        return False
    return True


@director_bp.route("/approvals")
@login_required
def approvals():
    if not _require_role("director"):
        return redirect(url_for("procurement.index"))

    pending = (
        ProcurementRequest.query
        .filter(ProcurementRequest.status == "pending")
        .order_by(ProcurementRequest.created_at.desc())
        .all()
    )

    approved_unpaid = (
        ProcurementRequest.query
        .filter(ProcurementRequest.status == "approved")
        .order_by(ProcurementRequest.created_at.desc())
        .all()
    )

    return render_template(
        "director/approvals.html",
        pending=pending,
        approved_unpaid=approved_unpaid
    )


@director_bp.route("/approve/<int:request_id>", methods=["POST"])
@login_required
def approve(request_id: int):
    if not _require_role("director"):
        return redirect(url_for("procurement.index"))

    req = ProcurementRequest.query.get_or_404(request_id)

    if req.status != "pending":
        flash("Only PENDING requests can be approved.", "warning")
        return redirect(url_for("director.approvals"))

    try:
        req.status = "approved"
        db.session.commit()
        flash("Request approved.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Could not approve request: {e}", "danger")

    return redirect(url_for("director.approvals"))


@director_bp.route("/reject/<int:request_id>", methods=["POST"])
@login_required
def reject(request_id: int):
    if not _require_role("director"):
        return redirect(url_for("procurement.index"))

    req = ProcurementRequest.query.get_or_404(request_id)

    if req.status != "pending":
        flash("Only PENDING requests can be rejected.", "warning")
        return redirect(url_for("director.approvals"))

    try:
        req.status = "rejected"
        db.session.commit()
        flash("Request rejected.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Could not reject request: {e}", "danger")

    return redirect(url_for("director.approvals"))


@director_bp.route("/pay/<int:request_id>", methods=["GET", "POST"])
@login_required
def pay(request_id: int):
    if not _require_role("director"):
        return redirect(url_for("procurement.index"))

    req = ProcurementRequest.query.get_or_404(request_id)

    if req.status != "approved":
        flash("Only APPROVED requests can be paid.", "warning")
        return redirect(url_for("director.approvals"))

    if request.method == "POST":
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
                    return redirect(url_for("director.pay", request_id=req.id))

        try:
            payer_name = getattr(current_user, "username", None) or getattr(current_user, "name", None) or "director"
            payment = Payment(
                procurement_request_id=req.id,
                amount=amount_paid,
                amount_paid=amount_paid,

                paid_by_role="director",
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
            req.status = "paid"
            db.session.commit()

            flash("Director payment saved successfully.", "success")
            return redirect(url_for("director.approvals"))

        except Exception as e:
            db.session.rollback()
            flash(f"Could not save payment: {e}", "danger")
            return redirect(url_for("director.pay", request_id=req.id))

    # Reuse finance pay template to keep things consistent
    return render_template("finance/pay.html", req=req, limit=None, payer_role="director")
