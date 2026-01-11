from datetime import datetime
from ..extensions import db

class ProcurementQuotation(db.Model):
    __tablename__ = "procurement_quotations"

    id = db.Column(db.Integer, primary_key=True)

    procurement_request_id = db.Column(
        db.Integer,
        db.ForeignKey("procurement_requests.id", ondelete="CASCADE"),
        nullable=False,
    )

    filename = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    request = db.relationship(
        "ProcurementRequest",
        back_populates="quotations",
    )

    def __repr__(self):
        return f"<ProcurementQuotation {self.id} {self.filename}>"
