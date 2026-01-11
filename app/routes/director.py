from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.procurement_request import ProcurementRequest
from app.models.approval import ApprovalAction

director_bp = Blueprint("director", __name__, url_prefix="/director")

@director_bp.route("/approvals")
@login_required
def approvals():
    if current_user.role != "director":
        flash("Access denied.")
        return redirect(url_for("procurement.index"))

    requests = ProcurementRequest.query.filter_by(status="pending").all()
    return render_template("director/approvals.html", requests=requests)

@director_bp.route("/approve/<int:request_id>")
@login_required
def approve(request_id):
    if current_user.role != "director":
        flash("Access denied.")
        return redirect(url_for("procurement.index"))

    req = ProcurementRequest.query.get_or_404(request_id)
    req.approve()

    action = ApprovalAction(
        procurement_request_id=req.id,
        actor_id=current_user.id,
        actor_role="director",
        action="approved"
    )

    db.session.add(action)
    db.session.commit()

    flash("Request approved.")
    return redirect(url_for("director.approvals"))

@director_bp.route("/reject/<int:request_id>")
@login_required
def reject(request_id):
    if current_user.role != "director":
        flash("Access denied.")
        return redirect(url_for("procurement.index"))

    req = ProcurementRequest.query.get_or_404(request_id)
    req.reject()

    action = ApprovalAction(
        procurement_request_id=req.id,
        actor_id=current_user.id,
        actor_role="director",
        action="rejected"
    )

    db.session.add(action)
    db.session.commit()

    flash("Request rejected.")
    return redirect(url_for("director.approvals"))
