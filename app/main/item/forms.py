# -*- coding:utf-8 -*-
from app.models import Item
from flask_pagedown.fields import PageDownField
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms import ValidationError
from wtforms.validators import Length, DataRequired, Regexp


class EditItemForm(FlaskForm):
    itemType = StringField(u"Rodzaj",
                       validators=[DataRequired(message=u"Proszę wypełnić to pole!"),
                                   Length(1, 128, message=u"Długość od 1 do 128 znaków.")])
    platform = StringField(u"Platforma",
                       validators=[DataRequired(message=u"Proszę wypełnić to pole!"),
                                   Length(1, 128, message=u"Długość od 1 do 128 znaków.")])                               
    title = StringField(u"Tytuł",
                        validators=[DataRequired(message=u"Proszę wypełnić to pole!"), Length(1, 128, message=u"Długość od 1 do 128 znaków.")])
    author = StringField(u"Autor", validators=[Length(0, 128, message=u"Długość od 0 do 128 znaków.")])
    publisher = StringField(u"Wydawca", validators=[Length(0, 64, message=u"Długość od 0 do 64 znaków.")])
    image = StringField(u"Zdjęcie", validators=[Length(0, 128, message=u"Długość od 0 do 128 znaków.")])
    pubdate = StringField(u"Data wydania", validators=[Length(0, 32, message=u"Długość od 0 do 32 znaków.")])
    price = StringField(u"Cena", validators=[Length(0, 64, message=u"Długość od 0 do 64 znaków.")])
    summary = PageDownField(u"Podsumowanie")
    amount = IntegerField(u'Ilość')
    submit = SubmitField(u"Zatwierdź")

"""
class AddItemForm(EditItemForm):
    def validate_title(self, filed):
        if Item.query.filter_by(title=filed.data).count():
            raise ValidationError(u'Ten numer ISBN już istnieje w systemie!.')
"""

class SearchForm(FlaskForm):
    search = StringField(validators=[DataRequired()])
    submit = SubmitField(u"Szukaj")


