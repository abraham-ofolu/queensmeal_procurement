from __future__ import annotations

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user

from app.models.audit_log import AuditLog


audit_bp = Blueprint("audit", __name__, url_prefix="/audit")


def _role() -> str:
    return (getattr(current_user, "role", "") or "").lower()


def _require_role(*roles):
    if _role() not in [r.lower() for r in roles]:
        flash("You are not allowed to access that page.", "danger")
        return False
    return True


@audit_bp.route("/")
@login_required
def index():
    # Director only (you can expand later)
    if not _require_role("director"):
        return redirect(url_for("procurement.index"))

    entity_type = (request.args.get("entity_type") or "").strip()
    action = (request.args.get("action") or "").strip()
    q = AuditLog.query

    if entity_type:
        q = q.filter(AuditLog.entity_type == entity_type)
    if action:
        q = q.filter(AuditLog.action == action)

    logs = q.order_by(AuditLog.created_at.desc()).limit(500).all()
    return render_template("audit/index.html", logs=logs, entity_type=entity_type, action=action)


@audit_bp.route("/request/<int:request_id>")
@login_required
def request_timeline(request_id: int):
    # Director only
    if not _require_role("director"):
        return redirect(url_for("procurement.index"))

    logs = (
        AuditLog.query
        .filter(AuditLog.entity_type == "ProcurementRequest", AuditLog.entity_id == str(request_id))
        .order_by(AuditLog.created_at.asc())
        .all()
    )
    return render_template("audit/request.html", request_id=request_id, logs=logs)
