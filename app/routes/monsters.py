from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, jsonify, Response, send_file
)
from flask_login import login_required, current_user
from app import db
from app.models.monster import Monster
from app.models.encounter import Encounter
from app.models.campaign import Campaign
import pdfkit
from pdfkit.configuration import Configuration
import io
import os
from werkzeug.utils import secure_filename
import tempfile
from werkzeug.exceptions import NotFound
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Try to import the full OCR implementation first
    from app.utils.ocr import extract_text_from_image, parse_monster_data
    logger.info("Using full OCR implementation with OpenCV")
except ImportError:
    # Fall back to simplified implementation if there are import errors
    from app.utils.simple_ocr import extract_text_from_image, parse_monster_data
    logger.info("Using simplified OCR implementation without OpenCV")

bp = Blueprint('monsters', __name__, url_prefix='/campaigns/<int:campaign_id>')

@bp.route('/monsters')
@login_required
def list(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.user_id != current_user.id:
        flash('You can only view your own campaigns!')
        return redirect(url_for('campaigns.list'))
    
    monsters = Monster.query.filter_by(campaign_id=campaign_id, encounter_id=None).all()
    return render_template('monsters/list.html', campaign=campaign, monsters=monsters)

@bp.route('/encounters/<int:encounter_id>/monsters')
@login_required
def encounter_monsters(campaign_id, encounter_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.user_id != current_user.id:
        flash('You can only view monsters in your own campaigns!')
        return redirect(url_for('campaigns.list'))
    
    encounter = Encounter.query.get_or_404(encounter_id)
    if encounter.campaign_id != campaign_id:
        flash('Encounter does not belong to this campaign!')
        return redirect(url_for('encounters.list', campaign_id=campaign_id))
    
    monsters = Monster.query.filter_by(encounter_id=encounter_id).all()
    return render_template('monsters/encounter_monsters.html', campaign=campaign, encounter=encounter, monsters=monsters)

@bp.route('/monsters/create', defaults={'encounter_id': None})
@bp.route('/encounters/<int:encounter_id>/monsters/create')
@login_required
def create(campaign_id, encounter_id=None):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.user_id != current_user.id:
        flash('You can only add monsters to your own campaigns!')
        return redirect(url_for('campaigns.list'))
    
    encounter = None
    if encounter_id:
        encounter = Encounter.query.get_or_404(encounter_id)
        if encounter.campaign_id != campaign_id:
            flash('Encounter does not belong to this campaign!')
            return redirect(url_for('encounters.list', campaign_id=campaign_id))
    
    if request.method == 'POST':
        # Extract form data for monster
        name = request.form['name']
        size = request.form['size']
        type = request.form['type']
        alignment = request.form['alignment']
        
        # Basic stats
        armor_class = request.form.get('armor_class', 0, type=int)
        armor_type = request.form['armor_type']
        hit_points = request.form.get('hit_points', 0, type=int)
        hit_dice = request.form['hit_dice']
        speed = request.form['speed']
        
        # Ability scores
        strength = request.form.get('strength', 10, type=int)
        dexterity = request.form.get('dexterity', 10, type=int)
        constitution = request.form.get('constitution', 10, type=int)
        intelligence = request.form.get('intelligence', 10, type=int)
        wisdom = request.form.get('wisdom', 10, type=int)
        charisma = request.form.get('charisma', 10, type=int)
        
        # Saving throws
        strength_save = request.form.get('strength_save', '')
        dexterity_save = request.form.get('dexterity_save', '')
        constitution_save = request.form.get('constitution_save', '')
        intelligence_save = request.form.get('intelligence_save', '')
        wisdom_save = request.form.get('wisdom_save', '')
        charisma_save = request.form.get('charisma_save', '')
        
        # Skills - handle multiple checkbox values
        skills = request.form.getlist('skills')
        skills_json = json.dumps(skills) if skills else ''
        
        # Resistances and immunities
        damage_vulnerabilities = request.form.get('damage_vulnerabilities', '')
        damage_resistances = request.form.get('damage_resistances', '')
        damage_immunities = request.form.get('damage_immunities', '')
        condition_immunities = request.form.get('condition_immunities', '')
        
        # Senses and languages
        senses = request.form.get('senses', '')
        languages = request.form.get('languages', '')
        
        # Challenge rating
        challenge_rating = request.form.get('challenge_rating', '')
        xp = request.form.get('xp', 0, type=int)
        
        # Special abilities and actions
        special_abilities = request.form.get('special_abilities', '')
        actions = request.form.get('actions', '')
        bonus_actions = request.form.get('bonus_actions', '')
        reactions = request.form.get('reactions', '')
        legendary_actions = request.form.get('legendary_actions', '')
        legendary_resistance = request.form.get('legendary_resistance', 0, type=int)
        lair_actions = request.form.get('lair_actions', '')
        
        # Description
        description = request.form.get('description', '')
        
        # Image URL
        image_url = request.form.get('image_url', '')
        
        error = None
        if not name:
            error = 'Name is required.'
            
        if error is not None:
            flash(error)
        else:
            monster = Monster(
                name=name,
                size=size,
                type=type,
                alignment=alignment,
                armor_class=armor_class,
                armor_type=armor_type,
                hit_points=hit_points,
                hit_dice=hit_dice,
                speed=speed,
                strength=strength,
                dexterity=dexterity,
                constitution=constitution,
                intelligence=intelligence,
                wisdom=wisdom,
                charisma=charisma,
                strength_save=strength_save,
                dexterity_save=dexterity_save,
                constitution_save=constitution_save,
                intelligence_save=intelligence_save,
                wisdom_save=wisdom_save,
                charisma_save=charisma_save,
                skills=skills_json,
                damage_vulnerabilities=damage_vulnerabilities,
                damage_resistances=damage_resistances,
                damage_immunities=damage_immunities,
                condition_immunities=condition_immunities,
                senses=senses,
                languages=languages,
                challenge_rating=challenge_rating,
                xp=xp,
                special_abilities=special_abilities,
                actions=actions,
                bonus_actions=bonus_actions,
                reactions=reactions,
                legendary_actions=legendary_actions,
                legendary_resistance=legendary_resistance,
                lair_actions=lair_actions,
                description=description,
                image_url=image_url,
                campaign_id=campaign_id,
                encounter_id=encounter_id
            )
            db.session.add(monster)
            db.session.commit()
            
            flash('Monster added successfully!')
            if encounter_id:
                return redirect(url_for('monsters.encounter_monsters', campaign_id=campaign_id, encounter_id=encounter_id))
            else:
                return redirect(url_for('monsters.list', campaign_id=campaign_id))
    
    return render_template('monsters/create.html', campaign=campaign, encounter=encounter)

@bp.route('/monsters/<int:id>/view')
@login_required
def view(campaign_id, id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.user_id != current_user.id:
        flash('You can only view monsters in your own campaigns!')
        return redirect(url_for('campaigns.list'))
    
    monster = Monster.query.get_or_404(id)
    if monster.campaign_id != campaign_id:
        flash('Monster does not belong to this campaign!')
        return redirect(url_for('monsters.list', campaign_id=campaign_id))
    
    return render_template('monsters/view.html', campaign=campaign, monster=monster)

@bp.route('/monsters/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def edit(campaign_id, id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.user_id != current_user.id:
        flash('You can only edit monsters in your own campaigns!')
        return redirect(url_for('campaigns.list'))
    
    monster = Monster.query.get_or_404(id)
    if monster.campaign_id != campaign_id:
        flash('Monster does not belong to this campaign!')
        return redirect(url_for('monsters.list', campaign_id=campaign_id))
    
    if request.method == 'POST':
        # Extract and update monster data (same as create route)
        monster.name = request.form['name']
        monster.size = request.form['size']
        monster.type = request.form['type']
        monster.alignment = request.form['alignment']
        
        monster.armor_class = request.form.get('armor_class', 0, type=int)
        monster.armor_type = request.form['armor_type']
        monster.hit_points = request.form.get('hit_points', 0, type=int)
        monster.hit_dice = request.form['hit_dice']
        monster.speed = request.form['speed']
        
        monster.strength = request.form.get('strength', 10, type=int)
        monster.dexterity = request.form.get('dexterity', 10, type=int)
        monster.constitution = request.form.get('constitution', 10, type=int)
        monster.intelligence = request.form.get('intelligence', 10, type=int)
        monster.wisdom = request.form.get('wisdom', 10, type=int)
        monster.charisma = request.form.get('charisma', 10, type=int)
        
        monster.strength_save = request.form.get('strength_save', '')
        monster.dexterity_save = request.form.get('dexterity_save', '')
        monster.constitution_save = request.form.get('constitution_save', '')
        monster.intelligence_save = request.form.get('intelligence_save', '')
        monster.wisdom_save = request.form.get('wisdom_save', '')
        monster.charisma_save = request.form.get('charisma_save', '')
        
        monster.skills = request.form.get('skills', '')
        
        monster.damage_vulnerabilities = request.form.get('damage_vulnerabilities', '')
        monster.damage_resistances = request.form.get('damage_resistances', '')
        monster.damage_immunities = request.form.get('damage_immunities', '')
        monster.condition_immunities = request.form.get('condition_immunities', '')
        
        monster.senses = request.form.get('senses', '')
        monster.languages = request.form.get('languages', '')
        
        monster.challenge_rating = request.form.get('challenge_rating', '')
        monster.xp = request.form.get('xp', 0, type=int)
        
        monster.special_abilities = request.form.get('special_abilities', '')
        monster.actions = request.form.get('actions', '')
        monster.bonus_actions = request.form.get('bonus_actions', '')
        monster.reactions = request.form.get('reactions', '')
        monster.legendary_actions = request.form.get('legendary_actions', '')
        monster.legendary_resistance = request.form.get('legendary_resistance', 0, type=int)
        monster.lair_actions = request.form.get('lair_actions', '')
        
        monster.description = request.form.get('description', '')
        monster.image_url = request.form.get('image_url', '')
        
        error = None
        if not monster.name:
            error = 'Name is required.'
            
        if error is not None:
            flash(error)
        else:
            db.session.commit()
            flash('Monster updated successfully!')
            
            if monster.encounter_id:
                return redirect(url_for('monsters.encounter_monsters', 
                                campaign_id=campaign_id, 
                                encounter_id=monster.encounter_id))
            else:
                return redirect(url_for('monsters.list', campaign_id=campaign_id))
    
    encounter = None
    if monster.encounter_id:
        encounter = Encounter.query.get(monster.encounter_id)
    
    return render_template('monsters/edit.html', campaign=campaign, monster=monster, encounter=encounter)

@bp.route('/monsters/<int:id>/delete', methods=('POST',))
@login_required
def delete(campaign_id, id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.user_id != current_user.id:
        flash('You can only delete monsters in your own campaigns!')
        return redirect(url_for('campaigns.list'))
    
    monster = Monster.query.get_or_404(id)
    if monster.campaign_id != campaign_id:
        flash('Monster does not belong to this campaign!')
        return redirect(url_for('monsters.list', campaign_id=campaign_id))
    
    encounter_id = monster.encounter_id
    
    db.session.delete(monster)
    db.session.commit()
    
    flash('Monster deleted successfully!')
    
    if encounter_id:
        return redirect(url_for('monsters.encounter_monsters', campaign_id=campaign_id, encounter_id=encounter_id))
    else:
        return redirect(url_for('monsters.list', campaign_id=campaign_id))

@bp.route('/monsters/<int:id>/export-pdf')
@login_required
def export_pdf(campaign_id, id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.user_id != current_user.id:
        flash('You can only export monsters from your own campaigns!')
        return redirect(url_for('campaigns.list'))
    
    monster = Monster.query.get_or_404(id)
    if monster.campaign_id != campaign_id:
        flash('Monster does not belong to this campaign!')
        return redirect(url_for('monsters.list', campaign_id=campaign_id))
    
    try:
        # Render the HTML template with the monster data
        rendered_html = render_template('monsters/pdf_template.html', campaign=campaign, monster=monster)
        
        # Create a temporary file to store the PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp:
            temp_filename = temp.name
        
        # Configuration for wkhtmltopdf
        options = {
            'page-size': 'Letter',
            'margin-top': '0.5in',
            'margin-right': '0.5in',
            'margin-bottom': '0.5in',
            'margin-left': '0.5in',
            'encoding': 'UTF-8',
            'no-outline': None,
            'enable-local-file-access': None
        }
        
        # Configure wkhtmltopdf path
        config = Configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')  # Adjust path if needed
        
        # Convert HTML to PDF
        pdfkit.from_string(rendered_html, temp_filename, options=options, configuration=config)
        
        # Send the file to the user
        response = send_file(
            temp_filename,
            as_attachment=True,
            download_name=f"{monster.name}_statblock.pdf",
            mimetype='application/pdf'
        )
        
        # Delete the temporary file after sending (wrap in a function to ensure deletion)
        @response.call_on_close
        def cleanup():
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
        
        return response
    except Exception as e:
        flash(f'Error generating PDF: {str(e)}')
        return redirect(url_for('monsters.view', campaign_id=campaign_id, id=id))

@bp.route('/monsters/<int:id>/pdf')
@login_required
def generate_pdf(id):
    monster = Monster.query.get_or_404(id)
    
    # Render the HTML template with the monster data
    rendered_html = render_template('monsters/pdf_template.html', monster=monster)
    
    # Create a temporary file to store the PDF
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp:
        temp_filename = temp.name
    
    # Configuration for wkhtmltopdf
    options = {
        'page-size': 'Letter',
        'margin-top': '0.5in',
        'margin-right': '0.5in',
        'margin-bottom': '0.5in',
        'margin-left': '0.5in',
        'encoding': 'UTF-8',
        'no-outline': None,
        'enable-local-file-access': None
    }
    
    # Configure wkhtmltopdf path
    config = Configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')  # Adjust path if needed
    
    # Convert HTML to PDF
    pdfkit.from_string(rendered_html, temp_filename, options=options, configuration=config)
    
    # Send the file to the user
    response = send_file(
        temp_filename,
        as_attachment=True,
        download_name=f"{monster.name}_statblock.pdf",
        mimetype='application/pdf'
    )
    
    # Delete the temporary file after sending (wrap in a function to ensure deletion)
    @response.call_on_close
    def cleanup():
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
    
    return response

@bp.route('/monsters/scan-image', methods=['POST'])
@login_required
def scan_image(campaign_id):
    """
    Process uploaded monster statblock image with OCR and extract data.
    Returns JSON with extracted monster data.
    """
    # Verify campaign exists and belongs to user
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.user_id != current_user.id:
        return jsonify({
            'success': False,
            'message': 'You can only add monsters to your own campaigns!'
        }), 403
    
    # Check if image was uploaded
    if 'statblock_image' not in request.files:
        return jsonify({
            'success': False,
            'message': 'No image file uploaded'
        }), 400
    
    image_file = request.files['statblock_image']
    
    # Check if file is empty
    if image_file.filename == '':
        return jsonify({
            'success': False,
            'message': 'No image file selected'
        }), 400
    
    # Process the image
    try:
        # Read image bytes
        image_bytes = image_file.read()
        
        # Save the original image for debugging
        debug_dir = os.path.join('app', 'static', 'debug')
        os.makedirs(debug_dir, exist_ok=True)
        original_path = os.path.join(debug_dir, 'original_upload.jpg')
        with open(original_path, 'wb') as f:
            f.write(image_bytes)
        logger.info(f"Saved original image to {original_path}")
        
        # Extract text from image
        extracted_text = extract_text_from_image(image_bytes)
        
        if not extracted_text:
            return jsonify({
                'success': False,
                'message': 'Could not extract text from image. Please try a clearer image.',
                'debug_url': url_for('static', filename='debug/debug_ocr_image.png')
            }), 400
        
        # Parse text to extract monster data
        monster_data = parse_monster_data(extracted_text)
        
        if not monster_data:
            return jsonify({
                'success': False,
                'message': 'Could not parse monster data from extracted text.',
                'raw_text': extracted_text,
                'debug_url': url_for('static', filename='debug/debug_ocr_image.png')
            }), 400
        
        # Log the extracted data for debugging
        logger.info(f"Extracted monster data: {monster_data}")
        
        # Return the extracted data
        return jsonify({
            'success': True,
            'message': 'Monster data extracted successfully!',
            'monster_data': monster_data,
            'raw_text': extracted_text,
            'debug_url': url_for('static', filename='debug/debug_ocr_image.png')
        })
        
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error processing image: {str(e)}',
            'debug_url': url_for('static', filename='debug/debug_ocr_image.png')
        }), 500

@bp.route('/ocr-debug')
@login_required
def ocr_debug():
    """Debug view for OCR troubleshooting"""
    debug_images = {}
    debug_dir = os.path.join('app', 'static', 'debug')
    
    if os.path.exists(os.path.join(debug_dir, 'original_upload.jpg')):
        debug_images['original'] = url_for('static', filename='debug/original_upload.jpg')
    
    if os.path.exists(os.path.join(debug_dir, 'debug_ocr_image.png')):
        debug_images['processed'] = url_for('static', filename='debug/debug_ocr_image.png')
    
    # Try to read the OCR logs
    log_content = ""
    try:
        with open('app.log', 'r') as f:
            log_lines = f.readlines()
            # Get last 50 lines
            log_content = ''.join(log_lines[-50:])
    except:
        log_content = "Could not read log file"
    
    return render_template(
        'monsters/ocr_debug.html', 
        debug_images=debug_images,
        log_content=log_content
    ) 