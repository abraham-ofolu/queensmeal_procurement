from datetime import datetime
from app.extensions import db


class ProcurementRequest(db.Model):
    __tablename__ = "procurement_requests"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

    amount = db.Column(db.Numeric(12, 2), nullable=False)

    vendor_id = db.Column(
        db.Integer,
        db.ForeignKey("vendors.id"),
        nullable=True
    )

    status = db.Column(
        db.String(50),
        default="pending",
        nullable=False
    )

    created_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # ✅ ONE clean relationship
    quotations = db.relationship(
        "ProcurementQuotation",
        back_populates="procurement",
        cascade="all, delete-orphan"
    )
