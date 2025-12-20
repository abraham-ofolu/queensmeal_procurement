from app.extensions import db

class RequestDocument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer)
    doc_type = db.Column(db.String(50))
