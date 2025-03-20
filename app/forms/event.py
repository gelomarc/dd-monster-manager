from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectMultipleField
from wtforms.validators import DataRequired

class EventForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    event_date = StringField('Date')
    npc_ids = SelectMultipleField('NPCs', coerce=int)  # Will be populated with choices in the route 