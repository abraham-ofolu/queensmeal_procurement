from datetime import datetime
from flask_login import current_user
from app.extensions import db
from app.models.audit_log import AuditLog


def log_audit(action, entity_type, entity_id=None):
    try:
        log = AuditLog(
            user=current_user.username if current_user.is_authenticated else "system",
            role=current_user.role if current_user.is_authenticated else "system",
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            timestamp=datetime.utcnow(),
        )
        db.session.add(log)
        db.session.commit()
    except Exception:
        db.session.rollback()
