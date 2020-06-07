# -*- coding:utf-8 -*-
from app import db
from app.models import User
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms import ValidationError
from wtforms.validators import Email, Length, DataRequired, EqualTo


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(message=u"Proszę uzupełnić to pole!"), Length(1, 64), Email(message=u"Czy to prawidłowy adres Email ?")])
    password = PasswordField(u'Hasło', validators=[DataRequired(message=u"Proszę uzupełnić to pole!"), Length(6, 32)])
    remember_me = BooleanField(u"Zapamiętaj mnie", default=True)
    submit = SubmitField(u'Zaloguj się')


class RegistrationForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(message=u"Proszę uzupełnić to pole!"), Length(1, 64), Email(message=u"Czy to prawidłowy adres Email ?")])
    name = StringField(u'Nazwa użytkownika', validators=[DataRequired(message=u"Proszę uzupełnić to pole!"), Length(1, 64)])
    password = PasswordField(u'Hasło',
                             validators=[DataRequired(message=u"Proszę uzupełnić to pole!"), EqualTo('password2', message=u'Hasła muszą być zgodne!'),
                                         Length(6, 32)])
    password2 = PasswordField(u'Potwierdź hasło', validators=[DataRequired(message=u"Proszę uzupełnić to pole!")])
    submit = SubmitField(u'Zarejestruj')

    def validate_email(self, filed):
        if User.query.filter(db.func.lower(User.email) == db.func.lower(filed.data)).first():
            raise ValidationError(u'Taki email jest już zarejestrowany!')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(u'Stare hasło', validators=[DataRequired(message=u"Proszę uzupełnić to pole!")])
    new_password = PasswordField(u'Nowe hasło', validators=[DataRequired(message=u"Proszę uzupełnić to pole!"),
                                                     EqualTo('confirm_password', message=u'Hasła muszą być zgodne'),
                                                     Length(6, 32)])
    confirm_password = PasswordField(u'Potwierdź nowe hasło', validators=[DataRequired(message=u"Proszę uzupełnić to pole!")])
    submit = SubmitField(u"Zapisz hasło")

    def validate_old_password(self, filed):
        from flask_login import current_user
        if not current_user.verify_password(filed.data):
            raise ValidationError(u'Stare hasło jest nieprawidłowe!')
