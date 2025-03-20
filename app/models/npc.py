from app import db
from datetime import datetime

class NPC(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    attitude = db.Column(db.String(20), nullable=False, default='neutral')  # hostile, neutral, friendly
    places_to_find = db.Column(db.Text)
    description = db.Column(db.Text)
    equipment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    
    def __repr__(self):
        return f'<NPC {self.name}>' 