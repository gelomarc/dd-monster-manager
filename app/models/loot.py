from datetime import datetime
from app import db

class Loot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    value = db.Column(db.String(50))
    rarity = db.Column(db.String(50))
    attunement = db.Column(db.Boolean, nullable=False, default=False)
    notes = db.Column(db.Text)
    
    # Foreign keys
    encounter_id = db.Column(db.Integer, db.ForeignKey('encounter.id', ondelete='CASCADE'), nullable=False, index=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    encounter = db.relationship('Encounter', back_populates='loot')
    campaign = db.relationship('Campaign', back_populates='loot')
    
    def __repr__(self):
        return f'<Loot {self.name}>' 