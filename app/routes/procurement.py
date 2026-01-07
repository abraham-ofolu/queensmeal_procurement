import os
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, current_app, send_from_directory
from flask_login import login_required, current_user

from app.extensions import db
from app.models import ProcurementRequest, AuditLog

procurement_bp = Blueprint("procurement", __name__, url_prefix="/procurement")


@procurement_bp.route("/")
@login_required
def list_requests():
    requests = ProcurementRequest.query.order_by(ProcurementRequest.created_at.desc()).all()
    return render_template("procurement/list.html", requests=requests)


@procurement_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_request():
    if request.method == "POST":
        pr = ProcurementRequest(
            title=request.form.get("title"),
            description=request.form.get("description"),
            amount=request.form.get("amount"),
            status="pending",
            created_at=datetime.utcnow()
        )
        db.session.add(pr)

        db.session.add(
            AuditLog(
                user_id=current_user.id,
                action="Created procurement request",
                entity="ProcurementRequest",
                entity_id=pr.id
            )
        )

        db.session.commit()
        return redirect(url_for("procurement.list_requests"))

    return render_template("procurement/create.html")


@procurement_bp.route("/<int:request_id>")
@login_required
def view_request(request_id):
    pr = ProcurementRequest.query.get_or_404(request_id)
    return render_template("procurement/view.html", pr=pr)


# ✅ THIS ROUTE WAS MISSING
@procurement_bp.route("/quotation/<path:filename>")
@login_required
def view_quotation(filename):
    upload_dir = os.path.join(
        current_app.root_path,
        "static",
        "uploads",
        "quotations"
    )
    return send_from_directory(upload_dir, filename, as_attachment=False)
