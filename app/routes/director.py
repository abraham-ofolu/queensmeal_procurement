from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.procurement_request import ProcurementRequest
from app.extensions import db

director_bp = Blueprint("director", __name__, url_prefix="/director")


def director_only():
    return current_user.is_authenticated and current_user.role == "DIRECTOR"


@director_bp.route("/approvals")
@login_required
def approvals():
    if not director_only():
        flash("Access denied.", "danger")
        return redirect(url_for("procurement.index"))

    requests = ProcurementRequest.query.filter_by(
        status="PROCUREMENT_APPROVED"
    ).order_by(ProcurementRequest.created_at.desc()).all()

    return render_template("director/approvals.html", requests=requests)


@director_bp.route("/approve/<int:request_id>")
@login_required
def approve(request_id):
    if not director_only():
        flash("Access denied.", "danger")
        return redirect(url_for("procurement.index"))

    req = ProcurementRequest.query.get_or_404(request_id)
    req.status = "DIRECTOR_APPROVED"
    db.session.commit()

    flash("Request approved by Director.", "success")
    return redirect(url_for("director.approvals"))


@director_bp.route("/reject/<int:request_id>")
@login_required
def reject(request_id):
    if not director_only():
        flash("Access denied.", "danger")
        return redirect(url_for("procurement.index"))

    req = ProcurementRequest.query.get_or_404(request_id)
    req.status = "REJECTED"
    db.session.commit()

    flash("Request rejected.", "warning")
    return redirect(url_for("director.approvals"))
