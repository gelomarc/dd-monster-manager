import pytest
from pytest_bdd import scenario, given, when, then, parsers
from app import create_app, db
from app.models.user import User

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

@scenario('features/auth.feature', 'User registration')
def test_user_registration():
    pass

@scenario('features/auth.feature', 'User login')
def test_user_login():
    pass

@scenario('features/auth.feature', 'User logout')
def test_user_logout():
    pass

@given('the user is on the registration page')
def registration_page(client):
    response = client.get('/auth/register')
    assert response.status_code == 200
    assert b'Register' in response.data
    return response

@when('they fill in valid registration information')
def fill_registration_form(client, response):
    result = client.post('/auth/register', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpassword'
    }, follow_redirects=True)
    response['result'] = result
    return result

@then('they should be redirected to the login page')
def redirected_to_login(response):
    result = response['result']
    assert b'Login' in result.data
    assert b'You have successfully registered' in result.data

@given('a registered user')
def registered_user(client):
    user = User(username='testuser', email='test@example.com')
    user.set_password('testpassword')
    with client.application.app_context():
        db.session.add(user)
        db.session.commit()

@given('the user is on the login page')
def login_page(client):
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Login' in response.data
    return response

@when('they fill in valid login credentials')
def fill_login_form(client, response):
    result = client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'testpassword'
    }, follow_redirects=True)
    response['result'] = result
    return result

@then('they should be redirected to the campaigns page')
def redirected_to_campaigns(response):
    result = response['result']
    assert b'Your Campaigns' in result.data
    assert b'You have successfully logged in' in result.data

@given('the user is logged in')
def logged_in_user(client):
    client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'testpassword'
    })

@when('they click on the logout button')
def click_logout(client, response):
    result = client.get('/auth/logout', follow_redirects=True)
    response['result'] = result
    return result

@then('they should be redirected to the index page')
def redirected_to_index(response):
    result = response['result']
    assert b'Welcome to DD Monsters' in result.data
    assert b'You have been logged out' in result.data 