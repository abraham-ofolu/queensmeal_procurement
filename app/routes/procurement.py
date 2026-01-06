import os
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app import db
from app.models import ProcurementRequest, Vendor, Payment

procurement_bp = Blueprint("procurement", __name__, url_prefix="/procurement")


@procurement_bp.route("/")
@login_required
def list_requests():
    requests_q = ProcurementRequest.query.order_by(
        ProcurementRequest.created_at.desc()
    ).all()
    return render_template("procurement/list.html", requests=requests_q)


@procurement_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_request():
    vendors = Vendor.query.order_by(Vendor.name.asc()).all()

    if request.method == "POST":
        quotation_file = request.files.get("quotation")
        quotation_filename = None

        if quotation_file and quotation_file.filename:
            filename = secure_filename(quotation_file.filename)
            upload_dir = os.path.join(
                current_app.root_path, "static", "uploads", "quotations"
            )
            os.makedirs(upload_dir, exist_ok=True)
            quotation_file.save(os.path.join(upload_dir, filename))
            quotation_filename = filename

        pr = ProcurementRequest(
            title=request.form.get("title"),
            description=request.form.get("description"),
            amount=float(request.form.get("amount")),
            vendor_id=request.form.get("vendor_id"),
            quotation=quotation_filename,
            status="pending",
            created_by=current_user.username,
            created_at=datetime.utcnow()
        )

        db.session.add(pr)
        db.session.commit()

        flash("Procurement request created successfully", "success")
        return redirect(url_for("procurement.list_requests"))

    return render_template("procurement/create.html", vendors=vendors)


@procurement_bp.route("/<int:request_id>")
@login_required
def view_request(request_id):
    pr = ProcurementRequest.query.get_or_404(request_id)

    payments = Payment.query.filter_by(
        procurement_request_id=pr.id
    ).order_by(Payment.paid_at.desc()).all()

    total_paid = sum(p.amount for p in payments)

    return render_template(
        "procurement/view.html",
        pr=pr,
        payments=payments,
        total_paid=total_paid
    )
