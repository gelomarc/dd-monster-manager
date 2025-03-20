from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectField, BooleanField
from wtforms.validators import DataRequired, Optional, NumberRange

class LootForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    quantity = IntegerField('Quantity', validators=[Optional(), NumberRange(min=1)], default=1)
    value = StringField('Value', validators=[Optional()])
    rarity = SelectField('Rarity', choices=[
        ('', '-- Select Rarity --'),
        ('Common', 'Common'),
        ('Uncommon', 'Uncommon'),
        ('Rare', 'Rare'),
        ('Very Rare', 'Very Rare'),
        ('Legendary', 'Legendary')
    ], validators=[Optional()])
    attunement = BooleanField('Requires Attunement', default=False)
    notes = TextAreaField('Notes', validators=[Optional()]) 