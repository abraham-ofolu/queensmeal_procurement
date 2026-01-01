# app/routes/audit.py
from flask import Blueprint, render_template
from flask_login import login_required, current_user

from app.extensions import db
from app.models.audit_log import AuditLog

audit_bp = Blueprint("audit", __name__, url_prefix="/audit")


@audit_bp.route("/")
@login_required
def audit_logs():
    # only director can view full audit log (simple rule)
    if getattr(current_user, "role", None) != "director":
        logs = (
            AuditLog.query.order_by(AuditLog.created_at.desc())
            .limit(100)
            .all()
        )
    else:
        logs = (
            AuditLog.query.order_by(AuditLog.created_at.desc())
            .limit(500)
            .all()
        )

    return render_template("audit/list.html", logs=logs)
