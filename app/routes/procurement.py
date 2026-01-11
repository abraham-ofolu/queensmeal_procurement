import os
from flask import (
    Blueprint, render_template, redirect,
    url_for, flash, send_from_directory
)
from flask_login import login_required
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.procurement import ProcurementRequest
from app.config import Config

procurement_bp = Blueprint(
    "procurement",
    __name__,
    url_prefix="/procurement"
)


@procurement_bp.route("/")
@login_required
def index():
    requests = ProcurementRequest.query.order_by(
        ProcurementRequest.created_at.desc()
    ).all()

    return render_template(
        "procurement/index.html",
        requests=requests
    )


@procurement_bp.route("/<int:request_id>/upload-quotation", methods=["POST"])
@login_required
def upload_quotation(request_id):
    req = ProcurementRequest.query.get_or_404(request_id)

    if "quotation" not in request.files:
        flash("No file selected.", "danger")
        return redirect(url_for("procurement.index"))

    file = request.files["quotation"]

    if file.filename == "":
        flash("No file selected.", "danger")
        return redirect(url_for("procurement.index"))

    filename = secure_filename(file.filename)

    upload_dir = os.path.join(
        Config.UPLOAD_FOLDER,
        "quotations"
    )
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, filename)
    file.save(file_path)

    req.quotation_file = filename
    db.session.commit()

    flash("Quotation uploaded successfully.", "success")
    return redirect(url_for("procurement.index"))


@procurement_bp.route("/quotation/<filename>")
@login_required
def view_quotation(filename):
    return send_from_directory(
        os.path.join(Config.UPLOAD_FOLDER, "quotations"),
        filename
    )
