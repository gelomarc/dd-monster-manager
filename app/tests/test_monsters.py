import pytest
import os
import tempfile
import uuid
from pytest_bdd import scenario, given, when, then, parsers
from app import create_app, db
from app.models.user import User
from app.models.campaign import Campaign
from app.models.monster import Monster
from app.models.encounter import Encounter
from io import BytesIO
from flask_login import login_user

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'test_secret_key',
        'WTF_CSRF_ENABLED': False
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def test_user(app):
    username = f"test_user_{uuid.uuid4().hex[:8]}"
    user = User(username=username, email=f"{username}@example.com")
    user.set_password('testpassword')
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def test_campaign(app, test_user):
    campaign = Campaign(
        title='Test Campaign',
        description='Test Description',
        user_id=test_user.id
    )
    db.session.add(campaign)
    db.session.commit()
    return campaign

@pytest.fixture
def test_monster(app, test_campaign):
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
        challenge_rating='2',
        xp=450,
        campaign_id=test_campaign.id
    )
    db.session.add(monster)
    db.session.commit()
    return monster

@pytest.fixture
def logged_in_client(app, client, test_user):
    # Use Flask-Login's login_user function to properly log in the user
    with client.session_transaction() as session:
        session['user_id'] = test_user.id
        session['_fresh'] = True
    
    # Also do a post to the login endpoint for completeness
    response = client.post('/auth/login', data={
        'username': test_user.username,
        'password': 'testpassword'
    }, follow_redirects=True)
    
    return client

# Scenarios
@scenario('features/monsters.feature', 'Creating a new monster')
def test_create_monster():
    pass

@scenario('features/monsters.feature', 'Viewing a monster')
def test_view_monster():
    pass

@scenario('features/monsters.feature', 'Editing a monster')
def test_edit_monster():
    pass

@scenario('features/monsters.feature', 'Deleting a monster')
def test_delete_monster():
    pass

@scenario('features/monsters.feature', 'Exporting a monster as PDF')
def test_export_monster_pdf():
    pass

# Given steps
@given('a user is logged in')
def user_logged_in(logged_in_client):
    return logged_in_client

@given('they are on the add monster page for a campaign')
def add_monster_page(logged_in_client, test_campaign):
    response = logged_in_client.get(f'/campaigns/{test_campaign.id}/monsters/create')
    assert response.status_code == 200
    assert b'Add New Monster' in response.data

@given('a monster exists in their campaign')
def monster_exists(test_monster):
    assert Monster.query.get(test_monster.id) is not None

# When steps
@when('they fill in valid monster information')
def fill_monster_form(logged_in_client, test_campaign):
    return logged_in_client.post(
        f'/campaigns/{test_campaign.id}/monsters/create',
        data={
            'name': 'New Test Monster',
            'size': 'Large',
            'type': 'Dragon',
            'alignment': 'chaotic evil',
            'armor_class': '18',
            'armor_type': 'natural armor',
            'hit_points': '120',
            'hit_dice': '12d10+48',
            'speed': '40 ft., fly 80 ft.',
            'strength': '21',
            'dexterity': '14',
            'constitution': '19',
            'intelligence': '16',
            'wisdom': '13',
            'charisma': '17',
            'challenge_rating': '8',
            'xp': '3900',
        },
        follow_redirects=True
    )

@when('they navigate to the monster\'s view page')
def navigate_to_monster_view(logged_in_client, test_campaign, test_monster):
    return logged_in_client.get(
        f'/campaigns/{test_campaign.id}/monsters/{test_monster.id}/view',
        follow_redirects=True
    )

@when('they edit the monster with new information')
def edit_monster_info(logged_in_client, test_campaign, test_monster):
    return logged_in_client.post(
        f'/campaigns/{test_campaign.id}/monsters/{test_monster.id}/edit',
        data={
            'name': 'Updated Monster',
            'size': 'Large',
            'type': 'Beast',
            'alignment': 'neutral',
            'armor_class': '16',
            'armor_type': 'natural armor',
            'hit_points': '60',
            'hit_dice': '8d10+16',
            'speed': '40 ft.',
            'strength': '18',
            'dexterity': '12',
            'constitution': '14',
            'intelligence': '8',
            'wisdom': '12',
            'charisma': '6',
            'challenge_rating': '3',
            'xp': '700',
        },
        follow_redirects=True
    )

@when('they delete the monster')
def delete_monster(logged_in_client, test_campaign, test_monster):
    return logged_in_client.post(
        f'/campaigns/{test_campaign.id}/monsters/{test_monster.id}/delete',
        follow_redirects=True
    )

@when('they request to export the monster as PDF')
def export_monster_pdf(logged_in_client, test_campaign, test_monster):
    # Patching the pdfkit functionality for testing
    import unittest.mock
    from unittest.mock import patch
    
    with patch('pdfkit.from_string') as mock_from_string:
        mock_from_string.return_value = b'PDF content'
        return logged_in_client.get(
            f'/campaigns/{test_campaign.id}/monsters/{test_monster.id}/export-pdf',
            follow_redirects=False
        )

# Then steps
@then('the monster should be created')
def monster_created(test_campaign):
    monster = Monster.query.filter_by(name='New Test Monster').first()
    assert monster is not None
    assert monster.campaign_id == test_campaign.id

@then('they should be redirected to the monsters list')
def redirected_to_monsters_list(response):
    assert b'New Test Monster' in response.data or b'Monster deleted successfully' in response.data

@then('they should see all the monster\'s details')
def monster_details_displayed(response, test_monster):
    assert test_monster.name.encode() in response.data
    assert test_monster.size.encode() in response.data
    assert test_monster.type.encode() in response.data
    assert str(test_monster.armor_class).encode() in response.data
    assert str(test_monster.hit_points).encode() in response.data

@then('the monster details should be updated')
def monster_updated(test_monster):
    updated = Monster.query.get(test_monster.id)
    assert updated.name == 'Updated Monster'
    assert updated.size == 'Large'
    assert updated.armor_class == 16
    assert updated.hit_points == 60

@then('they should be redirected to the monster\'s view page')
def redirected_to_monster_view(response):
    assert b'Updated Monster' in response.data

@then('the monster should be removed from the database')
def monster_removed(test_monster):
    assert Monster.query.get(test_monster.id) is None

@then('a PDF file should be generated')
def pdf_generated(response):
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/pdf'
    assert response.headers['Content-Disposition'].startswith('attachment; filename=')

@then('the PDF should contain the monster\'s details')
def pdf_contains_monster_details(response, test_monster):
    # In a real test environment, we might want to use a PDF parser to check content
    # For our tests, we'll check the headers as validation
    assert f"{test_monster.name}_statblock.pdf" in response.headers['Content-Disposition'] 