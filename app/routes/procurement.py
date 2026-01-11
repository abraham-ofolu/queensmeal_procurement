import os
import uuid
from flask import Blueprint, current_app, render_template, request, redirect, url_for, flash, send_from_directory
from flask_login import login_required
from werkzeug.utils import secure_filename

from ..extensions import db
from ..models.procurement_request import ProcurementRequest
from ..models.procurement_quotation import ProcurementQuotation

procurement_bp = Blueprint("procurement", __name__)

@procurement_bp.route("/", methods=["GET"])
@login_required
def index():
    requests = ProcurementRequest.query.order_by(ProcurementRequest.created_at.desc()).all()
    return render_template("procurement/index.html", requests=requests)

@procurement_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        item = request.form.get("item", "").strip()
        quantity = int(request.form.get("quantity", "1") or 1)
        amount = request.form.get("amount", "0") or "0"

        if not item:
            flash("Item is required.", "danger")
            return redirect(url_for("procurement.create"))

        pr = ProcurementRequest(item=item, quantity=quantity, amount=amount, status="pending")
        db.session.add(pr)
        db.session.commit()

        flash("Procurement request created.", "success")
        return redirect(url_for("procurement.index"))

    return render_template("procurement/create.html")

@procurement_bp.route("/<int:req_id>/upload-quotation", methods=["POST"])
@login_required
def upload_quotation(req_id):
    pr = ProcurementRequest.query.get_or_404(req_id)

    file = request.files.get("quotation")
    if not file or file.filename.strip() == "":
        flash("Please select a file to upload.", "danger")
        return redirect(url_for("procurement.index"))

    filename = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4()}_{filename}"

    save_path = os.path.join(current_app.config["QUOTATIONS_FOLDER"], unique_name)
    file.save(save_path)

    # Save record
    q = ProcurementQuotation(procurement_request_id=pr.id, filename=unique_name)
    db.session.add(q)

    # Optional: also store “main” file on request for quick link
    pr.quotation_file = unique_name

    db.session.commit()

    flash("Quotation uploaded successfully.", "success")
    return redirect(url_for("procurement.index"))

@procurement_bp.route("/quotation/<path:filename>", methods=["GET"])
@login_required
def view_quotation(filename):
    return send_from_directory(current_app.config["QUOTATIONS_FOLDER"], filename, as_attachment=False)
