# -*- coding:utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Length, DataRequired, URL
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
