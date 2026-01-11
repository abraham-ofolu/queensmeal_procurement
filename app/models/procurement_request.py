from datetime import datetime
from app.extensions import db


class ProcurementRequest(db.Model):
    __tablename__ = "procurement_requests"

    id = db.Column(db.Integer, primary_key=True)

    item = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    amount = db.Column(db.Float, nullable=False, default=0.0)

    # Status rules:
    # pending -> procurement can edit/upload quotation
    # pending_director -> director must approve/reject
    # approved -> finance can pay if within limit; director can pay if over limit
    # rejected -> view only
    # paid -> read-only
    status = db.Column(db.String(50), nullable=False, default="pending")

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Cloudinary quotation
    quotation_url = db.Column(db.Text, nullable=True)
    quotation_public_id = db.Column(db.Text, nullable=True)

    payments = db.relationship("Payment", backref="procurement_request", lazy=True)

    def __repr__(self):
        return f"<ProcurementRequest {self.id} {self.item} {self.status}>"
