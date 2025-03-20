import math
from typing import Dict, Union, Any
import pytesseract
from PIL import Image
import re
import json

def ability_score_to_modifier(score: int) -> int:
    """Convert an ability score to its modifier."""
    return math.floor((score - 10) / 2)

def format_saving_throw(value: int) -> str:
    """Format a saving throw value with proper + or - sign."""
    return f"+{value}" if value >= 0 else str(value)

def extract_number(text: str) -> Union[int, None]:
    """Extract the first number from a string."""
    match = re.search(r'[-+]?\d+', text)
    return int(match.group()) if match else None

def process_monster_image(image_path: str) -> Dict[str, Any]:
    """Process an image of a monster statblock and extract all relevant information."""
    try:
        # Open and process the image
        image = Image.open(image_path)
        
        # Extract text from image
        text = pytesseract.image_to_string(image)
        print("OCR Output:", text)  # Debug output
        
        # Initialize the result dictionary with default values
        result = {
            "name": "",
            "size": "",
            "type": "",
            "alignment": "",
            "armor_class": 0,
            "hit_points": 0,
            "hit_dice": "",
            "speed": "",
            "strength": 10,
            "dexterity": 10,
            "constitution": 10,
            "intelligence": 10,
            "wisdom": 10,
            "charisma": 10,
            "strength_save": None,
            "dexterity_save": None,
            "constitution_save": None,
            "intelligence_save": None,
            "wisdom_save": None,
            "charisma_save": None,
            "skills": "",
            "senses": "",
            "languages": "",
            "challenge_rating": "",
            "xp": 0,
            "special_abilities": "",
            "actions": "",
            "reactions": "",
            "legendary_actions": "",
            "mythic_actions": "",
            "lair_actions": "",
            "description": "",
        }
        
        # Split text into lines and clean them
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Extract ability scores and saving throws
        ability_scores = {
            'Str': ('strength', 'strength_save'),
            'Dex': ('dexterity', 'dexterity_save'),
            'Con': ('constitution', 'constitution_save'),
            'Int': ('intelligence', 'intelligence_save'),
            'Wis': ('wisdom', 'wisdom_save'),
            'Cha': ('charisma', 'charisma_save')
        }
        
        # Process each line for ability scores
        for line in lines:
            for abbr, (score_field, save_field) in ability_scores.items():
                # Pattern to match both score and modifier: "Str 6 (-2)"
                score_pattern = rf'{abbr}\s+(\d+)\s*[+-]\d+'
                score_match = re.search(score_pattern, line)
                if score_match:
                    result[score_field] = int(score_match.group(1))
                
                # Pattern to match saving throw modifier
                save_pattern = rf'{abbr}\s+([-+]\d+)'
                save_match = re.search(save_pattern, line)
                if save_match:
                    modifier = save_match.group(1)
                    result[save_field] = int(modifier)
        
        # Extract name (first line)
        if lines:
            result["name"] = lines[0]
        
        # Extract size, type, and alignment from second line
        if len(lines) > 1:
            type_line = lines[1]
            size_match = re.match(r'(Tiny|Small|Medium|Large|Huge|Gargantuan)', type_line, re.I)
            if size_match:
                result["size"] = size_match.group(1)
            
            type_match = re.search(r'(celestial|dragon|fiend|elemental|undead|humanoid|construct|beast|plant|monstrosity|giant|aberration|ooze|fey)', type_line, re.I)
            if type_match:
                result["type"] = type_match.group(1)
            
            alignment_match = re.search(r'(lawful|neutral|chaotic)\s+(good|neutral|evil)|unaligned', type_line, re.I)
            if alignment_match:
                result["alignment"] = alignment_match.group(0)
        
        # Extract other fields using the full text
        full_text = ' '.join(lines)
        
        # Extract armor class
        ac_match = re.search(r'AC\s*(\d+)', full_text)
        if ac_match:
            result["armor_class"] = int(ac_match.group(1))
        
        # Extract hit points
        hp_match = re.search(r'HP\s*(\d+)\s*\(([^)]+)\)', full_text)
        if hp_match:
            result["hit_points"] = int(hp_match.group(1))
            result["hit_dice"] = hp_match.group(2).strip()
        
        # Extract speed
        speed_match = re.search(r'Speed\s+([^A-Z]+)', full_text)
        if speed_match:
            result["speed"] = speed_match.group(1).strip()
        
        # Extract skills
        skills_match = re.search(r'Skills\s+([^A-Z\n]+)', full_text)
        if skills_match:
            result["skills"] = skills_match.group(1).strip()
        
        # Extract senses
        senses_match = re.search(r'Senses\s+([^A-Z\n]+)', full_text)
        if senses_match:
            result["senses"] = senses_match.group(1).strip()
        
        # Extract languages
        languages_match = re.search(r'Languages\s+([^A-Z\n]+)', full_text)
        if languages_match:
            result["languages"] = languages_match.group(1).strip()
        
        # Extract challenge rating and XP
        cr_match = re.search(r'CR\s*(\d+(?:/\d+)?)\s*\((\d+)\s*XP\)', full_text)
        if cr_match:
            result["challenge_rating"] = cr_match.group(1)
            result["xp"] = int(cr_match.group(2))
        
        # Extract special abilities
        traits_match = re.search(r'TRAITS\s*(.*?)\s*(?:ACTIONS|$)', full_text, re.S)
        if traits_match:
            result["special_abilities"] = traits_match.group(1).strip()
        
        # Extract actions
        actions_match = re.search(r'ACTIONS\s*(.*?)\s*(?:REACTIONS|LEGENDARY ACTIONS|$)', full_text, re.S)
        if actions_match:
            result["actions"] = actions_match.group(1).strip()
        
        # Extract reactions
        reactions_match = re.search(r'REACTIONS\s*(.*?)\s*(?:LEGENDARY ACTIONS|$)', full_text, re.S)
        if reactions_match:
            result["reactions"] = reactions_match.group(1).strip()
        
        print("Processed Result:", json.dumps(result, indent=2))  # Debug output
        return result
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")  # Debug output
        raise Exception(f"Error processing monster image: {str(e)}")

def validate_monster_data(data: Dict[str, Any]) -> bool:
    """Validate that all required fields are present and properly formatted."""
    required_fields = [
        "name",
        "size",
        "type",
        "alignment",
        "armor_class",
        "hit_points",
        "speed"
    ]
    
    for field in required_fields:
        if not data.get(field):
            return False
    
    return True 