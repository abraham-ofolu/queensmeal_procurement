from datetime import datetime
from app.extensions import db


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)

    entity_type = db.Column(db.String(80), nullable=False)   # e.g. ProcurementRequest, Vendor, Payment
    entity_id = db.Column(db.Integer, nullable=True)

    action = db.Column(db.String(50), nullable=False)        # e.g. created, updated, status_changed, deleted
    summary = db.Column(db.String(500), nullable=True)

    actor_user_id = db.Column(db.Integer, nullable=True)
    actor_username = db.Column(db.String(120), nullable=True)
    actor_role = db.Column(db.String(50), nullable=True)

    ip_address = db.Column(db.String(64), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    meta = db.Column(db.JSON, nullable=True)
