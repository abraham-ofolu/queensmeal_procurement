from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app.extensions import db
from app.models.procurement_request import ProcurementRequest
from app.models.procurement_quotation import ProcurementQuotation
from app.models.vendor import Vendor

# Optional Cloudinary upload
try:
    import cloudinary.uploader
    CLOUDINARY_OK = True
except Exception:
    CLOUDINARY_OK = False

procurement_bp = Blueprint("procurement", __name__, url_prefix="/procurement")


def _role():
    return (getattr(current_user, "role", "") or "").lower()


def _require_role(*roles):
    if _role() not in [r.lower() for r in roles]:
        flash("You are not allowed to access that page.", "danger")
        return False
    return True


@procurement_bp.route("/")
@login_required
def index():
    requests_qs = ProcurementRequest.query.order_by(
        ProcurementRequest.created_at.desc()
    ).all()
    return render_template("procurement/index.html", requests=requests_qs)


@procurement_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    # 🔒 ONLY PROCUREMENT CAN CREATE
    if not _require_role("procurement"):
        return redirect(url_for("procurement.index"))

    if request.method == "POST":
        item = (request.form.get("item") or "").strip()
        quantity = request.form.get("quantity")
        amount = request.form.get("amount")
        vendor_id = request.form.get("vendor_id")
        is_urgent = request.form.get("is_urgent") == "on"

        if not item or not quantity or not amount or not vendor_id:
            flash("All fields except quotation are required.", "danger")
            return redirect(url_for("procurement.create"))

        new_request = ProcurementRequest(
            item=item,
            quantity=int(quantity),
            amount=float(amount),
            vendor_id=int(vendor_id),
            is_urgent=is_urgent,
            status="pending",
            created_at=datetime.utcnow()
        )

        db.session.add(new_request)
        db.session.flush()  # 👈 ensures ID exists

        # 📎 HANDLE QUOTATION
        quotation_file = request.files.get("quotation")

        if quotation_file and quotation_file.filename:
            if not CLOUDINARY_OK:
                flash("Quotation upload unavailable.", "warning")
            else:
                try:
                    upload = cloudinary.uploader.upload(
                        quotation_file,
                        resource_type="auto",
                        folder="queensmeal/procurement/quotations"
                    )

                    quotation = ProcurementQuotation(
                        procurement_request_id=new_request.id,
                        file_path=upload["secure_url"]
                    )
                    db.session.add(quotation)

                except Exception as e:
                    db.session.rollback()
                    flash(f"Quotation upload failed: {e}", "danger")
                    return redirect(url_for("procurement.create"))

        db.session.commit()
        flash("Request submitted successfully.", "success")
        return redirect(url_for("procurement.index"))

    vendors = Vendor.query.order_by(Vendor.name.asc()).all()
    return render_template("procurement/create.html", vendors=vendors)
