from datetime import datetime
from app.extensions import db


class ProcurementQuotation(db.Model):
    __tablename__ = "procurement_quotations"

    id = db.Column(db.Integer, primary_key=True)

    procurement_request_id = db.Column(
        db.Integer,
        db.ForeignKey("procurement_requests.id"),
        nullable=False
    )

    file_url = db.Column(db.String(500), nullable=False)

    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ✅ MATCHING RELATIONSHIP
    procurement_request = db.relationship(
        "ProcurementRequest",
        back_populates="quotations"
    )

    def __repr__(self):
        return f"<ProcurementQuotation {self.id} for request {self.procurement_request_id}>"
