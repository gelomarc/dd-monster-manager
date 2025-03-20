import os
import unittest
from unittest.mock import patch, MagicMock, mock_open
import pytest
import io
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Try to import from either module
try:
    from app.utils.ocr import extract_text_from_image, parse_monster_data, extract_section
except ImportError:
    from app.utils.simple_ocr import extract_text_from_image, parse_monster_data, extract_section

class TestOCRUtils(unittest.TestCase):
    """Test OCR utility functions."""
    
    def test_extract_section(self):
        """Test the extract_section function."""
        # Test case with multiple sections
        text = """
        TRAITS
        This is a trait.
        Another trait line.
        
        ACTIONS
        This is an action.
        Another action line.
        
        REACTIONS
        This is a reaction.
        """
        
        # Test extracting traits section
        traits = extract_section(text, ["TRAITS"])
        self.assertIsNotNone(traits)
        self.assertIn("This is a trait", traits)
        self.assertIn("Another trait line", traits)
        self.assertNotIn("This is an action", traits)
        
        # Test extracting actions section
        actions = extract_section(text, ["ACTIONS"])
        self.assertIsNotNone(actions)
        self.assertIn("This is an action", actions)
        self.assertIn("Another action line", actions)
        self.assertNotIn("This is a reaction", actions)
        
        # Test extracting reactions section
        reactions = extract_section(text, ["REACTIONS"])
        self.assertIsNotNone(reactions)
        self.assertIn("This is a reaction", reactions)
        self.assertNotIn("This is an action", reactions)
        
        # Test non-existent section
        nonexistent = extract_section(text, ["LEGENDARY"])
        self.assertIsNone(nonexistent)
        
        # Test with multiple possible section names
        traits_alt = extract_section(text, ["TRAIT", "TRAITS", "Special Abilities"])
        self.assertIsNotNone(traits_alt)
        self.assertIn("This is a trait", traits_alt)

    def test_parse_monster_data_basic(self):
        """Test parsing basic monster information."""
        text = """
        Dragon
        Large Dragon, Chaotic Good
        AC 18
        HP 200
        Speed 40 ft., fly 80 ft.
        
        STR 23
        DEX 16
        CON 21
        INT 19
        WIS 15
        CHA 20
        """
        
        result = parse_monster_data(text)
        
        # Check basic info was parsed correctly
        self.assertEqual(result.get('name'), 'Dragon')
        self.assertEqual(result.get('size'), 'large')
        self.assertEqual(result.get('type'), 'dragon')
        self.assertEqual(result.get('alignment'), 'chaotic good')
        self.assertEqual(result.get('armor_class'), 18)
        self.assertEqual(result.get('hit_points'), 200)
        self.assertEqual(result.get('speed'), '40 ft., fly 80 ft.')
        
        # Check ability scores
        self.assertEqual(result.get('strength'), 23)
        self.assertEqual(result.get('dexterity'), 16)
        self.assertEqual(result.get('constitution'), 21)
        self.assertEqual(result.get('intelligence'), 19)
        self.assertEqual(result.get('wisdom'), 15)
        self.assertEqual(result.get('charisma'), 20)

    def test_parse_monster_data_advanced(self):
        """Test parsing more complex monster information."""
        text = """
        Ancient Red Dragon
        Gargantuan Dragon, Chaotic Evil
        
        AC 22 (natural armor)
        HP 546 (28d20 + 252)
        Speed 40 ft., climb 40 ft., fly 80 ft.
        
        STR 30 (+10)  DEX 10 (+0)  CON 29 (+9)
        INT 18 (+4)   WIS 15 (+2)  CHA 23 (+6)
        
        Saving Throws Dex +7, Con +16, Wis +9, Cha +13
        Skills Perception +16, Stealth +7
        Damage Immunities fire
        Senses blindsight 60 ft., darkvision 120 ft., passive Perception 26
        Languages Common, Draconic
        Challenge 24 (62,000 XP)
        
        TRAITS
        Legendary Resistance (3/Day). If the dragon fails a saving throw, it can choose to succeed instead.
        
        ACTIONS
        Multiattack. The dragon can use its Frightful Presence. It then makes three attacks: one with its bite and two with its claws.
        Bite. Melee Weapon Attack: +17 to hit, reach 15 ft., one target. Hit: 21 (2d10 + 10) piercing damage plus 14 (4d6) fire damage.
        
        REACTIONS
        Tail Attack. When a creature the dragon can see within 10 feet of it attacks it, the dragon makes a tail attack against that creature.
        """
        
        result = parse_monster_data(text)
        
        # Check sections were extracted
        self.assertIn('Legendary Resistance', result.get('special_abilities', ''))
        self.assertIn('Multiattack', result.get('actions', ''))
        self.assertIn('Tail Attack', result.get('reactions', ''))
        
        # Check complex fields
        self.assertEqual(result.get('challenge_rating'), '24')
        self.assertEqual(result.get('xp'), 62000)
        self.assertEqual(result.get('hit_dice'), '28d20 + 252')
        self.assertIn('Perception +16', result.get('skills', ''))
        self.assertIn('darkvision 120 ft.', result.get('senses', ''))
        self.assertIn('Common', result.get('languages', ''))

    def test_parse_monster_data_empty(self):
        """Test parsing with empty text."""
        result = parse_monster_data("")
        self.assertEqual(result, {})
        
        result = parse_monster_data(None)
        self.assertEqual(result, {})

    @patch('app.utils.simple_ocr.pytesseract.image_to_string')
    def test_extract_text_image_processing(self, mock_image_to_string):
        """Test the text extraction with image preprocessing."""
        # Mock the pytesseract response
        mock_image_to_string.return_value = "Test Monster\nMedium Humanoid, Neutral"
        
        # Create a simple test image
        image = Image.new('RGB', (100, 100), color='white')
        draw = ImageDraw.Draw(image)
        draw.text((10, 10), "Test", fill='black')
        
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        image_bytes = img_byte_arr.getvalue()
        
        # Test the function
        result = extract_text_from_image(image_bytes)
        
        # Verify correct text was returned
        self.assertEqual(result, "Test Monster\nMedium Humanoid, Neutral")
        
        # Check that pytesseract was called at least once
        self.assertTrue(mock_image_to_string.called)

    @patch('app.utils.simple_ocr.logger.error')
    @patch('app.utils.simple_ocr.pytesseract.image_to_string')
    def test_extract_text_error_handling(self, mock_image_to_string, mock_logger):
        """Test error handling in extract_text_from_image."""
        # Simulate an error
        mock_image_to_string.side_effect = Exception("Test error")
        
        # Create a simple test image
        image = Image.new('RGB', (100, 100), color='white')
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        image_bytes = img_byte_arr.getvalue()
        
        # Test the function
        result = extract_text_from_image(image_bytes)
        
        # Verify error was logged and None was returned
        self.assertIsNone(result)
        mock_logger.assert_called_once()

    def test_regex_patterns(self):
        """Test the regex patterns used in parsing monster data."""
        test_pairs = [
            # Format: (input_text, {expected_field: expected_value})
            ("AC 15 (natural armor)", {'armor_class': 15}),
            ("Armor Class 17", {'armor_class': 17}),
            ("HP 45", {'hit_points': 45}),
            ("Hit Points 75 (10d8 + 30)", {'hit_points': 75}),
            ("STR 18 (+4)", {'strength': 18}),
            ("DEX 14 (+2)", {'dexterity': 14}),
            ("Skills Perception +5, Stealth +4", {'skills': 'Perception +5, Stealth +4'}),
            ("Senses darkvision 60 ft., passive Perception 15", {'senses': 'darkvision 60 ft., passive Perception 15'}),
            ("Languages Common, Elvish", {'languages': 'Common, Elvish'}),
            ("CR 5 (1,800 XP)", {'challenge_rating': '5', 'xp': 1800}),
            ("Challenge 10", {'challenge_rating': '10'}),
            ("Speed 30 ft., swim 30 ft.", {'speed': '30 ft., swim 30 ft.'})
        ]
        
        for input_text, expected in test_pairs:
            result = parse_monster_data(input_text)
            for key, value in expected.items():
                self.assertEqual(result.get(key), value, 
                                f"Failed on pattern '{input_text}' for field '{key}'")

if __name__ == '__main__':
    unittest.main() 