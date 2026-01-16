from datetime import datetime
from decimal import Decimal

from app.extensions import db


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)

    procurement_request_id = db.Column(
        db.Integer,
        db.ForeignKey("procurement_requests.id"),
        nullable=False
    )

    # IMPORTANT: Your DB has BOTH `amount` (NOT NULL) and `amount_paid` (nullable)
    # We will store the same value in both to keep schema stable.
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    amount_paid = db.Column(db.Numeric(12, 2), nullable=True)

    paid_by_role = db.Column(db.String(50), nullable=False)

    # IMPORTANT: Your DB requires paid_by_name NOT NULL.
    paid_by_name = db.Column(db.String(100), nullable=False)

    paid_by_user_id = db.Column(db.Integer, nullable=True)

    receipt_url = db.Column(db.String(500), nullable=True)
    receipt_public_id = db.Column(db.String(255), nullable=True)
    receipt_uploaded_at = db.Column(db.DateTime, nullable=True)

    notes = db.Column(db.String(500), nullable=True)

    status = db.Column(db.String(50), nullable=False, default="paid")

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
    paid_at = db.Column(db.DateTime, nullable=True)

    procurement_request = db.relationship(
        "ProcurementRequest",
        back_populates="payments",
        overlaps="payments"
    )

    @staticmethod
    def normalize_amount(value) -> Decimal:
        # Handles strings like "20,000" safely
        if value is None:
            return Decimal("0.00")
        s = str(value).strip().replace(",", "")
        if s == "":
            return Decimal("0.00")
        return Decimal(s)
