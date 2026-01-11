from datetime import datetime
from ..extensions import db

class ProcurementRequest(db.Model):
    __tablename__ = "procurement_requests"

    id = db.Column(db.Integer, primary_key=True)

    item = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)

    status = db.Column(db.String(30), nullable=False, default="pending")  
    # pending -> director approve/reject
    # approved -> read-only
    # rejected -> view-only

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # store one “main” quotation filename for quick display (optional)
    quotation_file = db.Column(db.String(255), nullable=True)

    quotations = db.relationship(
        "ProcurementQuotation",
        back_populates="request",
        cascade="all, delete-orphan",
        lazy=True,
    )

    payments = db.relationship(
        "Payment",
        back_populates="request",
        cascade="all, delete-orphan",
        lazy=True,
    )

    def __repr__(self):
        return f"<ProcurementRequest {self.id} {self.item} {self.status}>"
