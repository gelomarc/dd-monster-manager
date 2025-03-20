import pytest
from app.models.loot import Loot
from app.models.campaign import Campaign
from app.models.encounter import Encounter
from app import db

def test_create_loot(client, auth, app):
    auth.login()
    
    # Create a campaign
    with client:
        response = client.post('/campaigns/create', data={
            'title': 'Test Campaign',
            'description': 'Test Description'
        })
        campaign_id = Campaign.query.filter_by(title='Test Campaign').first().id
    
    # Create an encounter
    with client:
        response = client.post(f'/campaigns/{campaign_id}/encounters/create', data={
            'name': 'Test Encounter',
            'difficulty': 'Medium',
            'description': 'Test Description',
            'monsters': 'Goblin, Orc'
        })
        encounter_id = Encounter.query.filter_by(name='Test Encounter').first().id
    
    # Create loot
    response = client.post(f'/campaigns/{campaign_id}/encounters/{encounter_id}/loot/create', data={
        'name': 'Magic Sword',
        'description': 'A powerful magic sword',
        'quantity': 1,
        'value': '100 gp',
        'rarity': 'Rare',
        'attunement': True,
        'notes': 'Requires attunement by a warrior'
    })
    assert response.status_code == 302  # Redirect after successful creation
    
    # Verify loot was created
    with app.app_context():
        loot = Loot.query.filter_by(name='Magic Sword').first()
        assert loot is not None
        assert loot.description == 'A powerful magic sword'
        assert loot.quantity == 1
        assert loot.value == '100 gp'
        assert loot.rarity == 'Rare'
        assert loot.attunement is True
        assert loot.notes == 'Requires attunement by a warrior'
        assert loot.encounter_id == encounter_id
        assert loot.campaign_id == campaign_id

def test_edit_loot(client, auth, app):
    auth.login()
    
    # Create initial data
    with app.app_context():
        campaign = Campaign(title='Test Campaign', description='Test Description', user_id=1)
        db.session.add(campaign)
        db.session.commit()
        
        encounter = Encounter(name='Test Encounter', campaign_id=campaign.id)
        db.session.add(encounter)
        db.session.commit()
        
        loot = Loot(
            name='Old Sword',
            description='An old sword',
            quantity=1,
            encounter_id=encounter.id,
            campaign_id=campaign.id
        )
        db.session.add(loot)
        db.session.commit()
        
        # Edit loot
        response = client.post(f'/campaigns/{campaign.id}/encounters/{encounter.id}/loot/{loot.id}/edit', data={
            'name': 'New Sword',
            'description': 'A new sword',
            'quantity': 2,
            'value': '200 gp',
            'rarity': 'Very Rare',
            'attunement': True,
            'notes': 'Updated notes'
        })
        assert response.status_code == 302  # Redirect after successful edit
        
        # Verify changes
        updated_loot = Loot.query.get(loot.id)
        assert updated_loot.name == 'New Sword'
        assert updated_loot.description == 'A new sword'
        assert updated_loot.quantity == 2
        assert updated_loot.value == '200 gp'
        assert updated_loot.rarity == 'Very Rare'
        assert updated_loot.attunement is True
        assert updated_loot.notes == 'Updated notes'

def test_delete_loot(client, auth, app):
    auth.login()
    
    # Create initial data
    with app.app_context():
        campaign = Campaign(title='Test Campaign', description='Test Description', user_id=1)
        db.session.add(campaign)
        db.session.commit()
        
        encounter = Encounter(name='Test Encounter', campaign_id=campaign.id)
        db.session.add(encounter)
        db.session.commit()
        
        loot = Loot(
            name='Test Loot',
            description='Test Description',
            quantity=1,
            encounter_id=encounter.id,
            campaign_id=campaign.id
        )
        db.session.add(loot)
        db.session.commit()
        loot_id = loot.id
        
        # Delete loot
        response = client.post(f'/campaigns/{campaign.id}/encounters/{encounter.id}/loot/{loot_id}/delete')
        assert response.status_code == 302  # Redirect after successful deletion
        
        # Verify deletion
        assert Loot.query.get(loot_id) is None

def test_unauthorized_access(client, auth, app):
    # Create test data
    with app.app_context():
        # Create a campaign owned by user 2
        campaign = Campaign(title='Other Campaign', description='Other Description', user_id=2)
        db.session.add(campaign)
        db.session.commit()
        campaign_id = campaign.id
        
        encounter = Encounter(name='Other Encounter', campaign_id=campaign.id)
        db.session.add(encounter)
        db.session.commit()
        encounter_id = encounter.id
        
        loot = Loot(
            name='Other Loot',
            description='Other Description',
            quantity=1,
            encounter_id=encounter.id,
            campaign_id=campaign.id
        )
        db.session.add(loot)
        db.session.commit()
        loot_id = loot.id
    
    # Login as user 1
    auth.login()
    
    # Try to access loot owned by user 2
    response = client.get(f'/campaigns/{campaign_id}/encounters/{encounter_id}/loot')
    assert response.status_code == 302  # Redirect to campaigns list
    
    response = client.post(f'/campaigns/{campaign_id}/encounters/{encounter_id}/loot/create', data={
        'name': 'New Loot',
        'description': 'New Description'
    })
    assert response.status_code == 302  # Redirect to campaigns list
    
    response = client.post(f'/campaigns/{campaign_id}/encounters/{encounter_id}/loot/{loot_id}/edit', data={
        'name': 'Updated Loot',
        'description': 'Updated Description'
    })
    assert response.status_code == 302  # Redirect to campaigns list
    
    response = client.post(f'/campaigns/{campaign_id}/encounters/{encounter_id}/loot/{loot_id}/delete')
    assert response.status_code == 302  # Redirect to campaigns list 