from datetime import datetime
from app.extensions import db


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)

    procurement_request_id = db.Column(
        db.Integer,
        db.ForeignKey("procurement_requests.id"),
        nullable=False
    )

    amount = db.Column(db.Numeric(12, 2), nullable=False)

    # director OR finance
    paid_by_role = db.Column(db.String(50), nullable=False)

    # username of payer
    paid_by_name = db.Column(db.String(100), nullable=False)

    # Cloudinary receipt
    receipt_url = db.Column(db.String(500), nullable=True)
    receipt_public_id = db.Column(db.String(255), nullable=True)

    status = db.Column(db.String(50), default="paid", nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    procurement_request = db.relationship("ProcurementRequest")

    def __repr__(self):
        return f"<Payment {self.id} {self.amount} by {self.paid_by_role}>"
