from flask import Blueprint, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.procurement_request import ProcurementRequest
from app.models.approval import ApprovalAction

director_bp = Blueprint("director", __name__, url_prefix="/director")


def director_only():
    return current_user.role == "director"


@director_bp.route("/approve/<int:request_id>")
@login_required
def approve(request_id):
    if not director_only():
        flash("Unauthorized", "danger")
        return redirect(url_for("procurement.index"))

    req = ProcurementRequest.query.get_or_404(request_id)
    req.status = "approved"

    db.session.add(ApprovalAction(
        procurement_request_id=req.id,
        actor=current_user.username,
        action="approved"
    ))

    db.session.commit()
    flash("Request approved", "success")
    return redirect(url_for("procurement.index"))


@director_bp.route("/reject/<int:request_id>")
@login_required
def reject(request_id):
    if not director_only():
        flash("Unauthorized", "danger")
        return redirect(url_for("procurement.index"))

    req = ProcurementRequest.query.get_or_404(request_id)
    req.status = "rejected"

    db.session.add(ApprovalAction(
        procurement_request_id=req.id,
        actor=current_user.username,
        action="rejected"
    ))

    db.session.commit()
    flash("Request rejected", "warning")
    return redirect(url_for("procurement.index"))
