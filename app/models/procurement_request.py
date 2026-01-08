from datetime import datetime
from app.extensions import db


class ProcurementRequest(db.Model):
    __tablename__ = "procurement_requests"

    id = db.Column(db.Integer, primary_key=True)

    item = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.String(100), nullable=False)
    estimated_cost = db.Column(db.Float, nullable=False)

    vendor_id = db.Column(db.Integer, db.ForeignKey("vendors.id"), nullable=True)

    quotation_url = db.Column(db.Text, nullable=True)

    status = db.Column(db.String(50), default="pending")

    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    payments = db.relationship(
        "Payment",
        backref="procurement",
        cascade="all, delete-orphan",
        lazy=True,
    )
