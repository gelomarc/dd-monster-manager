from app import db
from datetime import datetime
import pdfkit
from pdfkit.configuration import Configuration

class Monster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    size = db.Column(db.String(20))
    type = db.Column(db.String(50))
    alignment = db.Column(db.String(50))
    
    # Basic stats
    armor_class = db.Column(db.Integer)
    armor_type = db.Column(db.String(100))
    hit_points = db.Column(db.Integer)
    hit_dice = db.Column(db.String(20))
    speed = db.Column(db.String(200))
    
    # Ability scores
    strength = db.Column(db.Integer, default=10)
    dexterity = db.Column(db.Integer, default=10)
    constitution = db.Column(db.Integer, default=10)
    intelligence = db.Column(db.Integer, default=10)
    wisdom = db.Column(db.Integer, default=10)
    charisma = db.Column(db.Integer, default=10)
    
    # Saving throws
    strength_save = db.Column(db.String(10))
    dexterity_save = db.Column(db.String(10))
    constitution_save = db.Column(db.String(10))
    intelligence_save = db.Column(db.String(10))
    wisdom_save = db.Column(db.String(10))
    charisma_save = db.Column(db.String(10))
    
    # Skills - stored as JSON string with format: {"skill_name": bonus}
    skills = db.Column(db.Text)
    
    # Resistances and vulnerabilities
    damage_vulnerabilities = db.Column(db.Text)
    damage_resistances = db.Column(db.Text)
    damage_immunities = db.Column(db.Text)
    condition_immunities = db.Column(db.Text)
    
    # Senses and languages
    senses = db.Column(db.Text)
    languages = db.Column(db.Text)
    
    # Challenge rating
    challenge_rating = db.Column(db.String(10))
    xp = db.Column(db.Integer)
    
    # Special abilities
    special_abilities = db.Column(db.Text)
    
    # Actions
    actions = db.Column(db.Text)
    
    # Bonus actions
    bonus_actions = db.Column(db.Text)
    
    # Reactions
    reactions = db.Column(db.Text)
    
    # Legendary features
    legendary_actions = db.Column(db.Text)
    legendary_resistance = db.Column(db.Integer, default=0)  # Number of legendary resistances per day
    
    # Lair actions
    lair_actions = db.Column(db.Text)
    
    # Description
    description = db.Column(db.Text)
    
    # Image URL (optional)
    image_url = db.Column(db.String(500))
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    encounter_id = db.Column(db.Integer, db.ForeignKey('encounter.id'), nullable=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    
    def __repr__(self):
        return f'<Monster {self.name}>'
    
    def ability_modifier(self, score):
        return (score - 10) // 2
    
    def strength_mod(self):
        return self.ability_modifier(self.strength)
    
    def dexterity_mod(self):
        return self.ability_modifier(self.dexterity)
    
    def constitution_mod(self):
        return self.ability_modifier(self.constitution)
    
    def intelligence_mod(self):
        return self.ability_modifier(self.intelligence)
    
    def wisdom_mod(self):
        return self.ability_modifier(self.wisdom)
    
    def charisma_mod(self):
        return self.ability_modifier(self.charisma)

    def export_pdf(self, rendered_html, temp_filename, options):
        config = Configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')  # Adjust path as needed
        pdfkit.from_string(rendered_html, temp_filename, options=options, configuration=config) 