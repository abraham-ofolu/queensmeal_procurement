from app.extensions import db
from datetime import datetime


class ProcurementRequest(db.Model):
    __tablename__ = "procurement_requests"

    id = db.Column(db.Integer, primary_key=True)

    item = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)

    # 🔴 URGENCY (THIS WAS MISSING)
    urgent = db.Column(db.Boolean, default=False)

    status = db.Column(
        db.String(20),
        default="pending",  # pending | approved | rejected | paid
        nullable=False,
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    quotations = db.relationship(
        "ProcurementQuotation",
        back_populates="procurement_request",
        cascade="all, delete-orphan",
    )
