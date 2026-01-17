from datetime import datetime
from flask import request
from flask_login import current_user
from app.extensions import db
from app.models.audit_log import AuditLog


def safe_log(
    *,
    entity_type,
    entity_id,
    action,
    changes=None,
):
    """
    Fire-and-forget audit logger.
    NEVER breaks app flow.
    """
    try:
        log = AuditLog(
            entity_type=entity_type,
            entity_id=str(entity_id),
            action=action,
            changes=changes or {},
            actor_user_id=getattr(current_user, "id", None),
            actor_role=getattr(current_user, "role", None),
            actor_name=getattr(current_user, "username", None),
            ip_address=request.remote_addr,
            user_agent=request.headers.get("User-Agent"),
            created_at=datetime.utcnow(),
        )
        db.session.add(log)
        db.session.commit()
    except Exception:
        db.session.rollback()
        # swallow error – audit must never block workflow


def init_audit(app):
    # nothing required here anymore
    pass
