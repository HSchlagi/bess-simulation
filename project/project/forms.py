from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, FileField, SubmitField, DateField
from wtforms.validators import DataRequired

class CustomerForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    company = StringField('Company')
    contact = StringField('Contact')
    submit = SubmitField('Save')

class ProjectForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    location = StringField('Location')
    date = DateField('Date')
    bess_size = FloatField('BESS Size (kWh)')
    pv_power = FloatField('PV Power (kW)')
    hp_power = FloatField('Hydro Power (kW)')
    submit = SubmitField('Save')

class UploadForm(FlaskForm):
    file = FileField('Profile File', validators=[DataRequired()])
    submit = SubmitField('Upload')
