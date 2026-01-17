from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app.models.audit_log import AuditLog

audit_bp = Blueprint("audit", __name__, url_prefix="/audit")


def _role():
    return (getattr(current_user, "role", "") or "").lower()


@audit_bp.route("/", methods=["GET"])
@login_required
def index():
    if _role() != "director":
        flash("You are not allowed to view the audit trail.", "danger")
        return redirect(url_for("procurement.index"))

    entity = (request.args.get("entity") or "").strip()
    action = (request.args.get("action") or "").strip()

    q = AuditLog.query.order_by(AuditLog.created_at.desc())

    if entity:
        q = q.filter(AuditLog.entity_type.ilike(f"%{entity}%"))
    if action:
        q = q.filter(AuditLog.action.ilike(f"%{action}%"))

    logs = q.limit(500).all()  # last 500 actions
    return render_template("audit/index.html", logs=logs, entity=entity, action=action)
