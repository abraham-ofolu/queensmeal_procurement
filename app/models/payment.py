from datetime import datetime
from app.extensions import db


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)

    procurement_request_id = db.Column(
        db.Integer,
        db.ForeignKey("procurement_requests.id"),
        nullable=False,
        index=True,
    )

    amount = db.Column(db.Float, nullable=False, default=0.0)

    # "finance" or "director"
    paid_by_role = db.Column(db.String(50), nullable=False)

    # optional: store username/email if you want
    paid_by_name = db.Column(db.String(120), nullable=True)

    receipt_url = db.Column(db.Text, nullable=True)
    receipt_public_id = db.Column(db.Text, nullable=True)

    status = db.Column(db.String(50), nullable=False, default="paid")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Payment {self.id} req={self.procurement_request_id} {self.amount} by {self.paid_by_role}>"
