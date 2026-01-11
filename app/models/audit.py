from datetime import datetime
from app.extensions import db


class Audit(db.Model):
    __tablename__ = "audits"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)

    entity_type = db.Column(
        db.String(50),
        nullable=False
    )  # e.g. procurement, payment

    entity_id = db.Column(
        db.Integer,
        nullable=False,
        index=True
    )

    action = db.Column(
        db.String(100),
        nullable=False
    )

    performed_by = db.Column(
        db.String(100),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )
