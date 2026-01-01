import os
from datetime import datetime
from decimal import Decimal

from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.procurement_request import ProcurementRequest
from app.models.vendor import Vendor
from config import Config

procurement_bp = Blueprint("procurement", __name__, url_prefix="/procurement")


def _to_decimal(value: str) -> Decimal:
    try:
        return Decimal(value)
    except Exception:
        return Decimal("0.00")


@procurement_bp.route("/")
@login_required
def list_requests():
    prs = ProcurementRequest.query.order_by(ProcurementRequest.created_at.desc()).all()
    return render_template("procurement/list.html", requests=prs)


@procurement_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_request():
    if current_user.role != "procurement":
        flash("Access denied: Procurement role required.", "danger")
        return redirect(url_for("procurement.list_requests"))

    vendors = Vendor.query.order_by(Vendor.name.asc()).all()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip() or None
        amount = _to_decimal(request.form.get("amount", "0"))
        vendor_id = request.form.get("vendor_id")

        if not title or amount <= 0:
            flash("Title and valid amount are required.", "danger")
            return render_template("procurement/create.html", vendors=vendors)

        pr = ProcurementRequest(
            title=title,
            description=description,
            amount=amount,
            created_by=current_user.username,
            vendor_id=int(vendor_id) if vendor_id else None,
        )

        # Quotation upload (optional)
        file = request.files.get("quotation")
        if file and file.filename:
            filename = secure_filename(file.filename)
            # Make filename unique
            stamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            filename = f"{stamp}_{filename}"
            save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
            file.save(save_path)
            pr.quotation_filename = filename

        db.session.add(pr)
        db.session.commit()

        flash("Procurement request submitted successfully.", "success")
        return redirect(url_for("procurement.list_requests"))

    return render_template("procurement/create.html", vendors=vendors)


@procurement_bp.route("/<int:request_id>")
@login_required
def view_request(request_id):
    pr = ProcurementRequest.query.get_or_404(request_id)

    # PASS 1: everyone can view; editing/payment rules handled elsewhere
    finance_limit = float(current_app.config.get("FINANCE_PAYMENT_LIMIT", Config.FINANCE_PAYMENT_LIMIT))

    return render_template(
        "procurement/view.html",
        pr=pr,
        finance_limit=finance_limit,
    )


@procurement_bp.route("/approve/<int:request_id>", methods=["POST"])
@login_required
def approve_request(request_id):
    if current_user.role != "director":
        flash("Access denied: Director role required.", "danger")
        return redirect(url_for("procurement.list_requests"))

    pr = ProcurementRequest.query.get_or_404(request_id)
    if pr.status != "pending":
        flash("This request has already been processed.", "warning")
        return redirect(url_for("procurement.view_request", request_id=pr.id))

    pr.status = "approved"
    pr.approved_by = current_user.username
    pr.approved_at = datetime.utcnow()

    db.session.commit()
    flash("Request approved.", "success")
    return redirect(url_for("procurement.view_request", request_id=pr.id))


@procurement_bp.route("/reject/<int:request_id>", methods=["POST"])
@login_required
def reject_request(request_id):
    if current_user.role != "director":
        flash("Access denied: Director role required.", "danger")
        return redirect(url_for("procurement.list_requests"))

    pr = ProcurementRequest.query.get_or_404(request_id)
    if pr.status != "pending":
        flash("This request has already been processed.", "warning")
        return redirect(url_for("procurement.view_request", request_id=pr.id))

    pr.status = "rejected"
    db.session.commit()

    flash("Request rejected.", "warning")
    return redirect(url_for("procurement.view_request", request_id=pr.id))


@procurement_bp.route("/quotation/<filename>")
@login_required
def download_quotation(filename):
    # PASS 1: allow any logged-in user to view quotation
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename, as_attachment=False)
