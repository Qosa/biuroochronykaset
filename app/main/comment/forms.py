# -*- coding:utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import Length, DataRequired


class CommentForm(FlaskForm):
    comment = TextAreaField(u"Twoja recenzja",
                            validators=[DataRequired(message=u"Treść nie może być pusta!"), Length(1, 1024, message=u"Długość recenzji jest ograniczona do 1024 znaków")])
    submit = SubmitField(u"Opublikuj")
