from app.extensions import db

class ApprovalAction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer)
    actor = db.Column(db.String(100))
    action = db.Column(db.String(50))
