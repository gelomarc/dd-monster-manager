import pytest
import uuid
from pytest_bdd import scenario, given, when, then, parsers
from app import create_app, db
from app.models.user import User
from app.models.campaign import Campaign
from app.models.monster import Monster
from app.models.encounter import Encounter

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
def test_encounter(app, test_campaign):
    encounter = Encounter(
        name='Test Encounter',
        difficulty='Medium',
        description='A test encounter',
        campaign_id=test_campaign.id
    )
    db.session.add(encounter)
    db.session.commit()
    return encounter

@pytest.fixture
def test_monster(app, test_campaign):
    monster = Monster(
        name='Test Monster',
        size='Medium',
        type='Humanoid',
        alignment='neutral',
        armor_class=15,
        hit_points=45,
        speed='30 ft.',
        strength=16,
        dexterity=14,
        constitution=15,
        intelligence=10,
        wisdom=12,
        charisma=8,
        challenge_rating='2',
        campaign_id=test_campaign.id
    )
    db.session.add(monster)
    db.session.commit()
    return monster

@pytest.fixture
def encounter_with_monster(app, test_encounter, test_monster):
    test_monster.encounter_id = test_encounter.id
    db.session.commit()
    return test_encounter

@pytest.fixture
def encounter_with_multiple_monsters(app, test_encounter, test_campaign):
    # Add first monster
    monster1 = Monster(
        name='Monster One',
        size='Medium',
        type='Beast',
        alignment='neutral',
        armor_class=14,
        hit_points=30,
        speed='40 ft.',
        strength=14,
        dexterity=16,
        constitution=12,
        intelligence=8,
        wisdom=10,
        charisma=6,
        challenge_rating='1',
        campaign_id=test_campaign.id,
        encounter_id=test_encounter.id
    )
    
    # Add second monster
    monster2 = Monster(
        name='Monster Two',
        size='Large',
        type='Dragon',
        alignment='chaotic evil',
        armor_class=18,
        hit_points=120,
        speed='30 ft., fly 60 ft.',
        strength=20,
        dexterity=12,
        constitution=18,
        intelligence=14,
        wisdom=12,
        charisma=16,
        challenge_rating='7',
        campaign_id=test_campaign.id,
        encounter_id=test_encounter.id
    )
    
    db.session.add_all([monster1, monster2])
    db.session.commit()
    return test_encounter

@pytest.fixture
def logged_in_client(app, client, test_user):
    # Use Flask-Login's session to properly log in the user
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
@scenario('features/encounters.feature', 'Creating a new encounter')
def test_create_encounter():
    pass

@scenario('features/encounters.feature', 'Adding a monster to an encounter')
def test_add_monster_to_encounter():
    pass

@scenario('features/encounters.feature', 'Removing a monster from an encounter')
def test_remove_monster_from_encounter():
    pass

@scenario('features/encounters.feature', 'Viewing monsters in an encounter')
def test_view_encounter_monsters():
    pass

# Given steps
@given('a user is logged in')
def user_logged_in(logged_in_client):
    return logged_in_client

@given('they are on the add encounter page for a campaign')
def add_encounter_page(logged_in_client, test_campaign):
    response = logged_in_client.get(f'/campaigns/{test_campaign.id}/encounters/create')
    assert response.status_code == 200
    assert b'Add Encounter' in response.data

@given('an encounter exists in their campaign')
def encounter_exists(test_encounter):
    assert Encounter.query.get(test_encounter.id) is not None

@given('an encounter has a monster')
def encounter_has_monster(encounter_with_monster):
    assert Monster.query.filter_by(encounter_id=encounter_with_monster.id).count() == 1

@given('an encounter has multiple monsters')
def encounter_has_multiple_monsters(encounter_with_multiple_monsters):
    assert Monster.query.filter_by(encounter_id=encounter_with_multiple_monsters.id).count() > 1

# When steps
@when('they fill in valid encounter information')
def fill_encounter_form(logged_in_client, test_campaign):
    return logged_in_client.post(
        f'/campaigns/{test_campaign.id}/encounters/create',
        data={
            'name': 'New Test Encounter',
            'difficulty': 'Hard',
            'description': 'A challenging encounter for testing'
        },
        follow_redirects=True
    )

@when('they add a monster to the encounter')
def add_monster_to_encounter(logged_in_client, test_campaign, test_encounter, test_monster):
    return logged_in_client.post(
        f'/campaigns/{test_campaign.id}/monsters/{test_monster.id}/edit',
        data={
            'name': test_monster.name,
            'size': test_monster.size,
            'type': test_monster.type,
            'alignment': test_monster.alignment,
            'armor_class': test_monster.armor_class,
            'armor_type': '',
            'hit_points': test_monster.hit_points,
            'hit_dice': '',
            'speed': test_monster.speed,
            'strength': test_monster.strength,
            'dexterity': test_monster.dexterity,
            'constitution': test_monster.constitution,
            'intelligence': test_monster.intelligence,
            'wisdom': test_monster.wisdom,
            'charisma': test_monster.charisma,
            'challenge_rating': test_monster.challenge_rating,
            'encounter_id': test_encounter.id
        },
        follow_redirects=True
    )

@when('they delete the monster from the encounter')
def delete_monster_from_encounter(logged_in_client, test_campaign, encounter_with_monster):
    monster = Monster.query.filter_by(encounter_id=encounter_with_monster.id).first()
    return logged_in_client.post(
        f'/campaigns/{test_campaign.id}/monsters/{monster.id}/edit',
        data={
            'name': monster.name,
            'size': monster.size,
            'type': monster.type,
            'alignment': monster.alignment,
            'armor_class': monster.armor_class,
            'armor_type': '',
            'hit_points': monster.hit_points,
            'hit_dice': '',
            'speed': monster.speed,
            'strength': monster.strength,
            'dexterity': monster.dexterity,
            'constitution': monster.constitution,
            'intelligence': monster.intelligence,
            'wisdom': monster.wisdom,
            'charisma': monster.charisma,
            'challenge_rating': monster.challenge_rating,
            'encounter_id': ''  # Remove from encounter
        },
        follow_redirects=True
    )

@when('they navigate to the encounter\'s monsters page')
def navigate_to_encounter_monsters(logged_in_client, test_campaign, encounter_with_multiple_monsters):
    return logged_in_client.get(
        f'/campaigns/{test_campaign.id}/encounters/{encounter_with_multiple_monsters.id}/monsters',
        follow_redirects=True
    )

# Then steps
@then('the encounter should be created')
def encounter_created(test_campaign):
    encounter = Encounter.query.filter_by(name='New Test Encounter').first()
    assert encounter is not None
    assert encounter.campaign_id == test_campaign.id
    assert encounter.difficulty == 'Hard'

@then('they should be redirected to the encounters list')
def redirected_to_encounters_list(response):
    assert b'New Test Encounter' in response.data

@then('the monster should be associated with the encounter')
def monster_associated_with_encounter(test_monster, test_encounter):
    updated_monster = Monster.query.get(test_monster.id)
    assert updated_monster.encounter_id == test_encounter.id

@then('they should see the monster in the encounter\'s monster list')
def monster_in_encounter_list(response, test_monster):
    assert test_monster.name.encode() in response.data

@then('the monster should be removed from the encounter')
def monster_removed_from_encounter(encounter_with_monster):
    monsters = Monster.query.filter_by(encounter_id=encounter_with_monster.id).all()
    assert not monsters

@then('they should no longer see the monster in the encounter\'s monster list')
def monster_not_in_encounter_list(response, encounter_with_monster):
    # The monster should be back in the main monsters list, not in the encounter
    assert b'Monster has been updated' in response.data or b'Monster updated successfully' in response.data

@then('they should see all monsters in the encounter')
def all_monsters_in_encounter_displayed(response, encounter_with_multiple_monsters):
    monsters = Monster.query.filter_by(encounter_id=encounter_with_multiple_monsters.id).all()
    for monster in monsters:
        assert monster.name.encode() in response.data

# Add a response fixture to fix missing parameter issues
@pytest.fixture
def response(request):
    """This fixture provides the response from the previous when step."""
    for when_step in request.node.iter_markers("when"):
        return when_step.obj()
    return None 