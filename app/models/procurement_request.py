from datetime import datetime
from app.extensions import db


class ProcurementRequest(db.Model):
    __tablename__ = "procurement_requests"

    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    status = db.Column(db.String(50), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 🔴 THIS IS THE LINE YOU ASKED ABOUT
    quotations = db.relationship(
        "ProcurementQuotation",
        back_populates="procurement_request",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<ProcurementRequest {self.item}>"
