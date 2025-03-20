import os
import io
import pytest
from unittest.mock import patch, MagicMock
from app.utils.ocr import extract_text_from_image, parse_monster_data

@pytest.fixture
def sample_statblock_text():
    return """SPHINX OF WONDER
Tiny Celestial, Lawful Good
AC 13
HP 24 (7d4 + 7)
Speed 20ft., Fly 40ft.

STR   DEX   CON   INT   WIS   CHA
6(-2) 17(+3) 13(+1) 15(+2) 11(+0) 11(+0)

Skills: Arcana +4, Religion +4, Stealth +5
Condition Immunities: Charmed, Paralyzed, Radiant
Senses: Darkvision 60 ft., Passive Perception 11
Languages: Common
CR 1 (XP 200; PB +2)

TRAITS
Magic Resistance: The sphinx has Advantage on saving throws against spells and other magical effects.

ACTIONS
Bend, Make, Confuse Roll: +5, reach 5ft. Hit: (1d4 + 3) Slashing damage plus 7 (2d6) Radiant damage.

REACTIONS
Burst of Ingenuity (2/Day). Trigger: The sphinx or another creature within 10 feet makes an ability check or a saving throw. Response: The sphinx adds 2 to the roll."""

@pytest.mark.parametrize("test_input,expected", [
    ("Small Dragon, Neutral Good", {'size': 'small', 'type': 'dragon', 'alignment': 'neutral good'}),
    ("AC 15", {'armor_class': 15}),
    ("HP 45 (7d8 + 14)", {'hit_points': 45, 'hit_dice': '7d8 + 14'}),
    ("Speed 30 ft., fly 60 ft.", {'speed': '30 ft., fly 60 ft.'}),
    ("STR 18 (+4)", {'strength': 18}),
    ("Skills Perception +5, Stealth +4", {'skills': 'Perception +5, Stealth +4'}),
    ("CR 5 (1,800 XP)", {'challenge_rating': '5', 'xp': 1800}),
])
def test_regex_patterns(test_input, expected):
    """Test individual regex patterns for extracting monster data."""
    result = parse_monster_data(test_input)
    for key, value in expected.items():
        assert result.get(key) == value

def test_parse_monster_data(sample_statblock_text):
    """Test parsing a complete monster statblock."""
    result = parse_monster_data(sample_statblock_text)
    
    # Check basic information
    assert result['name'] == 'SPHINX OF WONDER'
    assert result['size'] == 'tiny'
    assert result['type'] == 'celestial'
    assert result['alignment'] == 'lawful good'
    
    # Check stats
    assert result['armor_class'] == 13
    assert result['hit_points'] == 24
    assert result['hit_dice'] == '7d4 + 7'
    assert result['speed'] == '20ft., Fly 40ft.'
    
    # Check ability scores
    assert result['strength'] == 6
    assert result['dexterity'] == 17
    assert result['constitution'] == 13
    assert result['intelligence'] == 15
    assert result['wisdom'] == 11
    assert result['charisma'] == 11
    
    # Check skills and features
    assert 'Arcana +4' in result['skills']
    assert 'Stealth +5' in result['skills']
    assert result['challenge_rating'] == '1'
    assert result['xp'] == 200
    
    # Check sections
    assert 'Magic Resistance' in result['special_abilities']
    assert 'Bend, Make, Confuse Roll' in result['actions']
    assert 'Burst of Ingenuity' in result['reactions']

@patch('app.utils.ocr.pytesseract.image_to_string')
@patch('app.utils.ocr.cv2')
@patch('app.utils.ocr.Image')
def test_extract_text_from_image(mock_image, mock_cv2, mock_image_to_string):
    """Test the image-to-text extraction functionality."""
    # Mock the image preprocessing
    mock_cv2.imdecode.return_value = MagicMock()
    mock_cv2.cvtColor.return_value = MagicMock()
    mock_cv2.threshold.return_value = (None, MagicMock())
    mock_cv2.fastNlMeansDenoising.return_value = MagicMock()
    
    # Mock the image conversion
    mock_image.fromarray.return_value = MagicMock()
    
    # Mock the OCR result
    expected_text = "Test Monster\nTiny Fey, Chaotic Good"
    mock_image_to_string.return_value = expected_text
    
    # Call the function with a mock image
    result = extract_text_from_image(b'test_image_bytes')
    
    # Verify the result
    assert result == expected_text
    
    # Verify the function calls
    mock_cv2.imdecode.assert_called_once()
    mock_cv2.cvtColor.assert_called_once()
    mock_cv2.threshold.assert_called_once()
    mock_cv2.fastNlMeansDenoising.assert_called_once()
    mock_image.fromarray.assert_called_once()
    mock_image_to_string.assert_called_once() 