from datetime import datetime
from flask import request
from flask_login import current_user
from app.extensions import db


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)

    # Core identifiers
    entity = db.Column(db.String(100), nullable=True)  # legacy compatibility
    entity_type = db.Column(db.String(100), nullable=True)
    entity_id = db.Column(db.String(50), nullable=True)

    action = db.Column(db.String(50), nullable=False)
    changes = db.Column(db.JSON, nullable=True)

    # Actor info
    actor_user_id = db.Column(db.Integer, nullable=True)
    actor_role = db.Column(db.String(50), nullable=True)
    actor_name = db.Column(db.String(100), nullable=True)

    # Request metadata
    ip_address = db.Column(db.String(100), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


def log_audit(entity_type, entity_id, action, changes=None):
    try:
        log = AuditLog(
            # write BOTH for safety
            entity=entity_type,
            entity_type=entity_type,
            entity_id=str(entity_id),
            action=action,
            changes=changes or {},

            actor_user_id=getattr(current_user, "id", None),
            actor_role=getattr(current_user, "role", None),
            actor_name=getattr(current_user, "username", None),

            ip_address=request.remote_addr if request else None,
            user_agent=request.headers.get("User-Agent") if request else None,
        )

        db.session.add(log)
        db.session.commit()

    except Exception:
        db.session.rollback()
        # audit must NEVER break business flow
        pass


def init_audit(app):
    # placeholder for future hooks (signals, SQLAlchemy events)
    pass
