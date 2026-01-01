import os
from datetime import datetime
from decimal import Decimal

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.procurement_request import ProcurementRequest
from app.models.vendor import Vendor

procurement_bp = Blueprint("procurement", __name__, url_prefix="/procurement")

ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png", "doc", "docx", "xls", "xlsx"}

def _allowed_file(filename: str) -> bool:
    if not filename or "." not in filename:
        return False
    return filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def _upload_folder() -> str:
    # uploads/quotations relative to project root
    base = current_app.root_path  # .../app
    project_root = os.path.abspath(os.path.join(base, ".."))
    folder = os.path.join(project_root, "uploads", "quotations")
    os.makedirs(folder, exist_ok=True)
    return folder

@procurement_bp.route("/", methods=["GET"])
@login_required
def list_requests():
    if current_user.role not in ["director", "procurement", "finance"]:
        flash("You do not have access to procurement.", "danger")
        return redirect(url_for("dashboard.home"))

    requests_q = ProcurementRequest.query.order_by(ProcurementRequest.created_at.desc()).all()
    vendors = Vendor.query.order_by(Vendor.name.asc()).all()
    return render_template("procurement/list.html", requests=requests_q, vendors=vendors)

@procurement_bp.route("/new", methods=["GET", "POST"])
@login_required
def create_request():
    if current_user.role not in ["director", "procurement"]:
        flash("Only Procurement or Director can create requests.", "danger")
        return redirect(url_for("procurement.list_requests"))

    vendors = Vendor.query.order_by(Vendor.name.asc()).all()

    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        description = (request.form.get("description") or "").strip()
        amount_raw = (request.form.get("amount") or "0").strip()
        needed_by_raw = (request.form.get("needed_by") or "").strip()
        vendor_id_raw = (request.form.get("vendor_id") or "").strip()

        if not title:
            flash("Title is required.", "danger")
            return render_template("procurement/form.html", mode="create", vendors=vendors)

        try:
            amount = Decimal(amount_raw)
        except Exception:
            flash("Amount must be a number.", "danger")
            return render_template("procurement/form.html", mode="create", vendors=vendors)

        needed_by = None
        if needed_by_raw:
            try:
                needed_by = datetime.strptime(needed_by_raw, "%Y-%m-%d").date()
            except Exception:
                flash("Needed-by date must be YYYY-MM-DD.", "danger")
                return render_template("procurement/form.html", mode="create", vendors=vendors)

        vendor_id = None
        if vendor_id_raw:
            try:
                vendor_id = int(vendor_id_raw)
            except Exception:
                vendor_id = None

        pr = ProcurementRequest(
            title=title,
            description=description or None,
            amount=amount,
            status="pending",
            created_by=current_user.id,
            needed_by=needed_by,
            vendor_id=vendor_id,
        )

        file = request.files.get("quotation")
        if file and file.filename:
            if not _allowed_file(file.filename):
                flash("Invalid quotation file type. Allowed: pdf/jpg/png/doc/docx/xls/xlsx", "danger")
                return render_template("procurement/form.html", mode="create", vendors=vendors)

            safe_name = secure_filename(file.filename)
            stamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            final_name = f"PR_{stamp}_{safe_name}"
            folder = _upload_folder()
            file.save(os.path.join(folder, final_name))
            pr.quotation_filename = final_name

        db.session.add(pr)
        db.session.commit()

        flash("Procurement request created successfully.", "success")
        return redirect(url_for("procurement.list_requests"))

    return render_template("procurement/form.html", mode="create", vendors=vendors)

@procurement_bp.route("/<int:request_id>/edit", methods=["GET", "POST"])
@login_required
def edit_request(request_id: int):
    if current_user.role not in ["director", "procurement"]:
        flash("Only Procurement or Director can edit requests.", "danger")
        return redirect(url_for("procurement.list_requests"))

    pr = ProcurementRequest.query.get_or_404(request_id)
    vendors = Vendor.query.order_by(Vendor.name.asc()).all()

    if request.method == "POST":
        pr.title = (request.form.get("title") or "").strip() or pr.title
        pr.description = (request.form.get("description") or "").strip() or None

        amount_raw = (request.form.get("amount") or "").strip()
        if amount_raw:
            try:
                pr.amount = Decimal(amount_raw)
            except Exception:
                flash("Amount must be a number.", "danger")
                return render_template("procurement/form.html", mode="edit", pr=pr, vendors=vendors)

        needed_by_raw = (request.form.get("needed_by") or "").strip()
        if needed_by_raw:
            try:
                pr.needed_by = datetime.strptime(needed_by_raw, "%Y-%m-%d").date()
            except Exception:
                flash("Needed-by date must be YYYY-MM-DD.", "danger")
                return render_template("procurement/form.html", mode="edit", pr=pr, vendors=vendors)
        else:
            pr.needed_by = None

        vendor_id_raw = (request.form.get("vendor_id") or "").strip()
        pr.vendor_id = int(vendor_id_raw) if vendor_id_raw.isdigit() else None

        # Replace quotation if new file uploaded
        file = request.files.get("quotation")
        if file and file.filename:
            if not _allowed_file(file.filename):
                flash("Invalid quotation file type. Allowed: pdf/jpg/png/doc/docx/xls/xlsx", "danger")
                return render_template("procurement/form.html", mode="edit", pr=pr, vendors=vendors)

            safe_name = secure_filename(file.filename)
            stamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            final_name = f"PR_{stamp}_{safe_name}"
            folder = _upload_folder()
            file.save(os.path.join(folder, final_name))
            pr.quotation_filename = final_name

        db.session.commit()
        flash("Procurement request updated.", "success")
        return redirect(url_for("procurement.list_requests"))

    return render_template("procurement/form.html", mode="edit", pr=pr, vendors=vendors)

@procurement_bp.route("/<int:request_id>/approve", methods=["POST"])
@login_required
def approve_request(request_id: int):
    if current_user.role != "director":
        flash("Only Director can approve requests.", "danger")
        return redirect(url_for("procurement.list_requests"))

    pr = ProcurementRequest.query.get_or_404(request_id)
    pr.status = "approved"
    pr.approved_by = current_user.id
    pr.approved_at = datetime.utcnow()
    db.session.commit()

    flash("Request approved.", "success")
    return redirect(url_for("procurement.list_requests"))

@procurement_bp.route("/quotation/<filename>", methods=["GET"])
@login_required
def download_quotation(filename: str):
    # Only allowed roles
    if current_user.role not in ["director", "procurement", "finance"]:
        flash("Access denied.", "danger")
        return redirect(url_for("dashboard.home"))

    folder = _upload_folder()
    return send_from_directory(folder, filename, as_attachment=True)
