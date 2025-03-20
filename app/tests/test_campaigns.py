import pytest
from pytest_bdd import scenario, given, when, then, parsers
from app import create_app, db
from app.models.user import User
from app.models.campaign import Campaign

@pytest.fixture
def client():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'test_secret_key'
    })
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

@pytest.fixture
def response():
    """Shared response fixture for test steps."""
    return {}

@pytest.fixture
def authenticated_client(client):
    with client.application.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpassword')
        db.session.add(user)
        db.session.commit()
        
    client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'testpassword'
    })
    
    return client

@scenario('features/campaigns.feature', 'View empty campaign list')
def test_view_empty_campaign_list():
    pass

@scenario('features/campaigns.feature', 'Create a new campaign')
def test_create_campaign():
    pass

@scenario('features/campaigns.feature', 'Delete an existing campaign')
def test_delete_campaign():
    pass

@given('the user is logged in')
def logged_in_user(authenticated_client):
    pass

@when('they visit the campaigns page')
def visit_campaigns_page(authenticated_client, response):
    result = authenticated_client.get('/campaigns', follow_redirects=True)
    response['result'] = result
    return result

@then('they should see an empty campaign list')
def see_empty_campaign_list(response):
    result = response['result']
    assert b'Your Campaigns' in result.data
    assert b"You don't have any campaigns yet" in result.data

@when('they go to the create campaign page')
def go_to_create_campaign(authenticated_client, response):
    result = authenticated_client.get('/campaigns/create', follow_redirects=True)
    response['result'] = result
    assert b'Add New Campaign' in result.data
    return result

@when('they create a new campaign with valid information')
def create_new_campaign(authenticated_client, response):
    result = authenticated_client.post('/campaigns/create', data={
        'title': 'Test Campaign',
        'description': 'This is a test campaign'
    }, follow_redirects=True)
    response['result'] = result
    return result

@then('they should see the campaign in the campaign list')
def see_campaign_in_list(response):
    result = response['result']
    assert b'Your Campaigns' in result.data
    assert b'Test Campaign' in result.data
    assert b'This is a test campaign' in result.data

@given('the user has created a campaign')
def user_with_campaign(authenticated_client):
    with authenticated_client.application.app_context():
        user = User.query.filter_by(username='testuser').first()
        campaign = Campaign(title='Test Campaign', description='This is a test campaign', user_id=user.id)
        db.session.add(campaign)
        db.session.commit()

@when('they delete the campaign')
def delete_campaign(authenticated_client, response):
    campaign_id = None
    with authenticated_client.application.app_context():
        campaign = Campaign.query.filter_by(title='Test Campaign').first()
        campaign_id = campaign.id
    
    result = authenticated_client.post(f'/campaigns/{campaign_id}/delete', follow_redirects=True)
    response['result'] = result
    return result

@then('the campaign should be removed from the list')
def campaign_removed(response):
    result = response['result']
    assert b'Your Campaigns' in result.data
    assert b'Test Campaign' not in result.data
    assert b"You don't have any campaigns yet" in result.data 