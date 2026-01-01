from datetime import datetime
from app.extensions import db


class ProcurementRequest(db.Model):
    __tablename__ = "procurement_requests"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)

    amount = db.Column(db.Numeric(12, 2), nullable=False)

    status = db.Column(db.String(20), nullable=False, default="pending")

    created_by = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    approved_by = db.Column(db.String(80), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)

    vendor_id = db.Column(db.Integer, db.ForeignKey("vendors.id"), nullable=True)
    quotation_filename = db.Column(db.String(255), nullable=True)
    needed_by = db.Column(db.Date, nullable=True)

    # ✅ This fixes: "ProcurementRequest has no attribute vendor"
    vendor = db.relationship("Vendor", lazy="joined")
