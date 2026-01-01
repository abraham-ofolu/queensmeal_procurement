# app/models/audit_log.py
from datetime import datetime
from app.extensions import db


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(80), nullable=True)
    role = db.Column(db.String(30), nullable=True)

    action = db.Column(db.String(200), nullable=False)        # e.g. "PROCUREMENT_CREATE"
    entity_type = db.Column(db.String(50), nullable=True)     # "ProcurementRequest", "Payment", "Vendor"
    entity_id = db.Column(db.Integer, nullable=True)

    details = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
