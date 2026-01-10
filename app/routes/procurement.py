from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required
from werkzeug.utils import secure_filename
import os

from app.extensions import db
from app.models.procurement import ProcurementRequest
from app.models.procurement_quotation import ProcurementQuotation

procurement_bp = Blueprint(
    "procurement",
    __name__,
    url_prefix="/procurement"
)

# =========================
# LIST REQUESTS
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
# CREATE REQUEST
# =========================
@procurement_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_request():
    if request.method == "POST":
        pr = ProcurementRequest(
            title=request.form["title"],
            description=request.form.get("description"),
            amount=request.form["amount"],
            created_by=request.form.get("created_by")
        )
        db.session.add(pr)
        db.session.commit()
        flash("Procurement request created", "success")
        return redirect(url_for("procurement.index"))

    return render_template("procurement/create.html")

# =========================
# ✅ UPLOAD QUOTATION (THIS FIXES 404)
# =========================
@procurement_bp.route("/<int:procurement_id>/upload-quotation", methods=["POST"])
@login_required
def upload_quotation(procurement_id):
    file = request.files.get("quotation")

    if not file or file.filename == "":
        flash("No file selected", "danger")
        return redirect(url_for("procurement.index"))

    filename = secure_filename(file.filename)

    upload_dir = os.path.join(current_app.root_path, "uploads")
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
