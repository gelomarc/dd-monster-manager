import re
import pytesseract
from PIL import Image
import cv2
import numpy as np
import io
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Tesseract path
# Try to use the path from environment variable first, then fall back to common install locations
TESSERACT_PATH = os.environ.get('TESSERACT_PATH')
if TESSERACT_PATH and os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
else:
    # Check common install locations
    common_locations = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',  # Windows default
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',  # Windows 32-bit
        '/usr/bin/tesseract',  # Linux
        '/usr/local/bin/tesseract',  # macOS
    ]
    
    for location in common_locations:
        if os.path.exists(location):
            pytesseract.pytesseract.tesseract_cmd = location
            logger.info(f"Found Tesseract at: {location}")
            break
    else:
        logger.warning("Tesseract executable not found in common locations. OCR may not work properly.")

def preprocess_image(image_bytes):
    """Preprocess image for better OCR results."""
    try:
        # Convert image bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding to enhance text
        _, threshold = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Denoise image
        denoised = cv2.fastNlMeansDenoising(threshold, None, 10, 7, 21)
        
        return denoised
    except Exception as e:
        logger.error(f"Error preprocessing image: {str(e)}")
        return None

def extract_text_from_image(image_bytes):
    """Extract text from image using OCR."""
    try:
        # Preprocess image for better OCR results
        processed_image = preprocess_image(image_bytes)
        if processed_image is None:
            return None
        
        # Convert numpy array to PIL Image
        pil_image = Image.fromarray(processed_image)
        
        # Extract text using pytesseract
        text = pytesseract.image_to_string(pil_image)
        
        return text
    except Exception as e:
        logger.error(f"Error extracting text from image: {str(e)}")
        return None

def parse_monster_data(text):
    """Parse the OCR text to extract monster attributes."""
    if not text:
        return {}
    
    monster_data = {}
    
    # Extract monster name (usually first line)
    lines = text.split('\n')
    if lines:
        monster_data['name'] = lines[0].strip()
    
    # Extract size, type, and alignment
    size_type_pattern = r"(\w+) (\w+), (\w+(?:\s+\w+)?)"
    size_type_match = re.search(size_type_pattern, text)
    if size_type_match:
        monster_data['size'] = size_type_match.group(1).lower()
        monster_data['type'] = size_type_match.group(2).lower()
        monster_data['alignment'] = size_type_match.group(3).lower()
    
    # Extract Armor Class
    ac_pattern = r"Armor Class (\d+)(?: \((.+)\))?"
    ac_match = re.search(ac_pattern, text)
    if ac_match:
        monster_data['armor_class'] = int(ac_match.group(1))
        if ac_match.group(2):
            monster_data['armor_type'] = ac_match.group(2)
    
    # Extract Hit Points
    hp_pattern = r"Hit Points (\d+)(?: \((.+)\))?"
    hp_match = re.search(hp_pattern, text)
    if hp_match:
        monster_data['hit_points'] = int(hp_match.group(1))
        if hp_match.group(2):
            monster_data['hit_dice'] = hp_match.group(2)
    
    # Extract Speed
    speed_pattern = r"Speed (.+?)(?:\n|$)"
    speed_match = re.search(speed_pattern, text)
    if speed_match:
        monster_data['speed'] = speed_match.group(1).strip()
    
    # Extract ability scores
    ability_pattern = r"(\d+) \(([+-]\d+)\)"
    abilities = re.findall(ability_pattern, text)
    
    if len(abilities) >= 6:
        ability_names = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']
        for i, ability in enumerate(ability_names):
            if i < len(abilities):
                monster_data[ability] = int(abilities[i][0])
    
    # Extract Skills
    skills_pattern = r"Skills (.+?)(?:\n|$)"
    skills_match = re.search(skills_pattern, text)
    if skills_match:
        monster_data['skills'] = skills_match.group(1).strip()
    
    # Extract Senses
    senses_pattern = r"Senses (.+?)(?:\n|$)"
    senses_match = re.search(senses_pattern, text)
    if senses_match:
        monster_data['senses'] = senses_match.group(1).strip()
    
    # Extract Languages
    languages_pattern = r"Languages (.+?)(?:\n|$)"
    languages_match = re.search(languages_pattern, text)
    if languages_match:
        monster_data['languages'] = languages_match.group(1).strip()
    
    # Extract Challenge Rating
    cr_pattern = r"Challenge (\d+(?:\/\d+)?)(?: \((.+) XP\))?"
    cr_match = re.search(cr_pattern, text)
    if cr_match:
        monster_data['challenge_rating'] = cr_match.group(1)
        if cr_match.group(2):
            monster_data['xp'] = int(cr_match.group(2).replace(',', ''))
    
    # Extract Traits/Special Abilities, Actions, and Reactions
    # These are more complex and often span multiple lines
    
    # Extract Traits/Special Abilities
    traits_start = text.find("TRAITS")
    actions_start = text.find("ACTIONS")
    reactions_start = text.find("REACTIONS")
    
    if traits_start >= 0 and actions_start >= 0:
        traits_text = text[traits_start+7:actions_start].strip()
        monster_data['special_abilities'] = traits_text
    
    # Extract Actions
    if actions_start >= 0:
        actions_end = reactions_start if reactions_start >= 0 else len(text)
        actions_text = text[actions_start+8:actions_end].strip()
        monster_data['actions'] = actions_text
    
    # Extract Reactions
    if reactions_start >= 0:
        reactions_text = text[reactions_start+10:].strip()
        monster_data['reactions'] = reactions_text
    
    logger.info(f"Extracted monster data: {monster_data}")
    return monster_data 