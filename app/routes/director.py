from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app.extensions import db
from app.models.procurement_request import ProcurementRequest
from app.models.payment import Payment

director_bp = Blueprint("director", __name__, url_prefix="/director")


def _role():
    return (getattr(current_user, "role", "") or "").lower()


@director_bp.route("/approvals")
@login_required
def approvals():
    if _role() != "director":
        flash("Access denied.", "danger")
        return redirect(url_for("procurement.index"))

    requests = ProcurementRequest.query.order_by(
        ProcurementRequest.created_at.desc()
    ).all()

    return render_template(
        "director/approvals.html",
        requests=requests,
    )


@director_bp.route("/approve/<int:request_id>", methods=["POST"])
@login_required
def approve(request_id):
    if _role() != "director":
        flash("Access denied.", "danger")
        return redirect(url_for("director.approvals"))

    req = ProcurementRequest.query.get_or_404(request_id)
    req.status = "approved"
    db.session.commit()

    flash("Request approved.", "success")
    return redirect(url_for("director.approvals"))


@director_bp.route("/pay/<int:request_id>", methods=["POST"])
@login_required
def director_pay(request_id):
    if _role() != "director":
        flash("Access denied.", "danger")
        return redirect(url_for("director.approvals"))

    amount_paid = request.form.get("amount_paid")

    if not amount_paid:
        flash("Amount is required.", "danger")
        return redirect(url_for("director.approvals"))

    req = ProcurementRequest.query.get_or_404(request_id)

    payment = Payment(
        procurement_request_id=req.id,
        amount_paid=amount_paid,
        paid_by_role="director",
        paid_by_name=current_user.username,
        status="paid",
        paid_at=datetime.utcnow(),
    )

    try:
        db.session.add(payment)
        req.status = "paid"
        db.session.commit()
        flash("Payment completed.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Payment failed: {e}", "danger")

    return redirect(url_for("director.approvals"))
