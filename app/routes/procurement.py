import os
from flask import Blueprint, render_template, request, redirect, url_for, abort, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.procurement import ProcurementRequest
from app.models.vendor import Vendor
from app.models.audit_log import AuditLog
from app.mailers import notify
from app.whatsapp import send_whatsapp

UPLOAD_ROOT = "uploads/requests"

procurement_bp = Blueprint("procurement", __name__, url_prefix="/procurement")


def _require_roles(*roles):
    if current_user.role not in roles:
        abort(403)


def _log(action, req_id):
    log = AuditLog(
        entity_type="procurement",
        entity_id=req_id,
        action=action,
        performed_by=current_user.username,
        role=current_user.role,
    )
    db.session.add(log)


@procurement_bp.route("/")
@login_required
def list_requests():
    requests = ProcurementRequest.query.all()
    return render_template("procurement/list.html", requests=requests)


@procurement_bp.route("/new", methods=["GET", "POST"])
@login_required
def new_request():
    _require_roles("branch", "procurement")
    vendors = Vendor.query.filter_by(status="approved").all()

    if request.method == "POST":
        vendor = Vendor.query.get(request.form.get("vendor_id"))
        if not vendor:
            abort(400)

        req = ProcurementRequest(
            item_name=request.form.get("item_name"),
            vendor_id=vendor.id,
            created_by=current_user.username,
            status="draft",
        )

        db.session.add(req)
        db.session.commit()

        _log("created", req.id)
        db.session.commit()

        notify(
            subject="New Procurement Request Created",
            body=f"'{req.item_name}' was created by {current_user.username}.",
            to_roles=["procurement", "finance"],
        )

        return redirect(url_for("procurement.request_detail", req_id=req.id))

    return render_template("procurement/view.html", vendors=vendors)


@procurement_bp.route("/<int:req_id>")
@login_required
def request_detail(req_id):
    req = ProcurementRequest.query.get_or_404(req_id)
    logs = AuditLog.query.filter_by(
        entity_type="procurement", entity_id=req.id
    ).order_by(AuditLog.timestamp.desc()).all()

    return render_template("procurement/detail.html", req=req, logs=logs)


@procurement_bp.route("/<int:req_id>/upload", methods=["POST"])
@login_required
def upload_quotation(req_id):
    _require_roles("branch", "procurement")
    req = ProcurementRequest.query.get_or_404(req_id)

    file = request.files.get("quotation")
    if not file:
        abort(400)

    folder = os.path.join(UPLOAD_ROOT, str(req.id))
    os.makedirs(folder, exist_ok=True)

    filename = secure_filename(file.filename)
    file.save(os.path.join(folder, filename))

    req.quotation_file = filename
    _log("uploaded quotation", req.id)
    db.session.commit()

    return redirect(url_for("procurement.request_detail", req_id=req.id))


@procurement_bp.route("/<int:req_id>/action/<string:action>", methods=["POST"])
@login_required
def request_action(req_id, action):
    req = ProcurementRequest.query.get_or_404(req_id)

    if action == "submit":
        _require_roles("branch", "procurement")
        req.status = "submitted"

        notify(
            subject="Procurement Submitted",
            body=f"Request #{req.id} awaits your approval.",
            to_roles=["director"],
        )

        send_whatsapp(
            f"🛒 PROCUREMENT SUBMITTED\n\n"
            f"Request #{req.id}\n"
            f"Item: {req.item_name}\n"
            f"Awaiting your approval."
        )

    elif action == "approve":
        _require_roles("finance", "director")
        req.status = "approved"

        notify(
            subject="Procurement Approved",
            body=f"Request #{req.id} has been approved.",
            to_roles=["procurement"],
            extra_emails=[f"{req.created_by}@queensmeal.com"],
        )

        send_whatsapp(
            f"✅ PROCUREMENT APPROVED\n\n"
            f"Request #{req.id}\n"
            f"Item: {req.item_name}"
        )

    elif action == "reject":
        _require_roles("director")
        req.status = "rejected"

        notify(
            subject="Procurement Rejected",
            body=f"Request #{req.id} has been rejected.",
            to_roles=["procurement"],
            extra_emails=[f"{req.created_by}@queensmeal.com"],
        )

        send_whatsapp(
            f"❌ PROCUREMENT REJECTED\n\n"
            f"Request #{req.id}\n"
            f"Item: {req.item_name}"
        )

    else:
        abort(400)

    _log(action, req.id)
    db.session.commit()

    return redirect(url_for("procurement.request_detail", req_id=req.id))
