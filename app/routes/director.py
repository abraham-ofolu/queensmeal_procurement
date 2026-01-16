from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app.extensions import db
from app.models.procurement_request import ProcurementRequest

director_bp = Blueprint("director", __name__, url_prefix="/director")


def _role() -> str:
    return (getattr(current_user, "role", "") or "").lower()


def _require_director() -> bool:
    return _role() == "director"


@director_bp.route("/approvals", methods=["GET"])
@login_required
def approvals():
    if not _require_director():
        flash("Only Director can access approvals.", "danger")
        return redirect(url_for("procurement.index"))

    pending = (
        ProcurementRequest.query.filter_by(status="pending")
        .order_by(ProcurementRequest.created_at.desc())
        .all()
    )
    return render_template("director/approvals.html", requests=pending)


@director_bp.route("/approve/<int:req_id>", methods=["POST"])
@login_required
def approve(req_id: int):
    if not _require_director():
        flash("Only Director can approve.", "danger")
        return redirect(url_for("director.approvals"))

    pr = ProcurementRequest.query.get_or_404(req_id)

    if pr.status != "pending":
        flash("Only pending requests can be approved.", "warning")
        return redirect(url_for("director.approvals"))

    pr.status = "approved"
    db.session.commit()
    flash("Request approved.", "success")
    return redirect(url_for("director.approvals"))


@director_bp.route("/reject/<int:req_id>", methods=["POST"])
@login_required
def reject(req_id: int):
    if not _require_director():
        flash("Only Director can reject.", "danger")
        return redirect(url_for("director.approvals"))

    pr = ProcurementRequest.query.get_or_404(req_id)

    if pr.status != "pending":
        flash("Only pending requests can be rejected.", "warning")
        return redirect(url_for("director.approvals"))

    pr.status = "rejected"
    db.session.commit()
    flash("Request rejected.", "success")
    return redirect(url_for("director.approvals"))
