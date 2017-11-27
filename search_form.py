from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms_components import DateField, TimeField


class SearchForm(FlaskForm):
    crypto_pair = StringField('Crypto pair, ex: bchusd')
    start_date = DateField('Start Date')
    start_time = TimeField('Start Time')
    end_date = DateField('End Date')
    end_time = TimeField('End Time')
    submit = SubmitField('Submit')
