from datetime import datetime

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user

from app.extensions import db
from app.models.procurement_request import ProcurementRequest
from app.utils.cloudinary_service import upload_file

procurement_bp = Blueprint("procurement", __name__, url_prefix="/procurement")


def _role() -> str:
    return (getattr(current_user, "role", "") or "").lower()


def _is_procurement() -> bool:
    return _role() == "procurement"


def _can_procurement_edit(req_obj: ProcurementRequest) -> bool:
    return (req_obj.status or "").lower() == "pending"


@procurement_bp.route("/", methods=["GET"], endpoint="index")
@login_required
def index():
    if _role() not in {"procurement", "director", "finance"}:
        abort(403)

    requests_list = ProcurementRequest.query.order_by(ProcurementRequest.created_at.desc()).all()
    return render_template("procurement/index.html", requests=requests_list)


@procurement_bp.route("/create", methods=["GET", "POST"], endpoint="create")
@procurement_bp.route("/create-request", methods=["GET", "POST"], endpoint="create_request")
@login_required
def create_request():
    if not _is_procurement():
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
            status="pending",
            created_at=datetime.utcnow(),
        )
        db.session.add(req_obj)
        db.session.commit()

        flash("Request created. Upload a quotation to submit to Director.", "success")
        return redirect(url_for("procurement.index"))

    return render_template("procurement/create.html")


@procurement_bp.route("/<int:req_id>/upload-quotation", methods=["POST"], endpoint="upload_quotation")
@login_required
def upload_quotation(req_id: int):
    if not _is_procurement():
        abort(403)

    req_obj = ProcurementRequest.query.get_or_404(req_id)

    if not _can_procurement_edit(req_obj):
        flash("This request is no longer editable.", "warning")
        return redirect(url_for("procurement.index"))

    file = request.files.get("quotation")
    if not file or not file.filename:
        flash("Please choose a quotation file to upload.", "danger")
        return redirect(url_for("procurement.index"))

    url, public_id = upload_file(file, folder="queensmeal/quotations")

    req_obj.quotation_url = url
    req_obj.quotation_public_id = public_id

    # submit to director
    req_obj.status = "pending_director"

    db.session.commit()

    flash("Quotation uploaded and submitted to Director.", "success")
    return redirect(url_for("procurement.index"))
