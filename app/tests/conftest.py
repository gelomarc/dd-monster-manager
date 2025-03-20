import os
import tempfile
import pytest
from app import create_app, db
from app.models.user import User

@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    os.close(db_fd)  # Close the file descriptor immediately
    
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test'
    })

    with app.app_context():
        db.create_all()
        # Create a test user
        user = User(username='test', email='test@example.com')
        user.set_password('test')
        db.session.add(user)
        db.session.commit()

    yield app

    # Clean up
    with app.app_context():
        db.session.remove()
        db.drop_all()
    
    try:
        os.unlink(db_path)
    except:
        pass  # Ignore errors during cleanup

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

class AuthActions:
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')

@pytest.fixture
def auth(client):
    return AuthActions(client) 