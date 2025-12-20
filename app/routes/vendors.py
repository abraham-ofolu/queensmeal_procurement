from flask import Blueprint, render_template, request, redirect, url_for, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models.vendor import Vendor
from app.models.audit_log import AuditLog
from app.mailers import notify

vendors_bp = Blueprint("vendors", __name__, url_prefix="/vendors")


def _require_roles(*roles):
    if current_user.role not in roles:
        abort(403)


def _log(action, vendor_id):
    log = AuditLog(
        entity_type="vendor",
        entity_id=vendor_id,
        action=action,
        performed_by=current_user.username,
        role=current_user.role,
    )
    db.session.add(log)


@vendors_bp.route("/")
@login_required
def list_vendors():
    vendors = Vendor.query.all()
    return render_template("vendors/list.html", vendors=vendors)


@vendors_bp.route("/new", methods=["GET", "POST"])
@login_required
def new_vendor():
    _require_roles("procurement", "director")

    if request.method == "POST":
        vendor = Vendor(
            company_name=request.form.get("company_name"),
            vendor_type=request.form.get("vendor_type"),
            contact_person=request.form.get("contact_person"),
            phone=request.form.get("phone"),
            email=request.form.get("email"),
            address=request.form.get("address"),
            bank_name=request.form.get("bank_name"),
            account_name=request.form.get("account_name"),
            account_number=request.form.get("account_number"),
            cac_number=request.form.get("cac_number"),
            notes=request.form.get("notes"),
            status="pending",
        )

        if not vendor.company_name or not vendor.vendor_type:
            abort(400)

        db.session.add(vendor)
        db.session.commit()

        _log("created", vendor.id)
        db.session.commit()

        notify(
            subject="New Vendor Added",
            body=f"Vendor '{vendor.company_name}' has been added and awaits approval.",
            to_roles=["procurement"],
        )

        return redirect(url_for("vendors.view_vendor", vendor_id=vendor.id))

    return render_template("vendors/view.html", vendor=None)


@vendors_bp.route("/<int:vendor_id>")
@login_required
def view_vendor(vendor_id):
    vendor = Vendor.query.get_or_404(vendor_id)
    return render_template("vendors/view.html", vendor=vendor)


@vendors_bp.route("/<int:vendor_id>/action/<string:action>", methods=["POST"])
@login_required
def vendor_action(vendor_id, action):
    _require_roles("director")
    vendor = Vendor.query.get_or_404(vendor_id)

    if action == "approve":
        vendor.status = "approved"
    elif action == "reject":
        vendor.status = "rejected"
    else:
        abort(400)

    _log(action, vendor.id)
    db.session.commit()

    notify(
        subject=f"Vendor {vendor.status.title()}",
        body=f"Vendor '{vendor.company_name}' has been {vendor.status}.",
        to_roles=["procurement", "director"],
    )

    return redirect(url_for("vendors.view_vendor", vendor_id=vendor.id))
