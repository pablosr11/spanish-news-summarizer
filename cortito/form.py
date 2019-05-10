#pending to add comments to news

from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class CommentForm(FlaskForm):

    comment = TextAreaField('Qúe opinas?', validators=[
        DataRequired(), Length(min=1, max=400)])
    submit = SubmitField('Publicar')