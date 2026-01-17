from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app.models.audit_log import AuditLog

audit_bp = Blueprint("audit", __name__, url_prefix="/audit")


def _role():
    return (getattr(current_user, "role", "") or "").lower()


@audit_bp.route("/")
@login_required
def index():
    # Only Director + Audit role can view
    if _role() not in ("director", "audit"):
        flash("You are not allowed to view Audit Trail.", "danger")
        return redirect(url_for("procurement.index"))

    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(200).all()
    return render_template("audit/index.html", logs=logs)
