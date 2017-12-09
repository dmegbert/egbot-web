from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField


class SearchForm(FlaskForm):
    trial = SelectField('Trial', coerce=str)
    submit = SubmitField('Submit')
