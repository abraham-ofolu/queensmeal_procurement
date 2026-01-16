from datetime import datetime
from app.extensions import db


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)

    procurement_request_id = db.Column(
        db.Integer,
        db.ForeignKey("procurement_requests.id"),
        nullable=False,
        index=True
    )

    amount_paid = db.Column(db.Numeric(12, 2), nullable=False)

    paid_by_user_id = db.Column(db.Integer, nullable=True)
    paid_by_role = db.Column(db.String(50), nullable=False)  # "finance" or "director"

    receipt_url = db.Column(db.String(500), nullable=True)   # proof of payment (Cloudinary URL)
    receipt_uploaded_at = db.Column(db.DateTime, nullable=True)

    notes = db.Column(db.String(500), nullable=True)

    paid_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    procurement_request = db.relationship(
        "ProcurementRequest",
        back_populates="payments",
        overlaps="payments"
    )
