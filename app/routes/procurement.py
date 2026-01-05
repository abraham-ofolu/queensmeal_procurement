# app/routes/procurement.py
import os
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, send_from_directory
from flask_login import login_required, current_user

from app.extensions import db
from app.constants import FINANCE_LIMIT
from app.models.procurement_request import ProcurementRequest
from app.models.audit_log import AuditLog
from app.models.vendor import Vendor  # assumes you have app/models/vendor.py

procurement_bp = Blueprint("procurement", __name__, url_prefix="/procurement")


def _log(action, entity_type=None, entity_id=None, details=None):
    db.session.add(
        AuditLog(
            username=getattr(current_user, "username", None),
            role=getattr(current_user, "role", None),
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
        )
    )


@procurement_bp.route("/")
@login_required
def list_requests():
    requests_q = ProcurementRequest.query.order_by(ProcurementRequest.created_at.desc()).all()
    return render_template("procurement/list.html", requests=requests_q)


@procurement_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_request():
    if current_user.role != "procurement":
        flash("Access denied", "danger")
        return redirect(url_for("procurement.list_requests"))

    vendors = Vendor.query.order_by(Vendor.name.asc()).all()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        amount = request.form.get("amount", "").strip()
        vendor_id = request.form.get("vendor_id") or None
        needed_by = request.form.get("needed_by") or None
        quotation_file = request.files.get("quotation")
        quotation_path = None

        if quotation_file and quotation_file.filename:
         filename = secure_filename(quotation_file.filename)
         upload_dir = os.path.join(current_app.root_path, "static", "uploads", "quotations")
         os.makedirs(upload_dir, exist_ok=True)
         quotation_file.save(os.path.join(upload_dir, filename))
         quotation_path = f"uploads/quotations/{filename}"


        if not title or not amount:
            flash("Title and Amount are required.", "danger")
            return render_template("procurement/create.html", vendors=vendors)

        # quotation upload
        quotation_file = request.files.get("quotation")
        quotation_filename = None
        if quotation_file and quotation_file.filename:
            upload_dir = os.path.join(current_app.root_path, "static", "uploads", "quotations")
            os.makedirs(upload_dir, exist_ok=True)
            safe_name = f"PR_{int(datetime.utcnow().timestamp())}_{quotation_file.filename}".replace(" ", "_")
            quotation_path = os.path.join(upload_dir, safe_name)
            quotation_file.save(quotation_path)
            quotation_filename = safe_name

        pr = ProcurementRequest(
            title=title,
            description=description,
            amount=amount,
            vendor_id=int(vendor_id) if vendor_id else None,
            created_by=current_user.username,
            needed_by=needed_by,
            quotation=quotation_filename,
            status="pending",
        )
        db.session.add(pr)
        db.session.flush()

        _log("PROCUREMENT_CREATE", "ProcurementRequest", pr.id, f"title={title}, amount={amount}")

        db.session.commit()
        flash("Procurement request submitted", "success")
        return redirect(url_for("procurement.view_request", request_id=pr.id))

    return render_template("procurement/create.html", vendors=vendors)


@procurement_bp.route("/quotation/<path:filename>")
@login_required
def view_quotation(filename):
    upload_dir = os.path.join(current_app.root_path, "static", "uploads", "quotations")
    return send_from_directory(upload_dir, filename, as_attachment=False)


@procurement_bp.route("/<int:request_id>")
@login_required
def view_request(request_id):
    pr = ProcurementRequest.query.get_or_404(request_id)

    # Access rules (frozen, simple)
    # procurement can view all; director can view all; finance can view approved only
    if current_user.role == "finance" and pr.status != "approved":
        flash("Finance can only view approved requests.", "warning")
        return redirect(url_for("procurement.list_requests"))

    total_paid = float(pr.payments.with_entities(db.func.coalesce(db.func.sum(db.cast(db.text("amount"), db.Numeric(12,2))), 0)).scalar() or 0) if hasattr(pr, "payments") else 0

    return render_template(
        "procurement/view.html",
        pr=pr,
        finance_limit=FINANCE_LIMIT,
        total_paid=total_paid,
    )


@procurement_bp.route("/approve/<int:request_id>", methods=["POST"])
@login_required
def approve_request(request_id):
    if current_user.role != "director":
        flash("Access denied", "danger")
        return redirect(url_for("procurement.list_requests"))

    pr = ProcurementRequest.query.get_or_404(request_id)

    if pr.status != "pending":
        flash("Request already processed", "warning")
        return redirect(url_for("procurement.view_request", request_id=request_id))

    pr.status = "approved"
    pr.approved_by = current_user.username
    pr.approved_at = datetime.utcnow()

    _log("PROCUREMENT_APPROVE", "ProcurementRequest", pr.id, f"approved_by={current_user.username}")

    db.session.commit()
    flash("Request approved", "success")
    return redirect(url_for("procurement.view_request", request_id=request_id))


@procurement_bp.route("/reject/<int:request_id>", methods=["POST"])
@login_required
def reject_request(request_id):
    if current_user.role != "director":
        flash("Access denied", "danger")
        return redirect(url_for("procurement.list_requests"))

    pr = ProcurementRequest.query.get_or_404(request_id)

    if pr.status != "pending":
        flash("Request already processed", "warning")
        return redirect(url_for("procurement.view_request", request_id=request_id))

    pr.status = "rejected"
    pr.rejected_by = current_user.username
    pr.rejected_at = datetime.utcnow()

    _log("PROCUREMENT_REJECT", "ProcurementRequest", pr.id, f"rejected_by={current_user.username}")

    db.session.commit()
    flash("Request rejected", "warning")
    return redirect(url_for("procurement.view_request", request_id=request_id))
