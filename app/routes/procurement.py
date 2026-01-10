from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from datetime import datetime
import os
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.procurement import ProcurementRequest
from app.models.vendor import Vendor
from app.models.procurement_quotation import ProcurementQuotation

procurement_bp = Blueprint(
    "procurement",
    __name__,
    url_prefix="/procurement"
)

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
def create_request():
    vendors = Vendor.query.all()

    if request.method == "POST":
        title = request.form["title"]
        description = request.form.get("description")
        amount = request.form["amount"]
        vendor_id = request.form.get("vendor_id")

        pr = ProcurementRequest(
            title=title,
            description=description,
            amount=amount,
            vendor_id=vendor_id if vendor_id else None,
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
# UPLOAD QUOTATION (SAFE)
# =========================
@procurement_bp.route("/<int:procurement_id>/upload-quotation", methods=["POST"])
@login_required
def upload_quotation(procurement_id):
    file = request.files.get("quotation")

    if not file or file.filename == "":
        flash("No file selected", "danger")
        return redirect(url_for("procurement.index"))

    filename = secure_filename(file.filename)

    upload_dir = os.path.join(
        current_app.root_path,
        "static",
        "quotations"
    )

    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, filename)
    file.save(file_path)

    quotation = ProcurementQuotation(
        procurement_id=procurement_id,
        filename=filename
    )

    db.session.add(quotation)
    db.session.commit()

    flash("Quotation uploaded successfully", "success")
    return redirect(url_for("procurement.index"))
