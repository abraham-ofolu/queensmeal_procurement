from datetime import datetime
from app.extensions import db


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)

    # legacy + new columns (keep both to avoid schema mismatch)
    entity = db.Column(db.String(100), nullable=False)            # legacy NOT NULL in your DB
    entity_type = db.Column(db.String(100), nullable=True)        # newer
    entity_id = db.Column(db.String(50), nullable=True)

    action = db.Column(db.String(50), nullable=False)

    changes = db.Column(db.JSON, nullable=True)

    actor_user_id = db.Column(db.Integer, nullable=True)
    actor_role = db.Column(db.String(50), nullable=True)
    actor_name = db.Column(db.String(100), nullable=True)

    ip_address = db.Column(db.String(100), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
