import os
from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, request, send_from_directory, abort
)
from flask_login import login_required, current_user
from app import db
from app.models import ProcurementRequest, AuditLog
from app.utils.cloudinary import upload_file, delete_file

procurement_bp = Blueprint("procurement", __name__, url_prefix="/procurement")


@procurement_bp.route("/")
@login_required
def list_requests():
    requests = ProcurementRequest.query.order_by(ProcurementRequest.created_at.desc()).all()
    return render_template("procurement/list.html", requests=requests)


@procurement_bp.route("/<int:request_id>")
@login_required
def view_request(request_id):
    pr = ProcurementRequest.query.get_or_404(request_id)
    return render_template("procurement/view.html", pr=pr)


@procurement_bp.route("/upload-quotation/<int:request_id>", methods=["POST"])
@login_required
def upload_quotation(request_id):
    if current_user.role != "procurement":
        abort(403)

    pr = ProcurementRequest.query.get_or_404(request_id)

    file = request.files.get("quotation")
    if not file:
        flash("No file selected", "danger")
        return redirect(url_for("procurement.view_request", request_id=request_id))

    # delete old quotation if exists
    if pr.quotation:
        delete_file(pr.quotation)

    url = upload_file(file, folder="quotations")

    pr.quotation = url
    db.session.add(AuditLog(
        user_id=current_user.id,
        action="UPLOAD_QUOTATION",
        entity="ProcurementRequest",
        entity_id=pr.id
    ))
    db.session.commit()

    flash("Quotation uploaded successfully", "success")
    return redirect(url_for("procurement.view_request", request_id=request_id))


@procurement_bp.route("/delete-quotation/<int:request_id>", methods=["POST"])
@login_required
def delete_quotation(request_id):
    if current_user.role != "procurement":
        abort(403)

    pr = ProcurementRequest.query.get_or_404(request_id)

    if pr.quotation:
        delete_file(pr.quotation)
        pr.quotation = None

        db.session.add(AuditLog(
            user_id=current_user.id,
            action="DELETE_QUOTATION",
            entity="ProcurementRequest",
            entity_id=pr.id
        ))
        db.session.commit()

    flash("Quotation deleted", "success")
    return redirect(url_for("procurement.view_request", request_id=request_id))
