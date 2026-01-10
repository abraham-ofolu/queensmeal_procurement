import os
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, current_app
)
from flask_login import login_required
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.procurement import ProcurementRequest
from app.models.procurement_quotation import ProcurementQuotation

procurement_bp = Blueprint(
    "procurement", __name__, url_prefix="/procurement"
)

# =========================
# LIST PROCUREMENT REQUESTS
# =========================
@procurement_bp.route("/")
@login_required
def index():
    requests = (
        ProcurementRequest.query
        .order_by(ProcurementRequest.created_at.desc())
        .all()
    )
    return render_template(
        "procurement/index.html",
        requests=requests
    )

# =========================
# CREATE PROCUREMENT
# =========================
@procurement_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        title = request.form.get("title")
        amount = request.form.get("amount")

        req = ProcurementRequest(
            title=title,
            amount=amount,
            status="pending"
        )

        db.session.add(req)
        db.session.commit()

        flash("Procurement request created", "success")
        return redirect(url_for("procurement.index"))

    return render_template("procurement/create.html")

# =========================
# UPLOAD QUOTATION (FIXED)
# =========================
@procurement_bp.route(
    "/<int:procurement_id>/upload-quotation",
    methods=["POST"]
)
@login_required
def upload_quotation(procurement_id):
    procurement = ProcurementRequest.query.get_or_404(procurement_id)

    # 🔴 THIS NAME MUST MATCH THE HTML INPUT
    file = request.files.get("quotation")

    if not file or file.filename == "":
        flash("No file selected", "danger")
        return redirect(url_for("procurement.index"))

    filename = secure_filename(file.filename)

    upload_folder = os.path.join(
        current_app.instance_path,
        "quotations"
    )
    os.makedirs(upload_folder, exist_ok=True)

    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)

    # ✅ THIS WAS THE MISSING PART
    quotation = ProcurementQuotation(
        procurement_id=procurement.id,
        filename=filename
    )

    db.session.add(quotation)
    db.session.commit()

    flash("Quotation uploaded successfully", "success")
    return redirect(url_for("procurement.index"))
