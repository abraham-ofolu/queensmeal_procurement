from datetime import datetime
from app.extensions import db


class ProcurementRequest(db.Model):
    __tablename__ = "procurement_requests"

    id = db.Column(db.Integer, primary_key=True)

    item = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Float, nullable=False)

    # URGENCY
    is_urgent = db.Column(db.Boolean, nullable=False, default=False)

    # LINK TO VENDOR (THIS FIXES YOUR ERROR)
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendors.id"), nullable=True)

    # Optional quotation URL (Cloudinary link or file link)
    quotation_url = db.Column(db.Text, nullable=True)

    # Workflow status
    # pending -> approved -> paid
    # pending -> rejected
    status = db.Column(db.String(20), nullable=False, default="pending")

    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships (safe even if you don’t use them in templates yet)
    vendor = db.relationship("Vendor", backref=db.backref("procurement_requests", lazy=True))
