from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from app.extensions import db
from app.models.procurement_request import ProcurementRequest

director_bp = Blueprint("director", __name__, url_prefix="/director")


@director_bp.route("/approvals")
@login_required
def approvals():
    pending_requests = (
        ProcurementRequest.query
        .filter_by(status="pending")
        .order_by(
            ProcurementRequest.is_urgent.desc(),
            ProcurementRequest.created_at.desc()
        )
        .all()
    )
    return render_template(
        "director/approvals.html",
        requests=pending_requests
    )


@director_bp.route("/approve/<int:request_id>")
@login_required
def approve(request_id):
    req = ProcurementRequest.query.get_or_404(request_id)
    req.status = "approved"
    db.session.commit()
    flash("Procurement approved and sent to Finance.", "success")
    return redirect(url_for("director.approvals"))


@director_bp.route("/reject/<int:request_id>")
@login_required
def reject(request_id):
    req = ProcurementRequest.query.get_or_404(request_id)
    req.status = "rejected"
    db.session.commit()
    flash("Procurement request rejected.", "danger")
    return redirect(url_for("director.approvals"))
