from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired

class NPCForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    role = StringField('Role', validators=[DataRequired()])
    attitude = SelectField('Attitude', 
                         choices=[
                             ('friendly', 'Friendly'),
                             ('neutral', 'Neutral'),
                             ('hostile', 'Hostile')
                         ],
                         default='neutral',
                         validators=[DataRequired()])
    places_to_find = TextAreaField('Places to Find')
    description = TextAreaField('Description')
    equipment = TextAreaField('Equipment') 