import os
from datetime import datetime
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app,
    send_from_directory,
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app import db
from app.models.procurement_request import ProcurementRequest
from app.models.vendor import Vendor
from app.models.payment import Payment

procurement_bp = Blueprint("procurement", __name__, url_prefix="/procurement")


# ============================
# LIST PROCUREMENT REQUESTS
# ============================
@procurement_bp.route("/")
@login_required
def list_requests():
    requests_q = ProcurementRequest.query.order_by(
        ProcurementRequest.created_at.desc()
    ).all()
    return render_template("procurement/list.html", requests=requests_q)


# ============================
# CREATE PROCUREMENT REQUEST
# ============================
@procurement_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_request():
    vendors = Vendor.query.order_by(Vendor.name.asc()).all()

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        amount = request.form.get("amount")
        vendor_id = request.form.get("vendor_id")
        needed_by = request.form.get("needed_by")

        pr = ProcurementRequest(
            title=title,
            description=description,
            amount=float(amount),
            vendor_id=vendor_id or None,
            created_by=current_user.username,
            status="pending",
            created_at=datetime.utcnow(),
            needed_by=needed_by or None,
        )

        # ============================
        # QUOTATION UPLOAD (FIXED)
        # ============================
        file = request.files.get("quotation")
        if file and file.filename:
            upload_dir = os.path.join(current_app.root_path, "uploads")
            os.makedirs(upload_dir, exist_ok=True)

            filename = secure_filename(file.filename)
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)

            # SAVE ONLY FILENAME TO DB
            pr.quotation = filename

        db.session.add(pr)
        db.session.commit()

        flash("Procurement request created successfully", "success")
        return redirect(url_for("procurement.list_requests"))

    return render_template("procurement/create.html", vendors=vendors)


# ============================
# VIEW PROCUREMENT REQUEST
# ============================
@procurement_bp.route("/<int:request_id>")
@login_required
def view_request(request_id):
    pr = ProcurementRequest.query.get_or_404(request_id)

    payments = Payment.query.filter_by(procurement_request_id=pr.id).all()
    total_paid = sum(p.amount for p in payments)

    return render_template(
        "procurement/view.html",
        pr=pr,
        payments=payments,
        total_paid=total_paid,
    )


# ============================
# VIEW UPLOADED QUOTATION
# ============================
@procurement_bp.route("/quotation/<path:filename>")
@login_required
def view_quotation(filename):
    upload_dir = os.path.join(current_app.root_path, "uploads")
    return send_from_directory(upload_dir, filename, as_attachment=False)


# ============================
# APPROVE REQUEST
# ============================
@procurement_bp.route("/approve/<int:request_id>", methods=["POST"])
@login_required
def approve_request(request_id):
    pr = ProcurementRequest.query.get_or_404(request_id)

    pr.status = "approved"
    pr.approved_by = current_user.username
    pr.approved_at = datetime.utcnow()

    db.session.commit()
    flash("Procurement request approved", "success")
    return redirect(url_for("procurement.view_request", request_id=request_id))


# ============================
# REJECT REQUEST
# ============================
@procurement_bp.route("/reject/<int:request_id>", methods=["POST"])
@login_required
def reject_request(request_id):
    pr = ProcurementRequest.query.get_or_404(request_id)

    pr.status = "rejected"
    pr.rejected_by = current_user.username
    pr.rejected_at = datetime.utcnow()

    db.session.commit()
    flash("Procurement request rejected", "warning")
    return redirect(url_for("procurement.view_request", request_id=request_id))
