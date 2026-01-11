from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from datetime import datetime

from app.extensions import db
from app.models.procurement import ProcurementRequest
from app.models.procurement_quotation import ProcurementQuotation
from app.models.vendor import Vendor

procurement_bp = Blueprint(
    "procurement",
    __name__,
    url_prefix="/procurement"
)

UPLOAD_FOLDER = "app/static/uploads/quotations"

# =========================
# LIST PROCUREMENT REQUESTS
# =========================
@procurement_bp.route("/", methods=["GET"])
@login_required
def index():
    requests = ProcurementRequest.query.order_by(
        ProcurementRequest.created_at.desc()
    ).all()

    return render_template(
        "procurement/index.html",
        requests=requests
    )

# =========================
# CREATE PROCUREMENT REQUEST
# =========================
@procurement_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    vendors = Vendor.query.all()

    if request.method == "POST":
        pr = ProcurementRequest(
            title=request.form["title"],
            description=request.form.get("description"),
            amount=request.form["amount"],
            vendor_id=request.form.get("vendor_id") or None,
            created_by=current_user.id
        )

        db.session.add(pr)
        db.session.commit()

        flash("Procurement request created successfully", "success")
        return redirect(url_for("procurement.index"))

    return render_template(
        "procurement/create.html",
        vendors=vendors
    )

# =========================
# UPLOAD QUOTATION
# =========================
@procurement_bp.route("/<int:procurement_id>/upload-quotation", methods=["POST"])
@login_required
def upload_quotation(procurement_id):
    file = request.files.get("quotation_file")

    if not file or file.filename == "":
        flash("No file selected", "danger")
        return redirect(url_for("procurement.index"))

    filename = secure_filename(file.filename)

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    file.save(os.path.join(UPLOAD_FOLDER, filename))

    quotation = ProcurementQuotation(
        procurement_id=procurement_id,
        filename=filename,
        uploaded_at=datetime.utcnow()
    )

    db.session.add(quotation)
    db.session.commit()

    flash("Quotation uploaded successfully", "success")
    return redirect(url_for("procurement.index"))

# =========================
# VIEW / DOWNLOAD QUOTATION
# =========================
@procurement_bp.route("/quotation/<filename>")
@login_required
def view_quotation(filename):
    return send_from_directory(
        UPLOAD_FOLDER,
        filename,
        as_attachment=False
    )
