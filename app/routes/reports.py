from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy import func

from app.extensions import db
from app.models.procurement import ProcurementRequest

reports_bp = Blueprint("reports", __name__)

@reports_bp.route("/")
@login_required
def index():
    total_requests = ProcurementRequest.query.count()

    total_requested_amount = (
        db.session.query(
            func.coalesce(func.sum(ProcurementRequest.amount), 0)
        ).scalar()
    )

    return render_template(
        "reports/index.html",
        total_requests=total_requests,
        total_requested_amount=total_requested_amount,
    )
