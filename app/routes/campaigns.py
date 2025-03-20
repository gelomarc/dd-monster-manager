from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from flask_login import login_required, current_user
from app import db
from app.models.campaign import Campaign

bp = Blueprint('campaigns', __name__)

@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('campaigns.list'))
    return render_template('index.html')

@bp.route('/campaigns')
@login_required
def list():
    campaigns = Campaign.query.filter_by(user_id=current_user.id).all()
    return render_template('campaigns/list.html', campaigns=campaigns)

@bp.route('/campaigns/<int:id>')
@login_required
def detail(id):
    campaign = Campaign.query.get_or_404(id)
    if campaign.user_id != current_user.id:
        flash('You can only view your own campaigns!')
        return redirect(url_for('campaigns.list'))
        
    return render_template('campaigns/detail.html', campaign=campaign)

@bp.route('/campaigns/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            campaign = Campaign(
                title=title,
                description=description,
                user_id=current_user.id
            )
            db.session.add(campaign)
            db.session.commit()
            flash('Campaign created successfully!')
            return redirect(url_for('campaigns.list'))

    return render_template('campaigns/create.html')

@bp.route('/campaigns/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    campaign = Campaign.query.get_or_404(id)
    
    if campaign.user_id != current_user.id:
        flash('You can only delete your own campaigns!')
        return redirect(url_for('campaigns.list'))
        
    db.session.delete(campaign)
    db.session.commit()
    flash('Campaign deleted successfully!')
    return redirect(url_for('campaigns.list')) 