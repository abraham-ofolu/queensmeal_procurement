from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app.extensions import db
from app.models.procurement_request import ProcurementRequest

director_bp = Blueprint("director", __name__, url_prefix="/director")


def _role():
    return (getattr(current_user, "role", "") or "").lower()


@director_bp.route("/approvals")
@login_required
def approvals():
    if _role() != "director":
        flash("Access denied.", "danger")
        return redirect(url_for("procurement.index"))

    requests = ProcurementRequest.query.filter(
        ProcurementRequest.status == "pending"
    ).order_by(ProcurementRequest.created_at.desc()).all()

    return render_template("director/approvals.html", requests=requests)


@director_bp.route("/approve/<int:request_id>")
@login_required
def approve(request_id):
    if _role() != "director":
        flash("Access denied.", "danger")
        return redirect(url_for("procurement.index"))

    req = ProcurementRequest.query.get_or_404(request_id)
    req.status = "approved"
    db.session.commit()

    flash("Request approved.", "success")
    return redirect(url_for("director.approvals"))


@director_bp.route("/reject/<int:request_id>")
@login_required
def reject(request_id):
    if _role() != "director":
        flash("Access denied.", "danger")
        return redirect(url_for("procurement.index"))

    req = ProcurementRequest.query.get_or_404(request_id)
    req.status = "rejected"
    db.session.commit()

    flash("Request rejected.", "warning")
    return redirect(url_for("director.approvals"))
