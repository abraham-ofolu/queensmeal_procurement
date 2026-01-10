from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app.extensions import db
from app.models.payment import Payment

finance_bp = Blueprint(
    "finance",
    __name__,
    url_prefix="/finance"
)


# =========================
# ROLE GUARD
# =========================
def finance_only():
    if current_user.role != "finance":
        flash("You are not authorised to access Finance pages.", "danger")
        return False
    return True


# =========================
# FINANCE DASHBOARD
# =========================
@finance_bp.route("/payments", methods=["GET"])
@login_required
def payments():
    if not finance_only():
        return redirect(url_for("procurement.index"))

    payments = Payment.query.order_by(
        Payment.created_at.desc()
    ).all()

    return render_template(
        "finance/payments.html",
        payments=payments
    )
