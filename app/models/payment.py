from datetime import datetime
from ..extensions import db

class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)

    procurement_request_id = db.Column(
        db.Integer,
        db.ForeignKey("procurement_requests.id", ondelete="CASCADE"),
        nullable=False,
    )

    amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    paid_by = db.Column(db.String(30), nullable=False)  # finance or director

    receipt_path = db.Column(db.String(255), nullable=True)

    status = db.Column(db.String(30), nullable=False, default="approved")  
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    request = db.relationship("ProcurementRequest", back_populates="payments")

    def __repr__(self):
        return f"<Payment {self.id} {self.amount} {self.paid_by}>"
