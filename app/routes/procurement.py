from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import ProcurementRequest, Vendor
import cloudinary
import cloudinary.uploader

from app.extensions import db
from app.models import ProcurementRequest, Vendor

procurement_bp = Blueprint("procurement", __name__, url_prefix="/procurement")


def _upload_to_cloudinary(file_storage, folder: str) -> str | None:
    if not file_storage or file_storage.filename == "":
        return None
    res = cloudinary.uploader.upload(
        file_storage,
        folder=folder,
        resource_type="auto",
        unique_filename=True,
        overwrite=False,
    )
    return res.get("secure_url")


@procurement_bp.route("/", methods=["GET"])
@login_required
def list_requests():
    reqs = ProcurementRequest.query.order_by(ProcurementRequest.created_at.desc()).all()
    return render_template("procurement/list.html", requests=reqs)


@procurement_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_request():
    vendors = Vendor.query.order_by(Vendor.name.asc()).all()

    if request.method == "POST":
        item = request.form.get("item", "").strip()
        quantity = request.form.get("quantity", "").strip()
        estimated_cost = request.form.get("estimated_cost", "").strip()
        vendor_id = request.form.get("vendor_id", "").strip()

        quotation_file = request.files.get("quotation")
        quotation_url = _upload_to_cloudinary(quotation_file, folder="queensmeal/quotations")

        pr = ProcurementRequest(
            item=item,
            quantity=quantity,
            estimated_cost=float(estimated_cost) if estimated_cost else 0.0,
            vendor_id=int(vendor_id) if vendor_id else None,
            quotation_url=quotation_url,
            status="pending",
            created_by=current_user.id,
            created_at=datetime.utcnow(),
        )

        db.session.add(pr)
        db.session.commit()

        flash("Procurement request created.", "success")
        return redirect(url_for("procurement.list_requests"))

    return render_template("procurement/create.html", vendors=vendors)


@procurement_bp.route("/<int:request_id>", methods=["GET"])
@login_required
def view_request(request_id: int):
    pr = ProcurementRequest.query.get_or_404(request_id)
    return render_template("procurement/view.html", pr=pr)
