import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.procurement import ProcurementRequest, ProcurementQuotation
from app.models.vendor import Vendor


procurement_bp = Blueprint(
    "procurement",
    __name__,
    url_prefix="/procurement"
)

UPLOAD_FOLDER = "uploads/quotations"
ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


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
# UPLOAD QUOTATION (OPTIONAL)
# =========================
@procurement_bp.route("/<int:procurement_id>/upload-quotation", methods=["GET", "POST"])
@login_required
def upload_quotation(procurement_id):
    procurement = ProcurementRequest.query.get_or_404(procurement_id)

    if request.method == "POST":
        file = request.files.get("quotation")

        if not file or file.filename == "":
            flash("No file selected", "danger")
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash("Invalid file type", "danger")
            return redirect(request.url)

        filename = secure_filename(file.filename)

        upload_path = os.path.join(current_app.root_path, UPLOAD_FOLDER)
        os.makedirs(upload_path, exist_ok=True)

        file.save(os.path.join(upload_path, filename))

        quotation = ProcurementQuotation(
            procurement_id=procurement.id,
            filename=filename
        )

        db.session.add(quotation)
        db.session.commit()

        flash("Quotation uploaded successfully", "success")
        return redirect(url_for("procurement.index"))

    return render_template(
        "procurement/upload_quotation.html",
        procurement=procurement
    )
