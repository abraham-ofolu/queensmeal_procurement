from __future__ import annotations

from datetime import datetime

from app.extensions import db


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)

    entity_type = db.Column(db.String(100), nullable=False)   # e.g., ProcurementRequest
    entity_id = db.Column(db.String(50), nullable=True)       # string to be safe across types
    action = db.Column(db.String(20), nullable=False)         # create/update/delete

    # Store field-level changes as JSON (Postgres supports JSONB)
    changes = db.Column(db.JSON, nullable=False, default=dict)

    actor_user_id = db.Column(db.Integer, nullable=True)
    actor_role = db.Column(db.String(50), nullable=True)
    actor_name = db.Column(db.String(150), nullable=True)

    ip_address = db.Column(db.String(100), nullable=True)
    user_agent = db.Column(db.String(300), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<AuditLog {self.id} {self.action} {self.entity_type}:{self.entity_id}>"
