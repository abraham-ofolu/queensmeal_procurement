from datetime import datetime
from app.extensions import db


class ProcurementRequest(db.Model):
    __tablename__ = "procurement_requests"

    id = db.Column(db.Integer, primary_key=True)

    item = db.Column(db.String(255), nullable=False)

    # ✅ restored
    description = db.Column(db.Text, nullable=True)

    quantity = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)

    is_urgent = db.Column(db.Boolean, default=False, nullable=False)

    status = db.Column(db.String(50), default="pending", nullable=False)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # 🔗 Vendor
    vendor_id = db.Column(
        db.Integer,
        db.ForeignKey("vendors.id"),
        nullable=False
    )

    vendor = db.relationship(
        "Vendor",
        back_populates="procurement_requests"
    )

    # 🔗 Quotations
    quotations = db.relationship(
        "ProcurementQuotation",
        back_populates="procurement_request",
        cascade="all, delete-orphan"
    )

    # 🔗 Payments
    payments = db.relationship(
        "Payment",
        back_populates="procurement_request",
        cascade="all, delete-orphan"
    )
