from app import db
from datetime import datetime

# Association table for Event-NPC relationship
event_npcs = db.Table('event_npcs',
    db.Column('event_id', db.Integer, db.ForeignKey('event.id', ondelete='CASCADE'), primary_key=True),
    db.Column('npc_id', db.Integer, db.ForeignKey('npc.id', ondelete='CASCADE'), primary_key=True)
)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    event_date = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    
    # Relationship with NPCs
    npcs = db.relationship('NPC', secondary=event_npcs, lazy='dynamic',
                         backref=db.backref('events', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Event {self.title}>' 