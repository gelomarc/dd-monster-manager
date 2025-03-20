from app import db
from datetime import datetime

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    players = db.relationship('Player', backref='campaign', lazy='dynamic', cascade='all, delete-orphan')
    npcs = db.relationship('NPC', backref='campaign', lazy='dynamic', cascade='all, delete-orphan')
    events = db.relationship('Event', backref='campaign', lazy='dynamic', cascade='all, delete-orphan')
    encounters = db.relationship('Encounter', backref='campaign', lazy='dynamic', cascade='all, delete-orphan')
    loot = db.relationship('Loot', back_populates='campaign', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Campaign {self.title}>' 