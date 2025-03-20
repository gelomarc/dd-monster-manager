from app import db
from datetime import datetime

class Encounter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.String(50))  # Easy, Medium, Hard, etc.
    description = db.Column(db.Text)
    monsters = db.Column(db.Text)  # Simple text list of monsters (kept for backward compatibility)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    
    # Relationship with monster statblocks
    monster_statblocks = db.relationship('Monster', backref='encounter', lazy='dynamic', cascade='all, delete-orphan')
    loot = db.relationship('Loot', back_populates='encounter', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Encounter {self.name}>' 