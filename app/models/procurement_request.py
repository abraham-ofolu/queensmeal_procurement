from datetime import datetime
from app.extensions import db


class ProcurementRequest(db.Model):
    __tablename__ = "procurement_requests"

    id = db.Column(db.Integer, primary_key=True)

    # Core request details
    item = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)

    # 🚨 URGENCY FLAG (THIS IS WHAT WAS MISSING)
    is_urgent = db.Column(db.Boolean, default=False, nullable=False)
       


    # Status flow
    # pending  -> waiting for director
    # approved -> approved by director
    # rejected -> rejected by director
    status = db.Column(db.String(50), default="pending", nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    quotations = db.relationship(
        "ProcurementQuotation",
        back_populates="procurement_request",
        cascade="all, delete-orphan"
    )

    approvals = db.relationship(
        "ApprovalAction",
        cascade="all, delete-orphan"
    )

    payments = db.relationship(
        "Payment",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        urgency = "URGENT" if self.is_urgent else "NORMAL"
        return f"<ProcurementRequest {self.id} | {self.item} | {urgency} | {self.status}>"
