# app/models/procurement_request.py
from datetime import datetime
from app.extensions import db


class ProcurementRequest(db.Model):
    __tablename__ = "procurement_requests"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)

    amount = db.Column(db.Numeric(12, 2), nullable=False)

    # pending / approved / rejected
    status = db.Column(db.String(20), default="pending", nullable=False, index=True)

    created_by = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    needed_by = db.Column(db.String(30), nullable=True)

    # Vendor link (frozen)
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendors.id"), nullable=True, index=True)

    # Quotation file (frozen)
    quotation = db.Column(db.String(255), nullable=True)

    # approvals (frozen)
    approved_by = db.Column(db.String(80), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)

    rejected_by = db.Column(db.String(80), nullable=True)
    rejected_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    vendor = db.relationship("Vendor", backref="procurement_requests")
    payments = db.relationship(
        "Payment",
        back_populates="procurement_request",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
