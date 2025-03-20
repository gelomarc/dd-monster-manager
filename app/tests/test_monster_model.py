import pytest
from app import create_app, db
from app.models.monster import Monster
from app.models.campaign import Campaign
from app.models.encounter import Encounter
from app.models.user import User
import uuid

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'test_secret_key'
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

class TestMonsterModel:
    def test_monster_creation(self, app):
        # Create a test user
        username = f"test_user_{uuid.uuid4().hex[:8]}"
        user = User(username=username, email=f"{username}@example.com")
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        
        # Create a test campaign
        campaign = Campaign(title='Test Campaign', description='Test description', user_id=user.id)
        db.session.add(campaign)
        db.session.commit()
        
        # Create a monster
        monster = Monster(
            name='Test Monster',
            size='Medium',
            type='Humanoid',
            alignment='neutral',
            armor_class=15,
            armor_type='natural armor',
            hit_points=45,
            hit_dice='6d8+12',
            speed='30 ft.',
            strength=16,
            dexterity=14,
            constitution=15,
            intelligence=10,
            wisdom=12,
            charisma=8,
            skills='Perception +3, Stealth +4',
            challenge_rating='2',
            xp=450,
            campaign_id=campaign.id
        )
        db.session.add(monster)
        db.session.commit()
        
        # Test monster was created correctly
        saved_monster = Monster.query.filter_by(name='Test Monster').first()
        assert saved_monster is not None
        assert saved_monster.name == 'Test Monster'
        assert saved_monster.size == 'Medium'
        assert saved_monster.type == 'Humanoid'
        assert saved_monster.alignment == 'neutral'
        assert saved_monster.armor_class == 15
        assert saved_monster.armor_type == 'natural armor'
        assert saved_monster.hit_points == 45
        assert saved_monster.hit_dice == '6d8+12'
    
    def test_ability_modifiers(self, app):
        # Create a test user
        username = f"test_user_{uuid.uuid4().hex[:8]}"
        user = User(username=username, email=f"{username}@example.com")
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        
        # Create a test campaign
        campaign = Campaign(title='Test Campaign', description='Test description', user_id=user.id)
        db.session.add(campaign)
        db.session.commit()
        
        # Create a monster with different ability scores
        monster = Monster(
            name='Ability Test Monster',
            campaign_id=campaign.id,
            strength=20,      # Modifier should be +5
            dexterity=16,     # Modifier should be +3
            constitution=14,  # Modifier should be +2
            intelligence=10,  # Modifier should be +0
            wisdom=8,         # Modifier should be -1
            charisma=6        # Modifier should be -2
        )
        db.session.add(monster)
        db.session.commit()
        
        # Test ability modifiers
        assert monster.strength_mod() == 5
        assert monster.dexterity_mod() == 3
        assert monster.constitution_mod() == 2
        assert monster.intelligence_mod() == 0
        assert monster.wisdom_mod() == -1
        assert monster.charisma_mod() == -2
    
    def test_monster_encounter_relationship(self, app):
        # Create a test user
        username = f"test_user_{uuid.uuid4().hex[:8]}"
        user = User(username=username, email=f"{username}@example.com")
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        
        # Create a test campaign
        campaign = Campaign(title='Test Campaign', description='Test description', user_id=user.id)
        db.session.add(campaign)
        db.session.commit()
        
        # Create an encounter
        encounter = Encounter(
            name='Test Encounter',
            campaign_id=campaign.id
        )
        db.session.add(encounter)
        db.session.commit()
        
        # Create monsters for the encounter
        monster1 = Monster(
            name='Monster One',
            campaign_id=campaign.id,
            encounter_id=encounter.id
        )
        
        monster2 = Monster(
            name='Monster Two',
            campaign_id=campaign.id,
            encounter_id=encounter.id
        )
        
        db.session.add_all([monster1, monster2])
        db.session.commit()
        
        # Test the relationship
        encounter_monsters = Monster.query.filter_by(encounter_id=encounter.id).all()
        assert len(encounter_monsters) == 2
        assert 'Monster One' in [m.name for m in encounter_monsters]
        assert 'Monster Two' in [m.name for m in encounter_monsters]
        
        # Test cascade deletion
        db.session.delete(encounter)
        db.session.commit()
        
        # Monsters should be deleted when encounter is deleted
        orphaned_monsters = Monster.query.filter_by(encounter_id=encounter.id).all()
        assert len(orphaned_monsters) == 0 