from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models.loot import Loot
from app.models.campaign import Campaign
from app.models.encounter import Encounter
from app.forms.loot import LootForm
from app import db

bp = Blueprint('loot', __name__)

@bp.route('/campaigns/<int:campaign_id>/encounters/<int:encounter_id>/loot')
@login_required
def list(campaign_id, encounter_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.user_id != current_user.id:
        flash('You do not have permission to view this campaign.', 'error')
        return redirect(url_for('campaigns.list'))
    
    encounter = Encounter.query.get_or_404(encounter_id)
    loot_items = Loot.query.filter_by(encounter_id=encounter_id).all()
    
    return render_template('loot/list.html',
                         campaign=campaign,
                         encounter=encounter,
                         loot_items=loot_items)

@bp.route('/campaigns/<int:campaign_id>/encounters/<int:encounter_id>/loot/create', methods=['GET', 'POST'])
@login_required
def create(campaign_id, encounter_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.user_id != current_user.id:
        flash('You do not have permission to modify this campaign.', 'error')
        return redirect(url_for('campaigns.list'))
    
    encounter = Encounter.query.get_or_404(encounter_id)
    form = LootForm()
    
    if form.validate_on_submit():
        loot = Loot(
            name=form.name.data,
            description=form.description.data,
            quantity=form.quantity.data,
            value=form.value.data,
            rarity=form.rarity.data,
            attunement=form.attunement.data,
            notes=form.notes.data,
            encounter_id=encounter_id,
            campaign_id=campaign_id
        )
        db.session.add(loot)
        db.session.commit()
        
        flash('Loot item added successfully.', 'success')
        return redirect(url_for('loot.list', campaign_id=campaign_id, encounter_id=encounter_id))
    
    return render_template('loot/form.html',
                         form=form,
                         campaign=campaign,
                         encounter=encounter)

@bp.route('/campaigns/<int:campaign_id>/encounters/<int:encounter_id>/loot/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(campaign_id, encounter_id, id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.user_id != current_user.id:
        flash('You do not have permission to modify this campaign.', 'error')
        return redirect(url_for('campaigns.list'))
    
    encounter = Encounter.query.get_or_404(encounter_id)
    loot = Loot.query.get_or_404(id)
    form = LootForm(obj=loot)
    
    if form.validate_on_submit():
        loot.name = form.name.data
        loot.description = form.description.data
        loot.quantity = form.quantity.data
        loot.value = form.value.data
        loot.rarity = form.rarity.data
        loot.attunement = form.attunement.data
        loot.notes = form.notes.data
        db.session.commit()
        
        flash('Loot item updated successfully.', 'success')
        return redirect(url_for('loot.list', campaign_id=campaign_id, encounter_id=encounter_id))
    
    return render_template('loot/form.html',
                         form=form,
                         campaign=campaign,
                         encounter=encounter,
                         loot=loot)

@bp.route('/campaigns/<int:campaign_id>/encounters/<int:encounter_id>/loot/<int:id>/delete', methods=['POST'])
@login_required
def delete(campaign_id, encounter_id, id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.user_id != current_user.id:
        flash('You do not have permission to modify this campaign.', 'error')
        return redirect(url_for('campaigns.list'))
    
    loot = Loot.query.get_or_404(id)
    db.session.delete(loot)
    db.session.commit()
    
    flash('Loot item deleted successfully.', 'success')
    return redirect(url_for('loot.list', campaign_id=campaign_id, encounter_id=encounter_id)) 