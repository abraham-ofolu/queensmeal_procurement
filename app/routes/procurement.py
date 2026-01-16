from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app.extensions import db
from app.models.procurement_request import ProcurementRequest
from app.models.vendor import Vendor

procurement_bp = Blueprint("procurement", __name__, url_prefix="/procurement")


def _role() -> str:
    return (getattr(current_user, "role", "") or "").strip().lower()


def _require_role(*roles: str) -> bool:
    allowed = [r.lower() for r in roles]
    if _role() not in allowed:
        flash("You are not allowed to access that page.", "danger")
        return False
    return True


@procurement_bp.route("/")
@login_required
def index():
    # Everyone logged-in can view list (actions restricted elsewhere)
    requests_qs = ProcurementRequest.query.order_by(ProcurementRequest.created_at.desc()).all()
    return render_template("procurement/index.html", requests=requests_qs)


@procurement_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    # Only procurement can create
    if not _require_role("procurement"):
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

    if not item or not quantity_raw or not amount_raw or not vendor_id_raw:
        flash("Item, Quantity, Amount, and Vendor are required.", "danger")
        return redirect(url_for("procurement.create"))

    try:
        quantity = int(quantity_raw)
        amount = float(amount_raw)
        vendor_id = int(vendor_id_raw)
    except Exception:
        flash("Quantity must be a number, Amount must be a number, Vendor must be selected.", "danger")
        return redirect(url_for("procurement.create"))

    # IMPORTANT: use only fields that exist in your ProcurementRequest model
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
        flash("Request submitted successfully.", "success")
        return redirect(url_for("procurement.index"))
    except Exception as e:
        db.session.rollback()
        flash(f"Could not save request: {e}", "danger")
        return redirect(url_for("procurement.create"))
