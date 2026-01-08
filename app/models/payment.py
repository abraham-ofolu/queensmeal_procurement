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
    method = db.Column(db.String(50), nullable=False)

    # ✅ Cloudinary URL ONLY (no filename, no local path)
    receipt_url = db.Column(db.String(500), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    procurement = db.relationship("ProcurementRequest", backref="payments")
