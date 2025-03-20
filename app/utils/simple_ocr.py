import re
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import io
import logging
import os
import base64

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

def extract_text_from_image(image_bytes):
    """Extract text from image using OCR with enhanced preprocessing for D&D statblocks."""
    try:
        # Open image from bytes
        image = Image.open(io.BytesIO(image_bytes))
        
        # Log original image size
        logger.info(f"Original image size: {image.size}")
        
        # Resize image for better OCR processing if it's too small
        if image.width < 800:
            ratio = 800 / image.width
            new_size = (800, int(image.height * ratio))
            image = image.resize(new_size, Image.LANCZOS)
            logger.info(f"Resized image to: {new_size}")
        
        # Create multiple versions with different preprocessing and combine results
        results = []
        
        # Version 1: Convert to grayscale
        gray_image = image.convert('L')
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(gray_image)
        high_contrast = enhancer.enhance(2.0)
        # Apply sharpening
        sharpened = high_contrast.filter(ImageFilter.SHARPEN)
        
        # Extract text (use --psm 6 for block of text)
        text1 = pytesseract.image_to_string(
            sharpened, 
            config='--psm 6 -c preserve_interword_spaces=1'
        )
        results.append(text1)
        logger.info(f"Processed version 1 text length: {len(text1)}")
        
        # Version 2: Threshold to black and white with high contrast
        threshold_image = gray_image.point(lambda p: 255 if p > 150 else 0)
        text2 = pytesseract.image_to_string(
            threshold_image,
            config='--psm 6 -c preserve_interword_spaces=1'
        )
        results.append(text2)
        logger.info(f"Processed version 2 text length: {len(text2)}")
        
        # Version 3: Try to better handle colored backgrounds
        # Apply a filter to reduce background colors
        filtered = image.filter(ImageFilter.EDGE_ENHANCE)
        # Convert to grayscale
        filtered_gray = filtered.convert('L')
        # Threshold
        filtered_thresh = filtered_gray.point(lambda p: 255 if p > 120 else 0)
        text3 = pytesseract.image_to_string(
            filtered_thresh,
            config='--psm 6 -c preserve_interword_spaces=1'
        )
        results.append(text3)
        logger.info(f"Processed version 3 text length: {len(text3)}")
        
        # Choose the best result (the longest text content usually has the most information)
        best_text = max(results, key=len)
        
        # Debug log
        logger.info(f"Best text extraction length: {len(best_text)}")
        if len(best_text) < 50:  # If text is very short, log a snippet
            logger.warning(f"Extracted text is very short: {best_text[:50]}")
            
            # Save debug image to app/static/debug/ folder
            debug_dir = os.path.join('app', 'static', 'debug')
            os.makedirs(debug_dir, exist_ok=True)
            
            filtered_thresh.save(os.path.join(debug_dir, 'debug_ocr_image.png'))
            logger.info(f"Saved debug image to {os.path.join(debug_dir, 'debug_ocr_image.png')}")
        
        return best_text
    except Exception as e:
        logger.error(f"Error extracting text from image: {str(e)}")
        return None

def parse_monster_data(text):
    """Parse the OCR text to extract monster attributes."""
    if not text:
        return {}
    
    # Log the entire OCR text for debugging
    logger.info(f"OCR Text to parse:\n{text}")
    
    monster_data = {}
    
    # Extract monster name (usually first line)
    lines = text.split('\n')
    if lines:
        monster_data['name'] = lines[0].strip()
    
    # Extract size, type, and alignment
    # More flexible pattern to match various OCR outputs
    size_type_pattern = r"(?:^|\n)(?:Size:?\s+)?([A-Za-z]+)\s+([A-Za-z]+),\s+([A-Za-z\s]+)"
    size_type_match = re.search(size_type_pattern, text)
    if size_type_match:
        monster_data['size'] = size_type_match.group(1).lower()
        monster_data['type'] = size_type_match.group(2).lower()
        monster_data['alignment'] = size_type_match.group(3).lower()
    
    # Extract Armor Class with more flexible pattern
    ac_pattern = r"(?:AC|Armor\s+Class):?\s*(\d+)"
    ac_match = re.search(ac_pattern, text)
    if ac_match:
        monster_data['armor_class'] = int(ac_match.group(1))
    
    # Extract Hit Points with more flexible pattern
    hp_pattern = r"(?:HP|Hit\s+Points):?\s*(\d+)"
    hp_match = re.search(hp_pattern, text)
    if hp_match:
        monster_data['hit_points'] = int(hp_match.group(1))
    
    # Extract Hit Dice
    hit_dice_pattern = r"\(([0-9d+\s]+)\)"
    hit_dice_match = re.search(hit_dice_pattern, text)
    if hit_dice_match and 'd' in hit_dice_match.group(1):
        monster_data['hit_dice'] = hit_dice_match.group(1)
    
    # Extract Speed
    speed_pattern = r"(?:Speed):?\s+([^.]+?)(?:\n|$)"
    speed_match = re.search(speed_pattern, text)
    if speed_match:
        monster_data['speed'] = speed_match.group(1).strip()
    
    # Extract ability scores - more robust patterns
    str_pattern = r"(?:STR|Str|Strength):?\s+(\d+)"
    dex_pattern = r"(?:DEX|Dex|Dexterity):?\s+(\d+)"
    con_pattern = r"(?:CON|Con|Constitution):?\s+(\d+)"
    int_pattern = r"(?:INT|Int|Intelligence):?\s+(\d+)"
    wis_pattern = r"(?:WIS|Wis|Wisdom):?\s+(\d+)"
    cha_pattern = r"(?:CHA|Cha|Charisma):?\s+(\d+)"
    
    str_match = re.search(str_pattern, text)
    if str_match:
        monster_data['strength'] = int(str_match.group(1))
    
    dex_match = re.search(dex_pattern, text)
    if dex_match:
        monster_data['dexterity'] = int(dex_match.group(1))
    
    con_match = re.search(con_pattern, text)
    if con_match:
        monster_data['constitution'] = int(con_match.group(1))
    
    int_match = re.search(int_pattern, text)
    if int_match:
        monster_data['intelligence'] = int(int_match.group(1))
    
    wis_match = re.search(wis_pattern, text)
    if wis_match:
        monster_data['wisdom'] = int(wis_match.group(1))
    
    cha_match = re.search(cha_pattern, text)
    if cha_match:
        monster_data['charisma'] = int(cha_match.group(1))
    
    # Extract Skills
    skills_pattern = r"(?:Skills):?\s+([^.]+?)(?:\n|$)"
    skills_match = re.search(skills_pattern, text)
    if skills_match:
        monster_data['skills'] = skills_match.group(1).strip()
    
    # Extract Senses
    senses_pattern = r"(?:Senses):?\s+([^.]+?)(?:\n|$)"
    senses_match = re.search(senses_pattern, text)
    if senses_match:
        monster_data['senses'] = senses_match.group(1).strip()
    
    # Extract Languages
    languages_pattern = r"(?:Languages):?\s+([^.]+?)(?:\n|$)"
    languages_match = re.search(languages_pattern, text)
    if languages_match:
        monster_data['languages'] = languages_match.group(1).strip()
    
    # Extract Challenge Rating - more flexible pattern
    cr_pattern = r"(?:CR|Challenge):?\s*(\d+(?:\/\d+)?)"
    cr_match = re.search(cr_pattern, text)
    if cr_match:
        monster_data['challenge_rating'] = cr_match.group(1)
    
    # Extract XP
    xp_pattern = r"(?:XP):?\s*(\d+,?\d*)"
    xp_match = re.search(xp_pattern, text)
    if xp_match:
        monster_data['xp'] = int(xp_match.group(1).replace(',', ''))
    
    # Extract Traits/Special Abilities, Actions, and Reactions
    # More flexible section detection
    traits_section = extract_section(text, ["TRAITS", "TRAIT", "Special Abilities", "Special"])
    if traits_section:
        monster_data['special_abilities'] = traits_section
    
    actions_section = extract_section(text, ["ACTIONS", "ACTION"])
    if actions_section:
        monster_data['actions'] = actions_section
    
    reactions_section = extract_section(text, ["REACTIONS", "REACTION"])
    if reactions_section:
        monster_data['reactions'] = reactions_section
    
    logger.info(f"Extracted monster data: {monster_data}")
    return monster_data

def extract_section(text, section_names):
    """Extract a section from the OCR text based on multiple possible section names."""
    text = text.replace('\r', '\n')
    
    # Try to find the section start
    start_index = -1
    for name in section_names:
        idx = text.find(name)
        if idx != -1:
            start_index = idx + len(name)
            break
    
    if start_index == -1:
        return None
    
    # Find the next section marker
    section_markers = ["TRAITS", "ACTIONS", "REACTIONS", "LEGENDARY", "LAIR", "MYTHIC"]
    end_index = len(text)
    
    for marker in section_markers:
        if marker in section_names:  # Skip the current section name
            continue
        idx = text.find(marker, start_index)
        if idx != -1 and idx < end_index:
            end_index = idx
    
    # Extract the section content
    section_text = text[start_index:end_index].strip()
    
    # Clean up the section
    lines = section_text.split('\n')
    clean_lines = []
    for line in lines:
        if line.strip():  # Skip empty lines
            clean_lines.append(line.strip())
    
    return '\n'.join(clean_lines) 