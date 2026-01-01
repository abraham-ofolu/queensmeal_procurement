from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import func
from app.extensions import db
from app.models.procurement_request import ProcurementRequest
from app.models.payment import Payment

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/")
@login_required
def home():
    total_requests = db.session.query(func.count(ProcurementRequest.id)).scalar() or 0
    total_request_amount = db.session.query(func.coalesce(func.sum(ProcurementRequest.amount), 0)).scalar() or 0

    total_paid = db.session.query(func.coalesce(func.sum(Payment.amount), 0)).scalar() or 0

    stats = {
        "total_requests": int(total_requests),
        "total_request_amount": float(total_request_amount),
        "total_paid": float(total_paid),
        "outstanding": float(total_request_amount) - float(total_paid),
        "role": getattr(current_user, "role", None),
    }

    return render_template("dashboard/home.html", stats=stats)
