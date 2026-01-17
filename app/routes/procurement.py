from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app.extensions import db
from app.models.procurement_request import ProcurementRequest
from app.models.procurement_quotation import ProcurementQuotation
from app.models.vendor import Vendor
from app.models.payment import Payment

# Optional: Cloudinary upload (won't break app if Cloudinary isn't installed)
try:
    import cloudinary.uploader
    CLOUDINARY_OK = True
except Exception:
    CLOUDINARY_OK = False

procurement_bp = Blueprint("procurement", __name__, url_prefix="/procurement")


def _role() -> str:
    return (getattr(current_user, "role", "") or "").lower()


def _require_role(*roles) -> bool:
    if _role() not in [r.lower() for r in roles]:
        flash("You are not allowed to access that page.", "danger")
        return False
    return True


@procurement_bp.route("/")
@login_required
def index():
    requests_qs = (
        ProcurementRequest.query
        .order_by(ProcurementRequest.created_at.desc())
        .all()
    )

    # For receipt links, we’ll show latest payment receipt if available
    # (No heavy joins — just simple relationship access in template)
    return render_template("procurement/index.html", requests=requests_qs)


@procurement_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    # Only procurement should create requests
    if not _require_role("procurement"):
        return redirect(url_for("procurement.index"))

    vendors = Vendor.query.order_by(Vendor.name.asc()).all()

    if request.method == "GET":
        return render_template("procurement/create.html", vendors=vendors)

    # POST — DO NOT allow hard crash: always handle errors
    try:
        item = (request.form.get("item") or "").strip()
        description = (request.form.get("description") or "").strip() or None

        qty_raw = (request.form.get("quantity") or "").strip()
        amount_raw = (request.form.get("amount") or "").strip()
        vendor_id_raw = (request.form.get("vendor_id") or "").strip()

        is_urgent = True if request.form.get("is_urgent") == "on" else False

        quotation_file = request.files.get("quotation")  # optional

        if not item or not qty_raw or not amount_raw or not vendor_id_raw:
            flash("Item, Quantity, Amount, and Vendor are required.", "danger")
            return render_template("procurement/create.html", vendors=vendors)

        try:
            quantity = int(qty_raw)
            if quantity <= 0:
                raise ValueError()
        except Exception:
            flash("Quantity must be a valid number greater than 0.", "danger")
            return render_template("procurement/create.html", vendors=vendors)

        try:
            # store as Decimal to match Numeric columns
            amount = Decimal(amount_raw)
            if amount <= 0:
                raise InvalidOperation()
        except Exception:
            flash("Amount must be a valid number greater than 0.", "danger")
            return render_template("procurement/create.html", vendors=vendors)

        try:
            vendor_id = int(vendor_id_raw)
        except Exception:
            flash("Please select a valid vendor.", "danger")
            return render_template("procurement/create.html", vendors=vendors)

        vendor = Vendor.query.get(vendor_id)
        if not vendor:
            flash("Selected vendor not found.", "danger")
            return render_template("procurement/create.html", vendors=vendors)

        # Create the request first
        new_request = ProcurementRequest(
            item=item,
            description=description,
            quantity=quantity,
            amount=amount,
            vendor_id=vendor_id,
            is_urgent=is_urgent,
            status="pending",
            created_at=datetime.utcnow(),
        )
        db.session.add(new_request)
        db.session.flush()  # get new_request.id without final commit

        # Optional quotation upload -> save ProcurementQuotation(file_path=secure_url)
        if quotation_file and quotation_file.filename:
            if not CLOUDINARY_OK:
                # Save request anyway, just warn
                flash("Request saved, but quotation upload is not available (Cloudinary not configured).", "warning")
            else:
                try:
                    res = cloudinary.uploader.upload(
                        quotation_file,
                        resource_type="auto",
                        folder="queensmeal/procurement/quotations",
                    )
                    quotation_url = res.get("secure_url")
                    if quotation_url:
                        q = ProcurementQuotation(
                            procurement_request_id=new_request.id,
                            file_path=quotation_url,
                            created_at=datetime.utcnow(),
                        )
                        db.session.add(q)
                    else:
                        flash("Request saved, but quotation upload returned no URL.", "warning")
                except Exception as e:
                    # Save request anyway, just warn
                    flash(f"Request saved, but could not save quotation: {e}", "warning")

        db.session.commit()
        flash("Request submitted successfully.", "success")
        return redirect(url_for("procurement.index"))

    except Exception as e:
        db.session.rollback()
        flash(f"Could not save request: {e}", "danger")
        return render_template("procurement/create.html", vendors=vendors)
