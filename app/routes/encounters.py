from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)
from flask_login import login_required, current_user
from app import db
from app.models.encounter import Encounter
from app.models.campaign import Campaign
from app.models.loot import Loot

bp = Blueprint('encounters', __name__, url_prefix='/campaigns/<int:campaign_id>/encounters')

@bp.route('/')
@login_required
def list(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.user_id != current_user.id:
        flash('You can only view your own campaigns!')
        return redirect(url_for('campaigns.list'))
    
    encounters = Encounter.query.filter_by(campaign_id=campaign_id).all()
    return render_template('encounters/list.html', campaign=campaign, encounters=encounters)

@bp.route('/<int:id>')
@login_required
def view(campaign_id, id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.user_id != current_user.id:
        flash('You can only view encounters in your own campaigns!')
        return redirect(url_for('campaigns.list'))
    
    encounter = Encounter.query.get_or_404(id)
    if encounter.campaign_id != campaign_id:
        flash('Encounter does not belong to this campaign!')
        return redirect(url_for('encounters.list', campaign_id=campaign_id))
    
    loot_items = Loot.query.filter_by(encounter_id=id).all()
    
    return render_template('encounters/view.html',
                         campaign=campaign,
                         encounter=encounter,
                         loot_items=loot_items)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.user_id != current_user.id:
        flash('You can only add encounters to your own campaigns!')
        return redirect(url_for('campaigns.list'))
    
    if request.method == 'POST':
        name = request.form['name']
        difficulty = request.form['difficulty']
        description = request.form['description']
        monsters = request.form['monsters']
        error = None

        if not name:
            error = 'Name is required.'

        if error is not None:
            flash(error)
        else:
            encounter = Encounter(
                name=name,
                difficulty=difficulty,
                description=description,
                monsters=monsters,
                campaign_id=campaign_id
            )
            db.session.add(encounter)
            db.session.commit()
            flash('Encounter added successfully!')
            return redirect(url_for('encounters.list', campaign_id=campaign_id))

    return render_template('encounters/create.html', campaign=campaign)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(campaign_id, id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.user_id != current_user.id:
        flash('You can only delete encounters from your own campaigns!')
        return redirect(url_for('campaigns.list'))
    
    encounter = Encounter.query.get_or_404(id)
    if encounter.campaign_id != campaign_id:
        flash('Encounter does not belong to this campaign!')
        return redirect(url_for('encounters.list', campaign_id=campaign_id))
        
    db.session.delete(encounter)
    db.session.commit()
    flash('Encounter deleted successfully!')
    return redirect(url_for('encounters.list', campaign_id=campaign_id)) 