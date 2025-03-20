import os
import pytest
import io
import json
from unittest.mock import patch, MagicMock
from PIL import Image, ImageDraw
from flask import url_for
from app import create_app, db
from app.models.user import User
from app.models.campaign import Campaign

class TestOCRAPI:
    """Integration tests for the OCR API endpoint."""
    
    @pytest.fixture
    def app(self):
        """Create and configure a Flask app for testing."""
        app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})
        
        # Create the database and load test data
        with app.app_context():
            db.create_all()
            
            # Create a test user
            user = User(username='testuser', email='test@example.com')
            user.set_password('password')
            db.session.add(user)
            
            # Create a test campaign
            campaign = Campaign(title='Test Campaign', description='Test Description', user_id=1)
            db.session.add(campaign)
            
            db.session.commit()
        
        yield app
    
    @pytest.fixture
    def client(self, app):
        """A test client for the app."""
        return app.test_client()
    
    @pytest.fixture
    def auth_client(self, client):
        """A test client with authentication."""
        client.post('/auth/login', data={'username': 'testuser', 'password': 'password'})
        return client
    
    @pytest.fixture
    def test_image(self):
        """Create a test image."""
        image = Image.new('RGB', (300, 400), color='white')
        d = ImageDraw.Draw(image)
        d.text((10, 10), "Dragon", fill='black')
        d.text((10, 30), "Medium Dragon, Neutral", fill='black')
        d.text((10, 50), "AC 15", fill='black')
        d.text((10, 70), "HP 50", fill='black')
        
        img_io = io.BytesIO()
        image.save(img_io, 'JPEG')
        img_io.seek(0)
        
        return img_io
    
    @patch('app.routes.monsters.extract_text_from_image')
    @patch('app.routes.monsters.parse_monster_data')
    def test_scan_image_success(self, mock_parse, mock_extract, auth_client, test_image):
        """Test successful image scanning and data extraction."""
        # Mock OCR function returns
        mock_extract.return_value = "Dragon\nMedium Dragon, Neutral\nAC 15\nHP 50"
        mock_parse.return_value = {
            'name': 'Dragon',
            'size': 'medium',
            'type': 'dragon',
            'alignment': 'neutral',
            'armor_class': 15,
            'hit_points': 50
        }
        
        # Create the upload data
        data = {
            'statblock_image': (test_image, 'test_image.jpg')
        }
        
        # Call the API
        response = auth_client.post('/campaigns/1/monsters/scan-image', data=data, content_type='multipart/form-data')
        
        # Check response
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert response_data['monster_data']['name'] == 'Dragon'
        assert response_data['monster_data']['armor_class'] == 15
        
        # Verify mocks were called
        mock_extract.assert_called_once()
        mock_parse.assert_called_once()
    
    @patch('app.routes.monsters.extract_text_from_image')
    def test_scan_image_extraction_failure(self, mock_extract, auth_client, test_image):
        """Test handling of OCR extraction failure."""
        # Mock OCR function to return None (extraction failed)
        mock_extract.return_value = None
        
        # Create the upload data
        data = {
            'statblock_image': (test_image, 'test_image.jpg')
        }
        
        # Call the API
        response = auth_client.post('/campaigns/1/monsters/scan-image', data=data, content_type='multipart/form-data')
        
        # Check response
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert 'Could not extract text' in response_data['message']
        
        # Verify mock was called
        mock_extract.assert_called_once()
    
    @patch('app.routes.monsters.extract_text_from_image')
    @patch('app.routes.monsters.parse_monster_data')
    def test_scan_image_parsing_failure(self, mock_parse, mock_extract, auth_client, test_image):
        """Test handling of parsing failure."""
        # Mock OCR function returns
        mock_extract.return_value = "Some text that won't parse correctly"
        mock_parse.return_value = {}  # Empty dict = parsing failed
        
        # Create the upload data
        data = {
            'statblock_image': (test_image, 'test_image.jpg')
        }
        
        # Call the API
        response = auth_client.post('/campaigns/1/monsters/scan-image', data=data, content_type='multipart/form-data')
        
        # Check response
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert 'Could not parse monster data' in response_data['message']
        
        # Verify mocks were called
        mock_extract.assert_called_once()
        mock_parse.assert_called_once()
    
    def test_scan_image_no_file(self, auth_client):
        """Test handling when no file is uploaded."""
        # Call the API with empty data
        response = auth_client.post('/campaigns/1/monsters/scan-image', data={}, content_type='multipart/form-data')
        
        # Check response
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert 'No image file uploaded' in response_data['message']
    
    def test_scan_image_empty_file(self, auth_client):
        """Test handling when an empty file is uploaded."""
        # Create empty file data
        data = {
            'statblock_image': (io.BytesIO(), '')
        }
        
        # Call the API
        response = auth_client.post('/campaigns/1/monsters/scan-image', data=data, content_type='multipart/form-data')
        
        # Check response
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert 'No image file selected' in response_data['message']
    
    def test_scan_image_unauthorized(self, client, test_image):
        """Test handling when user is not authenticated."""
        # Create the upload data
        data = {
            'statblock_image': (test_image, 'test_image.jpg')
        }
        
        # Call the API without authentication
        response = client.post('/campaigns/1/monsters/scan-image', data=data, content_type='multipart/form-data')
        
        # Should redirect to login page
        assert response.status_code == 302
        assert '/auth/login' in response.location
    
    @patch('app.routes.monsters.logger.error')
    @patch('app.routes.monsters.extract_text_from_image')
    def test_scan_image_exception(self, mock_extract, mock_log, auth_client, test_image):
        """Test handling of exceptions during image processing."""
        # Simulate an exception during extraction
        mock_extract.side_effect = Exception("Test exception")
        
        # Create the upload data
        data = {
            'statblock_image': (test_image, 'test_image.jpg')
        }
        
        # Call the API
        response = auth_client.post('/campaigns/1/monsters/scan-image', data=data, content_type='multipart/form-data')
        
        # Check response
        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert 'Error processing image' in response_data['message']
        
        # Verify exception was logged
        mock_log.assert_called_once() 