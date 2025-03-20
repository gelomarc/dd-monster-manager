import os
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from unittest.mock import patch, MagicMock
import time
import json
from app import create_app, db
from app.models.user import User
from app.models.campaign import Campaign

class TestOCRClient:
    """Client-side tests for OCR functionality using Selenium.
    
    Note: These tests require a browser driver to be installed.
    Skip these if running in an environment without browser support.
    """
    
    @pytest.fixture(scope='module')
    def driver(self):
        """Set up and tear down a browser for tests."""
        # Skip if no browser driver available or in CI
        if os.environ.get('CI') or os.environ.get('SKIP_BROWSER_TESTS'):
            pytest.skip("Skipping browser tests in CI environment")
            
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            driver = webdriver.Chrome(options=options)
            yield driver
            driver.quit()
        except Exception as e:
            pytest.skip(f"Browser driver not available: {str(e)}")
    
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
    def mock_ocr_response(self):
        """A mock OCR response to use in tests."""
        return {
            'success': True,
            'message': 'Monster data extracted successfully!',
            'monster_data': {
                'name': 'Dragon',
                'size': 'medium',
                'type': 'dragon',
                'alignment': 'neutral',
                'armor_class': 15,
                'hit_points': 50,
                'strength': 18,
                'dexterity': 14,
                'constitution': 16,
                'intelligence': 16,
                'wisdom': 12,
                'charisma': 14,
                'special_abilities': 'Fire Breath: The dragon breathes fire in a 15-foot cone.',
                'actions': 'Bite: +6 to hit, 1d10+4 piercing damage.'
            },
            'raw_text': 'Dragon\nMedium Dragon, Neutral\nAC 15\nHP 50'
        }
    
    def test_setFieldValue_function(self, driver):
        """Test the setFieldValue helper function in isolation."""
        # Skip if driver not available
        if driver is None:
            pytest.skip("No browser driver available")
        
        # Create a simple HTML page with a form field
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test</title>
        </head>
        <body>
            <input type="text" name="test_field">
            <textarea name="test_area"></textarea>
            <select name="test_select">
                <option value="option1">Option 1</option>
                <option value="option2">Option 2</option>
            </select>
            <script>
                function setFieldValue(selector, value) {
                    const field = document.querySelector(selector);
                    if (field && value !== undefined && value !== null) {
                        field.value = value;
                    }
                    return field ? true : false;
                }
            </script>
        </body>
        </html>
        """
        
        # Load the HTML
        driver.get("data:text/html;charset=utf-8," + html)
        
        # Test setting value on existing field
        result = driver.execute_script(
            "return setFieldValue('input[name=\"test_field\"]', 'test value');"
        )
        assert result is True
        
        # Verify the value was set
        value = driver.execute_script(
            "return document.querySelector('input[name=\"test_field\"]').value;"
        )
        assert value == "test value"
        
        # Test setting value on non-existent field
        result = driver.execute_script(
            "return setFieldValue('input[name=\"nonexistent\"]', 'test value');"
        )
        assert result is False
        
        # Test handling null/undefined values
        result = driver.execute_script(
            "return setFieldValue('input[name=\"test_field\"]', null);"
        )
        assert result is True
        
        # Value should not change when null/undefined
        value = driver.execute_script(
            "return document.querySelector('input[name=\"test_field\"]').value;"
        )
        assert value == "test value"  # Still has previous value
    
    def test_populateFormFields_function(self, driver):
        """Test the populateFormFields function."""
        # Skip if driver not available
        if driver is None:
            pytest.skip("No browser driver available")
        
        # Create a simplified version of the monster form
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test</title>
        </head>
        <body>
            <form id="monster-form">
                <input type="text" name="name">
                <select name="size">
                    <option value="tiny">Tiny</option>
                    <option value="small">Small</option>
                    <option value="medium">Medium</option>
                    <option value="large">Large</option>
                </select>
                <input type="text" name="type">
                <input type="text" name="alignment">
                <input type="number" name="armor_class">
                <input type="number" name="hit_points">
                <input type="number" name="strength">
                <input type="number" name="dexterity">
                <input type="number" name="constitution">
                <input type="number" name="intelligence">
                <input type="number" name="wisdom">
                <input type="number" name="charisma">
                <textarea name="special_abilities"></textarea>
                <textarea name="actions"></textarea>
            </form>
            
            <script>
                function setFieldValue(selector, value) {
                    const field = document.querySelector(selector);
                    if (field && value !== undefined && value !== null) {
                        field.value = value;
                    }
                }
                
                function populateFormFields(monsterData) {
                    // Populate basic info
                    setFieldValue('input[name="name"]', monsterData.name);
                    setFieldValue('select[name="size"]', monsterData.size);
                    setFieldValue('input[name="type"]', monsterData.type);
                    setFieldValue('input[name="alignment"]', monsterData.alignment);
                    
                    // Basic stats
                    setFieldValue('input[name="armor_class"]', monsterData.armor_class);
                    setFieldValue('input[name="hit_points"]', monsterData.hit_points);
                    
                    // Ability scores
                    setFieldValue('input[name="strength"]', monsterData.strength);
                    setFieldValue('input[name="dexterity"]', monsterData.dexterity);
                    setFieldValue('input[name="constitution"]', monsterData.constitution);
                    setFieldValue('input[name="intelligence"]', monsterData.intelligence);
                    setFieldValue('input[name="wisdom"]', monsterData.wisdom);
                    setFieldValue('input[name="charisma"]', monsterData.charisma);
                    
                    // Abilities and actions
                    setFieldValue('textarea[name="special_abilities"]', monsterData.special_abilities);
                    setFieldValue('textarea[name="actions"]', monsterData.actions);
                }
            </script>
        </body>
        </html>
        """
        
        # Load the HTML
        driver.get("data:text/html;charset=utf-8," + html)
        
        # Test the populateFormFields function with sample data
        monster_data = {
            'name': 'Dragon',
            'size': 'medium',
            'type': 'dragon',
            'alignment': 'neutral',
            'armor_class': 15,
            'hit_points': 50,
            'strength': 18,
            'dexterity': 14,
            'constitution': 16,
            'intelligence': 16,
            'wisdom': 12,
            'charisma': 14,
            'special_abilities': 'Fire Breath: The dragon breathes fire in a 15-foot cone.',
            'actions': 'Bite: +6 to hit, 1d10+4 piercing damage.'
        }
        
        # Execute the function
        driver.execute_script(f"populateFormFields({json.dumps(monster_data)});")
        
        # Verify values were set correctly
        assert driver.find_element(By.NAME, "name").get_attribute("value") == "Dragon"
        assert driver.find_element(By.NAME, "size").get_attribute("value") == "medium"
        assert driver.find_element(By.NAME, "type").get_attribute("value") == "dragon"
        assert driver.find_element(By.NAME, "armor_class").get_attribute("value") == "15"
        assert driver.find_element(By.NAME, "strength").get_attribute("value") == "18"
        assert driver.find_element(By.NAME, "special_abilities").get_attribute("value") == "Fire Breath: The dragon breathes fire in a 15-foot cone."
    
    def test_populateFormFields_with_missing_fields(self, driver):
        """Test populateFormFields handles missing fields gracefully."""
        # Skip if driver not available
        if driver is None:
            pytest.skip("No browser driver available")
        
        # Create HTML with missing form fields
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test</title>
        </head>
        <body>
            <form id="monster-form">
                <input type="text" name="name">
                <!-- Missing: size -->
                <input type="text" name="type">
                <!-- Missing: alignment -->
                <input type="number" name="armor_class">
            </form>
            
            <script>
                function setFieldValue(selector, value) {
                    const field = document.querySelector(selector);
                    if (field && value !== undefined && value !== null) {
                        field.value = value;
                    }
                }
                
                function populateFormFields(monsterData) {
                    // Populate basic info - includes missing fields
                    setFieldValue('input[name="name"]', monsterData.name);
                    setFieldValue('select[name="size"]', monsterData.size);
                    setFieldValue('input[name="type"]', monsterData.type);
                    setFieldValue('input[name="alignment"]', monsterData.alignment);
                    setFieldValue('input[name="armor_class"]', monsterData.armor_class);
                }
            </script>
        </body>
        </html>
        """
        
        # Load the HTML
        driver.get("data:text/html;charset=utf-8," + html)
        
        # Test with data that includes fields not in the form
        monster_data = {
            'name': 'Dragon',
            'size': 'medium',  # This field is missing
            'type': 'dragon',
            'alignment': 'neutral',  # This field is missing
            'armor_class': 15
        }
        
        # Execute the function - should not throw error
        driver.execute_script(f"populateFormFields({json.dumps(monster_data)});")
        
        # Verify existing fields were set correctly
        assert driver.find_element(By.NAME, "name").get_attribute("value") == "Dragon"
        assert driver.find_element(By.NAME, "type").get_attribute("value") == "dragon"
        assert driver.find_element(By.NAME, "armor_class").get_attribute("value") == "15"
    
    def test_populateFormFields_with_null_values(self, driver):
        """Test populateFormFields handles null values gracefully."""
        # Skip if driver not available
        if driver is None:
            pytest.skip("No browser driver available")
        
        # Create HTML with form fields
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test</title>
        </head>
        <body>
            <form id="monster-form">
                <input type="text" name="name" value="Initial Name">
                <input type="text" name="type" value="Initial Type">
            </form>
            
            <script>
                function setFieldValue(selector, value) {
                    const field = document.querySelector(selector);
                    if (field && value !== undefined && value !== null) {
                        field.value = value;
                    }
                }
                
                function populateFormFields(monsterData) {
                    // Populate with some null values
                    setFieldValue('input[name="name"]', monsterData.name);
                    setFieldValue('input[name="type"]', monsterData.type);
                }
            </script>
        </body>
        </html>
        """
        
        # Load the HTML
        driver.get("data:text/html;charset=utf-8," + html)
        
        # Test with data that includes null values
        monster_data = {
            'name': 'Dragon',
            'type': None  # This value is null
        }
        
        # Execute the function
        driver.execute_script(f"populateFormFields({json.dumps(monster_data)});")
        
        # Verify values
        assert driver.find_element(By.NAME, "name").get_attribute("value") == "Dragon"
        assert driver.find_element(By.NAME, "type").get_attribute("value") == "Initial Type"  # Should not change 