from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user

from app.extensions import db
from app.models.procurement_request import ProcurementRequest
from app.models.vendor import Vendor


procurement_bp = Blueprint("procurement", __name__, url_prefix="/procurement")


def _is_procurement():
    # supports either 'procurement' or 'PROCUREMENT' etc.
    role = getattr(current_user, "role", "") or ""
    return role.lower() == "procurement"


@procurement_bp.route("/", methods=["GET"])
@login_required
def index():
    # List all requests (everyone can view), newest first
    requests_list = (
        ProcurementRequest.query.order_by(ProcurementRequest.created_at.desc()).all()
        if hasattr(ProcurementRequest, "created_at")
        else ProcurementRequest.query.all()
    )
    return render_template("procurement/index.html", requests=requests_list)


@procurement_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        # (leave your existing POST logic here)
        pass

    vendors = Vendor.query.order_by(Vendor.name.asc()).all()
    return render_template(
        "procurement/create.html",
        vendors=vendors
    )

    # Only procurement can create/submit
    if not _is_procurement():
        flash("Only Procurement can create requests.", "danger")
        return redirect(url_for("procurement.index"))

    if request.method == "POST":
        item = (request.form.get("item") or "").strip()
        quantity_raw = (request.form.get("quantity") or "").strip()
        amount_raw = (request.form.get("amount") or "").strip()
        urgent = True if request.form.get("urgent") == "on" else False

        # Basic validation
        if not item:
            flash("Item/Description is required.", "danger")
            return render_template("procurement/create.html") if _template_exists("procurement/create.html") else redirect(url_for("procurement.index"))

        try:
            quantity = int(quantity_raw) if quantity_raw else 1
        except ValueError:
            flash("Quantity must be a number.", "danger")
            return render_template("procurement/create.html") if _template_exists("procurement/create.html") else redirect(url_for("procurement.index"))

        try:
            amount = float(amount_raw) if amount_raw else 0.0
        except ValueError:
            flash("Amount must be a number.", "danger")
            return render_template("procurement/create.html") if _template_exists("procurement/create.html") else redirect(url_for("procurement.index"))

        # Create request (status should start as "pending" per your rules)
        pr = ProcurementRequest(
            item=item,
            quantity=quantity,
            amount=amount,
            status="pending",
        )

        # created_at if field exists
        if hasattr(pr, "created_at") and getattr(pr, "created_at") is None:
            pr.created_at = datetime.utcnow()

        # urgency: only set if the model has a column for it (prevents crashes)
        if hasattr(pr, "urgent"):
            pr.urgent = urgent
        elif hasattr(pr, "is_urgent"):
            pr.is_urgent = urgent

        db.session.add(pr)
        db.session.commit()

        flash("Procurement request submitted successfully.", "success")
        return redirect(url_for("procurement.index"))

    # GET
    # If you already have procurement/create.html, it will render.
    # If not, we still keep the route alive and return to index.
    if _template_exists("procurement/create.html"):
        return render_template("procurement/create.html")
    flash("Create page template not found yet. (Route is ready.)", "warning")
    return redirect(url_for("procurement.index"))


def _template_exists(template_name: str) -> bool:
    """Safe check so missing templates don't crash the whole app."""
    from flask import current_app

    try:
        current_app.jinja_env.get_template(template_name)
        return True
    except Exception:
        return False
