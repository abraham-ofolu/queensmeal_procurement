import os
from datetime import datetime
from uuid import uuid4

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.procurement_request import ProcurementRequest
from app.models.procurement_quotation import ProcurementQuotation
from app.models.vendor import Vendor

# Optional Cloudinary support (won't break if not installed/configured)
try:
    import cloudinary.uploader  # type: ignore

    CLOUDINARY_OK = True
except Exception:
    CLOUDINARY_OK = False


procurement_bp = Blueprint("procurement", __name__, url_prefix="/procurement")


def _role() -> str:
    return (getattr(current_user, "role", "") or "").lower()


def _require_role(*roles) -> bool:
    return _role() in [r.lower() for r in roles]


def _allowed_file(filename: str) -> bool:
    # Accept common quotation formats
    allowed = {"pdf", "png", "jpg", "jpeg", "webp"}
    ext = (filename.rsplit(".", 1)[-1] or "").lower()
    return ext in allowed


@procurement_bp.route("/")
@login_required
def index():
    requests_qs = ProcurementRequest.query.order_by(ProcurementRequest.created_at.desc()).all()
    return render_template("procurement/index.html", requests=requests_qs)


@procurement_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    # Only Procurement can create requests
    if not _require_role("procurement"):
        flash("Only Procurement can create requests.", "danger")
        return redirect(url_for("procurement.index"))

    vendors = Vendor.query.order_by(Vendor.name.asc()).all()

    if request.method == "GET":
        return render_template("procurement/create.html", vendors=vendors)

    # POST
    item = (request.form.get("item") or "").strip()
    quantity_raw = (request.form.get("quantity") or "").strip()
    amount_raw = (request.form.get("amount") or "").strip()
    vendor_id_raw = (request.form.get("vendor_id") or "").strip()
    is_urgent = True if request.form.get("is_urgent") == "on" else False

    quotation_file = request.files.get("quotation")

    if not item or not quantity_raw or not amount_raw or not vendor_id_raw:
        flash("Item, Quantity, Amount, and Vendor are required.", "danger")
        return redirect(url_for("procurement.create"))

    try:
        quantity = int(quantity_raw)
    except Exception:
        flash("Quantity must be a number.", "danger")
        return redirect(url_for("procurement.create"))

    try:
        amount = float(amount_raw)
    except Exception:
        flash("Amount must be a number.", "danger")
        return redirect(url_for("procurement.create"))

    try:
        vendor_id = int(vendor_id_raw)
    except Exception:
        flash("Vendor is required.", "danger")
        return redirect(url_for("procurement.create"))

    # Ensure vendor exists
    vendor = Vendor.query.get(vendor_id)
    if not vendor:
        flash("Selected vendor does not exist. Please add the vendor first.", "danger")
        return redirect(url_for("procurement.create"))

    # 1) Create request first
    new_request = ProcurementRequest(
        item=item,
        quantity=quantity,
        amount=amount,
        vendor_id=vendor_id,
        is_urgent=is_urgent,
        status="pending",
        created_at=datetime.utcnow(),
    )

    try:
        db.session.add(new_request)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f"Could not save request: {e}", "danger")
        return redirect(url_for("procurement.create"))

    # 2) If quotation file provided: save it as ProcurementQuotation
    if quotation_file and quotation_file.filename:
        if not _allowed_file(quotation_file.filename):
            flash("Quotation must be PDF or an image (png/jpg).", "danger")
            return redirect(url_for("procurement.create"))

        file_url = None

        # Prefer Cloudinary if available
        if CLOUDINARY_OK and (os.getenv("CLOUDINARY_URL") or os.getenv("CLOUDINARY_CLOUD_NAME")):
            try:
                res = cloudinary.uploader.upload(
                    quotation_file,
                    resource_type="auto",
                    folder="queensmeal/procurement/quotations",
                )
                file_url = res.get("secure_url")
            except Exception as e:
                flash(f"Quotation upload failed (Cloudinary): {e}", "danger")
                # request is already created, but quotation failed; keep request and continue
        else:
            # Local fallback: saves into app/static/uploads/quotations
            try:
                base_dir = current_app.root_path  # .../app
                uploads_dir = os.path.join(base_dir, "static", "uploads", "quotations")
                os.makedirs(uploads_dir, exist_ok=True)

                safe_name = secure_filename(quotation_file.filename)
                unique_name = f"{uuid4().hex}_{safe_name}"
                abs_path = os.path.join(uploads_dir, unique_name)
                quotation_file.save(abs_path)

                # Public URL path
                file_url = url_for("static", filename=f"uploads/quotations/{unique_name}")
            except Exception as e:
                flash(f"Quotation upload failed (local): {e}", "danger")

        if file_url:
            try:
                q = ProcurementQuotation(
                    procurement_request_id=new_request.id,
                    file_path=file_url,
                )
                db.session.add(q)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                flash(f"Saved request, but could not save quotation: {e}", "danger")

    flash("Request submitted successfully.", "success")
    return redirect(url_for("procurement.index"))
