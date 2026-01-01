# app/models/payment.py
from datetime import datetime
from app.extensions import db


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)

    procurement_request_id = db.Column(
        db.Integer, db.ForeignKey("procurement_requests.id"), nullable=False, index=True
    )

    amount = db.Column(db.Numeric(12, 2), nullable=False)

    # frozen schema fields for payments
    method = db.Column(db.String(50), nullable=True)          # Transfer / Cash / POS / Cheque etc
    reference = db.Column(db.String(120), nullable=True)      # bank ref / narration / txn ref
    receipt = db.Column(db.String(255), nullable=True)        # uploaded file name
    paid_by = db.Column(db.String(80), nullable=True)         # username
    paid_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # relationship (NO backref conflict)
    procurement_request = db.relationship(
        "ProcurementRequest", back_populates="payments"
    )
