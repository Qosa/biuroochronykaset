# -*- coding:utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import Length, DataRequired, URL, Regexp, NumberRange
from flask_pagedown.fields import PageDownField
from flask_wtf.file import FileField, FileAllowed
from app import avatars


class EditProfileForm(FlaskForm):
    name = StringField(u'Nazwa użytkownika', validators=[DataRequired(message=u"Proszę wypełnić to pole!"), Length(1, 64, message=u"Długość od 1 do 64 znaków")])
    major = StringField(u'Zawód', validators=[Length(0, 128, message=u"Długość od 0 do 128 znaków")])
    headline = StringField(u'Motto', validators=[Length(0, 32, message=u"Maksymalnie 32 znaki")])
    about_me = PageDownField(u"O mnie")
    submit = SubmitField(u"Zapisz")


class AvatarEditForm(FlaskForm):
    avatar_url = StringField('', validators=[Length(1, 100, message=u"Długość ograniczona do 100 znaków"), URL(message=u"Podaj poprawny adres URL")])
    submit = SubmitField(u"Zapisz")


class AvatarUploadForm(FlaskForm):
    avatar = FileField('', validators=[FileAllowed(avatars, message=u"Prześlij zdjęcie")])

class TransactionProcessingForm(FlaskForm):
    street = StringField(u'Ulica', validators=[DataRequired(message=u"Proszę wypełnić to pole!"), Length(1, 64, message=u"Długość od 1 do 64 znaków")])
    house_nbr = IntegerField(u'Nr. Domu', validators=[DataRequired(message=u"Proszę wypełnić to pole!"),NumberRange(min=0, max=9999,message=u"Podaj poprawny numer domu/bloku")])
    flat_nbr = IntegerField(u'Nr. Lokalu', validators=[NumberRange(min=0, max=9999,message=u"Podaj poprawny numer mieszkania/lokalu")])
    postal_code = StringField(u'Kod pocztowy',validators=[DataRequired(message=u"Proszę wypełnić to pole!"),Regexp('[0-9]{2}\-[0-9]{3}',message="Podaj poprawny kod pocztowy")])
    city = StringField(u'Miasto', validators=[DataRequired(message=u"Proszę wypełnić to pole!"),Length(0, 64, message=u"Maksymalnie 32 znaki")])
    cardholder = StringField(u'Właściciel karty', validators=[DataRequired(message=u"Proszę wypełnić to pole!"),Length(0, 128, message=u"Maksymalnie 32 znaki")])
    card_nbr = StringField(u'Nr. karty', validators=[DataRequired(message=u"Proszę wypełnić to pole!"),Regexp('^(?:4[0-9]{12}(?:[0-9]{3})?|[25][1-7][0-9]{14}|6(?:011|5[0-9][0-9])[0-9]{12}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|(?:2131|1800|35\d{3})\d{11})$',message="Podaj poprawny numer karty płatniczej")])
    submit = SubmitField(u"Zapisz")    
