from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user
from app import db
from app.models.npc import NPC
from app.models.campaign import Campaign
from app.forms.npc import NPCForm

bp = Blueprint('npcs', __name__, url_prefix='/campaigns/<int:campaign_id>/npcs')

@bp.route('/')
@login_required
def list(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.user_id != current_user.id:
        flash('You can only view NPCs in your own campaigns!', 'error')
        return redirect(url_for('campaigns.list'))
    
    npcs = NPC.query.filter_by(campaign_id=campaign_id).order_by(NPC.name).all()
    return render_template('npcs/list.html', campaign=campaign, npcs=npcs)

@bp.route('/<int:id>')
@login_required
def view(campaign_id, id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.user_id != current_user.id:
        flash('You can only view NPCs in your own campaigns!', 'error')
        return redirect(url_for('campaigns.list'))
    
    npc = NPC.query.get_or_404(id)
    if npc.campaign_id != campaign_id:
        flash('NPC does not belong to this campaign!', 'error')
        return redirect(url_for('npcs.list', campaign_id=campaign_id))
    
    return render_template('npcs/view.html', campaign=campaign, npc=npc)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.user_id != current_user.id:
        flash('You can only add NPCs to your own campaigns!', 'error')
        return redirect(url_for('campaigns.list'))
    
    form = NPCForm()
    if form.validate_on_submit():
        npc = NPC(
            name=form.name.data,
            role=form.role.data,
            attitude=form.attitude.data,
            places_to_find=form.places_to_find.data,
            description=form.description.data,
            equipment=form.equipment.data,
            campaign_id=campaign_id
        )
        db.session.add(npc)
        db.session.commit()
        flash('NPC added successfully!', 'success')
        return redirect(url_for('npcs.list', campaign_id=campaign_id))
    
    return render_template('npcs/form.html', campaign=campaign, form=form)

@bp.route('/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def edit(campaign_id, id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.user_id != current_user.id:
        flash('You can only edit NPCs in your own campaigns!', 'error')
        return redirect(url_for('campaigns.list'))
    
    npc = NPC.query.get_or_404(id)
    if npc.campaign_id != campaign_id:
        flash('NPC does not belong to this campaign!', 'error')
        return redirect(url_for('npcs.list', campaign_id=campaign_id))
    
    form = NPCForm(obj=npc)
    if form.validate_on_submit():
        npc.name = form.name.data
        npc.role = form.role.data
        npc.attitude = form.attitude.data
        npc.places_to_find = form.places_to_find.data
        npc.description = form.description.data
        npc.equipment = form.equipment.data
        db.session.commit()
        flash('NPC updated successfully!', 'success')
        return redirect(url_for('npcs.view', campaign_id=campaign_id, id=id))
    
    return render_template('npcs/form.html', campaign=campaign, npc=npc, form=form)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(campaign_id, id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.user_id != current_user.id:
        flash('You can only delete NPCs from your own campaigns!', 'error')
        return redirect(url_for('campaigns.list'))
    
    npc = NPC.query.get_or_404(id)
    if npc.campaign_id != campaign_id:
        flash('NPC does not belong to this campaign!', 'error')
        return redirect(url_for('npcs.list', campaign_id=campaign_id))
    
    db.session.delete(npc)
    db.session.commit()
    flash('NPC deleted successfully!', 'success')
    return redirect(url_for('npcs.list', campaign_id=campaign_id)) 