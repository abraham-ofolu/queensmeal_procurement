from datetime import datetime
from app.extensions import db

class ProcurementRequest(db.Model):
    __tablename__ = "procurement_requests"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)

    amount = db.Column(db.Numeric(12, 2), nullable=False)

    vendor_id = db.Column(
        db.Integer,
        db.ForeignKey("vendors.id"),
        nullable=False
    )

    status = db.Column(
        db.String(50),
        default="pending",
        nullable=False
    )

    created_by_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    def __repr__(self):
        return f"<ProcurementRequest {self.id} - {self.title}>"
