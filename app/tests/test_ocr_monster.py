import unittest
from pathlib import Path
import json
import os

class TestSphinxOCR(unittest.TestCase):
    def setUp(self):
        # Expected values from the Sphinx of Wonder statblock
        self.expected_data = {
            "name": "Sphinx of Wonder",
            "size": "Tiny",
            "type": "Celestial",
            "alignment": "Lawful Good",
            "armor_class": 13,
            "hit_points": 24,
            "hit_dice": "4d4 + 7",
            "speed": "20ft., Fly 40ft",
            
            # Ability Scores
            "strength": 6,
            "dexterity": 17,
            "constitution": 13,
            "intelligence": 13,
            "wisdom": 11,
            "charisma": 11,
            
            # Saving Throws
            "strength_save": -2,
            "dexterity_save": 3,
            "constitution_save": 1,
            "intelligence_save": 3,
            "wisdom_save": 5,
            "charisma_save": 0,
            
            # Skills and Senses
            "skills": "Arcana +4, Religion +4, Stealth +5",
            "senses": "Darkvision 60 ft., Passive Perception 11",
            "languages": "Common",
            "challenge_rating": "1",
            "xp": 200,
            
            # Special Features
            "special_abilities": "Magic Resistance. The sphinx has Advantage on saving throws against spells and other magical effects.",
            
            # Actions
            "actions": "Rapid Magic Bolt +5, reach 5ft. Hit 3 (1d4 + 3) Slashing damage plus 7 (2d6) Radiant damage.",
            
            # Reactions
            "reactions": "Burst of Ingenuity (2/Day). Trigger: The sphinx or another creature within 20 feet makes an ability check or a saving throw. Response: The sphinx adds 2 to the roll.",
            
            # Additional Fields
            "initiative": 3,
            "damage_vulnerabilities": "",
            "damage_resistances": "",
            "damage_immunities": "",
            "condition_immunities": "",
            "legendary_actions": "",
            "mythic_actions": "",
            "lair_actions": "",
            "description": "A tiny celestial sphinx with an aura of magical wonder."
        }

    def test_ocr_field_extraction(self):
        """Test that OCR correctly extracts all fields from the Sphinx of Wonder image"""
        from app.ocr import process_monster_image  # Import your OCR processing function
        
        # Path to the test image
        test_image_path = Path(__file__).parent / "test_data" / "sphinx_of_wonder.jpg"
        
        # Ensure test image exists
        self.assertTrue(test_image_path.exists(), f"Test image not found at {test_image_path}")
        
        # Process the image
        try:
            result = process_monster_image(test_image_path)
            
            # Test each field
            for field, expected_value in self.expected_data.items():
                with self.subTest(field=field):
                    self.assertIn(field, result, f"Field '{field}' missing from OCR result")
                    actual_value = result[field]
                    
                    # Handle different types of values
                    if isinstance(expected_value, (int, float)):
                        self.assertEqual(float(actual_value), float(expected_value),
                                      f"Mismatch in {field}: expected {expected_value}, got {actual_value}")
                    else:
                        # For strings, do case-insensitive comparison and ignore whitespace
                        self.assertEqual(str(actual_value).lower().strip(),
                                      str(expected_value).lower().strip(),
                                      f"Mismatch in {field}: expected {expected_value}, got {actual_value}")
                        
        except Exception as e:
            self.fail(f"OCR processing failed: {str(e)}")

    def test_saving_throw_formatting(self):
        """Test that saving throws are correctly formatted with + or - signs"""
        from app.ocr import format_saving_throw  # Import your formatting function
        
        test_cases = [
            (-2, "-2"),
            (3, "+3"),
            (0, "+0"),
            (5, "+5"),
            (1, "+1")
        ]
        
        for input_value, expected_output in test_cases:
            with self.subTest(input_value=input_value):
                result = format_saving_throw(input_value)
                self.assertEqual(result, expected_output)

    def test_ability_score_to_modifier(self):
        """Test that ability scores are correctly converted to modifiers"""
        from app.ocr import ability_score_to_modifier  # Import your conversion function
        
        test_cases = [
            (6, -2),   # Strength
            (17, 3),   # Dexterity
            (13, 1),   # Constitution
            (13, 1),   # Intelligence
            (11, 0),   # Wisdom
            (11, 0)    # Charisma
        ]
        
        for score, expected_modifier in test_cases:
            with self.subTest(score=score):
                result = ability_score_to_modifier(score)
                self.assertEqual(result, expected_modifier)

if __name__ == '__main__':
    unittest.main() 