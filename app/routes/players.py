from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)
from flask_login import login_required, current_user
from app import db
from app.models.player import Player
from app.models.campaign import Campaign

bp = Blueprint('players', __name__, url_prefix='/campaigns/<int:campaign_id>/players')

@bp.route('/')
@login_required
def list(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.user_id != current_user.id:
        flash('You can only view your own campaigns!')
        return redirect(url_for('campaigns.list'))
    
    players = Player.query.filter_by(campaign_id=campaign_id).all()
    return render_template('players/list.html', campaign=campaign, players=players)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.user_id != current_user.id:
        flash('You can only add players to your own campaigns!')
        return redirect(url_for('campaigns.list'))
    
    if request.method == 'POST':
        name = request.form['name']
        character_class = request.form['character_class']
        level = request.form['level']
        description = request.form['description']
        error = None

        if not name:
            error = 'Name is required.'

        if error is not None:
            flash(error)
        else:
            player = Player(
                name=name,
                character_class=character_class,
                level=int(level) if level else 1,
                description=description,
                campaign_id=campaign_id
            )
            db.session.add(player)
            db.session.commit()
            flash('Player added successfully!')
            return redirect(url_for('players.list', campaign_id=campaign_id))

    return render_template('players/create.html', campaign=campaign)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(campaign_id, id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.user_id != current_user.id:
        flash('You can only delete players from your own campaigns!')
        return redirect(url_for('campaigns.list'))
    
    player = Player.query.get_or_404(id)
    if player.campaign_id != campaign_id:
        flash('Player does not belong to this campaign!')
        return redirect(url_for('players.list', campaign_id=campaign_id))
        
    db.session.delete(player)
    db.session.commit()
    flash('Player deleted successfully!')
    return redirect(url_for('players.list', campaign_id=campaign_id)) 