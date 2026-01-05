from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy import func

from app.extensions import db
from app.models.procurement_request import ProcurementRequest
from app.models.payment import Payment

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


@reports_bp.route("/")
@login_required
def index():

    # ---- PROCUREMENT STATS ----
    total_requests = db.session.query(func.count(ProcurementRequest.id)).scalar() or 0

    approved_count = db.session.query(func.count(ProcurementRequest.id)) \
        .filter(ProcurementRequest.status == "approved").scalar() or 0

    pending_count = db.session.query(func.count(ProcurementRequest.id)) \
        .filter(ProcurementRequest.status == "pending").scalar() or 0

    rejected_count = db.session.query(func.count(ProcurementRequest.id)) \
        .filter(ProcurementRequest.status == "rejected").scalar() or 0

    total_requested_amount = db.session.query(func.coalesce(func.sum(ProcurementRequest.amount), 0)).scalar()

    # ---- PAYMENT STATS ----
    total_paid = db.session.query(func.coalesce(func.sum(Payment.amount), 0)).scalar()

    return render_template(
        "reports/index.html",
        total_requests=total_requests,
        approved_count=approved_count,
        pending_count=pending_count,
        rejected_count=rejected_count,
        total_requested_amount=total_requested_amount,
        total_paid=total_paid,
    )
