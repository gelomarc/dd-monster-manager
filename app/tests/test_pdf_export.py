import pytest
import unittest.mock
import uuid
from unittest.mock import patch, MagicMock
from app import create_app, db
from app.models.user import User
from app.models.campaign import Campaign
from app.models.monster import Monster
from io import BytesIO

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
        skills='Perception +3, Stealth +4',
        challenge_rating='2',
        xp=450,
        special_abilities='Keen Senses: The monster has advantage on Wisdom (Perception) checks that rely on sight.',
        actions='Multiattack: The monster makes two attacks.\nSlash: +5 to hit, reach 5 ft., one target. Hit: 7 (1d8+3) slashing damage.',
        campaign_id=test_campaign.id
    )
    db.session.add(monster)
    db.session.commit()
    return monster

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

class TestPDFExport:
    @patch('pdfkit.from_string')
    @patch('tempfile.NamedTemporaryFile')
    def test_pdf_generation(self, mock_tempfile, mock_from_string, logged_in_client, test_campaign, test_monster):
        # Mock tempfile
        mock_temp = MagicMock()
        mock_temp.name = '/tmp/test.pdf'
        mock_tempfile.return_value.__enter__.return_value = mock_temp
        
        # Mock PDF content
        mock_from_string.return_value = b'PDF content'
        
        # Make request to export PDF
        response = logged_in_client.get(f'/campaigns/{test_campaign.id}/monsters/{test_monster.id}/export-pdf')
        
        # Assertions
        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'application/pdf'
        assert f"{test_monster.name}_statblock.pdf" in response.headers['Content-Disposition']
        
        # Verify pdfkit was called with correct parameters
        mock_from_string.assert_called_once()
        # First argument is the rendered HTML
        assert isinstance(mock_from_string.call_args[0][0], str)
        # Should contain monster details
        assert test_monster.name in mock_from_string.call_args[0][0]
        assert str(test_monster.armor_class) in mock_from_string.call_args[0][0]
        
        # Check correct options were passed
        options = mock_from_string.call_args[0][2]
        assert options['page-size'] == 'Letter'
        assert 'margin-top' in options
        assert 'encoding' in options
    
    def test_pdf_content_structure(self, app, client, test_user, test_campaign, test_monster):
        # This test checks the structure of the HTML template that will be rendered for PDF
        # Ensure test_user is attached to a session
        with client.session_transaction() as session:
            session['user_id'] = test_user.id
            session['_fresh'] = True
        
        # Get the rendered template
        response = client.get(f'/campaigns/{test_campaign.id}/monsters/{test_monster.id}/view')
        
        # Verify essential elements exist
        assert test_monster.name.encode() in response.data
        assert str(test_monster.armor_class).encode() in response.data
        assert str(test_monster.hit_points).encode() in response.data
        assert test_monster.size.encode() in response.data
        assert test_monster.type.encode() in response.data
        
        # Check ability scores
        assert str(test_monster.strength).encode() in response.data
        assert str(test_monster.dexterity).encode() in response.data
        assert str(test_monster.constitution).encode() in response.data
        assert str(test_monster.intelligence).encode() in response.data
        assert str(test_monster.wisdom).encode() in response.data
        assert str(test_monster.charisma).encode() in response.data
        
        # Check special abilities and actions
        if test_monster.special_abilities:
            assert b'Special Abilities' in response.data
            assert test_monster.special_abilities.encode() in response.data
        
        if test_monster.actions:
            assert b'Actions' in response.data
            assert test_monster.actions.replace('\n', '<br>').encode() in response.data or test_monster.actions.encode() in response.data
    
    @patch('pdfkit.from_string')
    def test_pdf_export_error_handling(self, mock_from_string, logged_in_client, test_campaign, test_monster):
        # Simulate an error during PDF generation
        mock_from_string.side_effect = Exception("PDF generation error")
        
        # Make request to export PDF
        response = logged_in_client.get(
            f'/campaigns/{test_campaign.id}/monsters/{test_monster.id}/export-pdf',
            follow_redirects=True
        )
        
        # Verify error handling
        assert response.status_code == 200
        assert b'Error generating PDF' in response.data
        
        # Should redirect back to monster view
        assert test_monster.name.encode() in response.data 