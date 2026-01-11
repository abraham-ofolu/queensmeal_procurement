import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
    abort,
)
from flask_login import login_required, current_user

from app.extensions import db
from app.models.procurement_request import ProcurementRequest

procurement_bp = Blueprint("procurement", __name__, url_prefix="/procurement")


# -----------------------------
# Helpers
# -----------------------------
def _is_procurement_user() -> bool:
    return getattr(current_user, "role", "").lower() == "procurement"


def _ensure_upload_folder() -> str:
    """
    IMPORTANT (Render): If you don't mount a persistent disk, files can disappear after deploy/restart.
    This code uses UPLOAD_FOLDER if set, otherwise falls back to <project>/uploads.
    """
    upload_root = current_app.config.get("UPLOAD_FOLDER")
    if not upload_root:
        upload_root = os.path.join(current_app.root_path, "..", "uploads")

    upload_root = os.path.abspath(upload_root)
    os.makedirs(upload_root, exist_ok=True)

    # Keep quotations in a subfolder
    quotation_dir = os.path.join(upload_root, "quotations")
    os.makedirs(quotation_dir, exist_ok=True)
    return quotation_dir


def _allowed_quotation(filename: str) -> bool:
    allowed = {"pdf", "png", "jpg", "jpeg", "webp"}
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in allowed


def _can_procurement_edit(req_obj: ProcurementRequest) -> bool:
    """
    Rules:
    - pending: procurement can edit/submit/upload quotation
    - pending_director: procurement read-only
    - approved: everyone read-only (except finance/director payments in their pages)
    - rejected: procurement view-only
    """
    status = (req_obj.status or "").lower()
    return status in {"pending"}


# -----------------------------
# Routes
# -----------------------------
@procurement_bp.route("/", methods=["GET"], endpoint="index")
@login_required
def index():
    if not _is_procurement_user() and getattr(current_user, "role", "").lower() not in {"director", "finance"}:
        abort(403)

    requests_list = ProcurementRequest.query.order_by(ProcurementRequest.created_at.desc()).all()
    return render_template("procurement/index.html", requests=requests_list)


@procurement_bp.route("/create", methods=["GET", "POST"], endpoint="create")
@procurement_bp.route("/create-request", methods=["GET", "POST"], endpoint="create_request")
@login_required
def create_request():
    if not _is_procurement_user():
        abort(403)

    if request.method == "POST":
        item = (request.form.get("item") or "").strip()
        quantity_raw = (request.form.get("quantity") or "").strip()
        amount_raw = (request.form.get("amount") or "").strip()

        if not item:
            flash("Item is required.", "danger")
            return redirect(url_for("procurement.create"))

        try:
            quantity = int(quantity_raw) if quantity_raw else 1
            if quantity < 1:
                raise ValueError()
        except Exception:
            flash("Quantity must be a whole number (1 or more).", "danger")
            return redirect(url_for("procurement.create"))

        try:
            amount = float(amount_raw)
            if amount < 0:
                raise ValueError()
        except Exception:
            flash("Amount must be a valid number.", "danger")
            return redirect(url_for("procurement.create"))

        req_obj = ProcurementRequest(
            item=item,
            quantity=quantity,
            amount=amount,
            status="pending",  # procurement can still edit/upload quotation while pending
            created_at=datetime.utcnow(),
            quotation_file=None,
        )

        db.session.add(req_obj)
        db.session.commit()

        flash("Request created. Now upload a quotation to submit to Director.", "success")
        return redirect(url_for("procurement.index"))

    return render_template("procurement/create.html")


@procurement_bp.route("/<int:req_id>/upload-quotation", methods=["POST"], endpoint="upload_quotation")
@login_required
def upload_quotation(req_id: int):
    if not _is_procurement_user():
        abort(403)

    req_obj = ProcurementRequest.query.get_or_404(req_id)

    if not _can_procurement_edit(req_obj):
        flash("This request is no longer editable.", "warning")
        return redirect(url_for("procurement.index"))

    if "quotation" not in request.files:
        flash("No quotation file provided.", "danger")
        return redirect(url_for("procurement.index"))

    file = request.files["quotation"]
    if not file or not file.filename:
        flash("Please choose a file to upload.", "danger")
        return redirect(url_for("procurement.index"))

    filename_original = secure_filename(file.filename)
    if not _allowed_quotation(filename_original):
        flash("Allowed formats: PDF, PNG, JPG, JPEG, WEBP.", "danger")
        return redirect(url_for("procurement.index"))

    quotation_dir = _ensure_upload_folder()

    ext = filename_original.rsplit(".", 1)[-1].lower()
    stored_name = f"{uuid.uuid4()}.{ext}"
    full_path = os.path.join(quotation_dir, stored_name)

    file.save(full_path)

    # Save filename on the request
    req_obj.quotation_file = stored_name

    # Once quotation is uploaded, we submit to Director
    req_obj.status = "pending_director"

    db.session.commit()

    flash("Quotation uploaded successfully and submitted to Director.", "success")
    return redirect(url_for("procurement.index"))


@procurement_bp.route("/quotation/<path:filename>", methods=["GET"], endpoint="view_quotation")
@login_required
def view_quotation(filename: str):
    """
    Serves saved quotation files.
    """
    # allow procurement/director/finance to view
    role = getattr(current_user, "role", "").lower()
    if role not in {"procurement", "director", "finance"}:
        abort(403)

    quotation_dir = _ensure_upload_folder()
    return send_from_directory(quotation_dir, filename, as_attachment=False)
