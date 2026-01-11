from datetime import datetime
from app.extensions import db


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)

    procurement_id = db.Column(
        db.Integer,
        db.ForeignKey("procurement_requests.id"),
        nullable=False
    )

    amount = db.Column(db.Numeric(12, 2), nullable=False)

    paid_by = db.Column(db.String(50), nullable=False)  # finance | director

    receipt_path = db.Column(db.String(255), nullable=True)

    status = db.Column(
        db.String(50),
        nullable=False,
        default="paid"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )
