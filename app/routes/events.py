from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)
from flask_login import login_required, current_user
from app import db
from app.models.event import Event
from app.models.campaign import Campaign
from app.models.npc import NPC
from app.forms.event import EventForm

bp = Blueprint('events', __name__, url_prefix='/campaigns/<int:campaign_id>/events')

@bp.route('/')
@login_required
def list(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.user_id != current_user.id:
        flash('You can only view events in your own campaigns!', 'error')
        return redirect(url_for('campaigns.list'))
    
    events = Event.query.filter_by(campaign_id=campaign_id).order_by(Event.event_date.desc()).all()
    return render_template('events/list.html', campaign=campaign, events=events)

@bp.route('/<int:id>')
@login_required
def view(campaign_id, id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.user_id != current_user.id:
        flash('You can only view events in your own campaigns!', 'error')
        return redirect(url_for('campaigns.list'))
    
    event = Event.query.get_or_404(id)
    if event.campaign_id != campaign_id:
        flash('Event does not belong to this campaign!', 'error')
        return redirect(url_for('events.list', campaign_id=campaign_id))
    
    return render_template('events/view.html', campaign=campaign, event=event)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.user_id != current_user.id:
        flash('You can only add events to your own campaigns!', 'error')
        return redirect(url_for('campaigns.list'))
    
    form = EventForm()
    # Get all NPCs from the campaign for the select field
    npcs = NPC.query.filter_by(campaign_id=campaign_id).order_by(NPC.name).all()
    form.npc_ids.choices = [(npc.id, npc.name) for npc in npcs]
    
    if form.validate_on_submit():
        event = Event(
            title=form.title.data,
            description=form.description.data,
            event_date=form.event_date.data,
            campaign_id=campaign_id
        )
        # Add selected NPCs
        if form.npc_ids.data:
            selected_npcs = NPC.query.filter(NPC.id.in_(form.npc_ids.data)).all()
            event.npcs.extend(selected_npcs)
            
        db.session.add(event)
        db.session.commit()
        flash('Event added successfully!', 'success')
        return redirect(url_for('events.list', campaign_id=campaign_id))
    
    return render_template('events/form.html', campaign=campaign, form=form)

@bp.route('/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def edit(campaign_id, id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.user_id != current_user.id:
        flash('You can only edit events in your own campaigns!', 'error')
        return redirect(url_for('campaigns.list'))
    
    event = Event.query.get_or_404(id)
    if event.campaign_id != campaign_id:
        flash('Event does not belong to this campaign!', 'error')
        return redirect(url_for('events.list', campaign_id=campaign_id))
    
    form = EventForm(obj=event)
    # Get all NPCs from the campaign for the select field
    npcs = NPC.query.filter_by(campaign_id=campaign_id).order_by(NPC.name).all()
    form.npc_ids.choices = [(npc.id, npc.name) for npc in npcs]
    
    if request.method == 'GET':
        # Pre-select current NPCs
        form.npc_ids.data = [npc.id for npc in event.npcs]
    
    if form.validate_on_submit():
        event.title = form.title.data
        event.description = form.description.data
        event.event_date = form.event_date.data
        
        # Update NPCs
        event.npcs = []  # Clear existing NPCs
        if form.npc_ids.data:
            selected_npcs = NPC.query.filter(NPC.id.in_(form.npc_ids.data)).all()
            event.npcs.extend(selected_npcs)
        
        db.session.commit()
        flash('Event updated successfully!', 'success')
        return redirect(url_for('events.view', campaign_id=campaign_id, id=id))
    
    return render_template('events/form.html', campaign=campaign, event=event, form=form)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(campaign_id, id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.user_id != current_user.id:
        flash('You can only delete events from your own campaigns!', 'error')
        return redirect(url_for('campaigns.list'))
    
    event = Event.query.get_or_404(id)
    if event.campaign_id != campaign_id:
        flash('Event does not belong to this campaign!', 'error')
        return redirect(url_for('events.list', campaign_id=campaign_id))
    
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted successfully!', 'success')
    return redirect(url_for('events.list', campaign_id=campaign_id)) 