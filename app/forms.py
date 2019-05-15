#pending to add comments to news

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class CommentForm(FlaskForm):

    user = StringField('Usuario', validators=[
        DataRequired(), Length(min=1, max=50)])
    comment = TextAreaField('Qúe opinas?', validators=[
        DataRequired(), Length(min=1, max=400)])
    submit = SubmitField('Publicar')