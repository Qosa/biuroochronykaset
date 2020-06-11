# -*- coding: utf-8 -*-
import json
from datetime import datetime, timedelta

import bleach
from app import db, lm, avatars
from flask import current_app, url_for
from flask_login import UserMixin, AnonymousUserMixin
from markdown import markdown
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True)
    name = db.Column(db.String(64))
    password_hash = db.deferred(db.Column(db.String(128)))
    major = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    headline = db.Column(db.String(32), nullable=True)
    about_me = db.deferred(db.Column(db.Text, nullable=True))
    about_me_html = db.deferred(db.Column(db.Text, nullable=True))
    avatar = db.Column(db.String(128))
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)

    @property
    def password(self):
        raise AttributeError('password is not readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email.lower() == current_app.config['FLASKY_ADMIN'].lower():
                self.role = Role.query.filter_by(permissions=0x1ff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        self.member_since = datetime.now()

    def can(self, permissions):
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    logs = db.relationship('Log',
                           backref=db.backref('user', lazy='joined'),
                           lazy='dynamic',
                           cascade='all, delete-orphan')

    comments = db.relationship('Comment',
                               backref=db.backref('user', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')

    def __repr__(self):
        return '<User %r>' % self.email

    def borrowing(self, item):
        return self.logs.filter_by(item_id=item.id, returned=0).first()

    def can_borrow_item(self):
        return self.logs.filter(Log.returned == 0, Log.return_timestamp < datetime.now()).count() == 0

    def borrow_item(self, item):
        if self.logs.filter(Log.returned == 0, Log.return_timestamp < datetime.now()).count() > 0:
            return False, u"Nie można wypożyczyć,zaległe książki nie zostały zwrócone!"
        if self.borrowing(item):
            return False, u'Wygląda na to, że już wypożyczyłeś tą książkę!!'
        if not item.can_borrow(id,item.id):
            return False, u'Brak egzemplarzy do wypożyczenia!'

        db.session.add(Log(self, item))
        return True, u'Wypożyczono pomyślnie %s' % item.title

    def return_item(self, log):
        if log.returned == 1 or (self.id != 1 and log.user_id != self.id):
            print(log.returned)
            print(log.user_id)
            print("user"+str(self.id))
            return False, u'Nie znaleziono takiego wypożyczenia!'
        log.returned = 1
        log.return_timestamp = datetime.now()
        db.session.add(log)
        db.session.commit()
        return True, u'Zwrot zakończony pomyślnie  %s' % log.item.title

    def avatar_url(self, _external=False):
        if self.avatar:
            avatar_json = json.loads(self.avatar)
            if avatar_json['use_out_url']:
                return avatar_json['url']
            else:
                return url_for('_uploads.uploaded_file', setname=avatars.name, filename=avatar_json['url'],
                               _external=_external)
        else:
            return url_for('static', filename='img/toad.png', _external=_external)

    @staticmethod
    def on_changed_about_me(target, value, oldvalue, initiaor):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquate', 'code', 'em', 'i',
                        'li', 'ol', 'pre', 'strong', 'ul', 'h1', 'h2', 'h3', 'p']
        target.about_me_html = bleach.linkify(
            bleach.clean(markdown(value, output_format='html'),
                         tags=allowed_tags, strip=True))


db.event.listen(User.about_me, 'set', User.on_changed_about_me)


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


lm.anonymous_user = AnonymousUser


class Permission(object):
    RETURN_ITEM = 0x01
    BORROW_ITEM = 0x02
    WRITE_COMMENT = 0x04
    DELETE_OTHERS_COMMENT = 0x08
    UPDATE_OTHERS_INFORMATION = 0x10
    UPDATE_ITEM_INFORMATION = 0x20
    ADD_ITEM = 0x40
    DELETE_ITEM = 0x80
    ADMINISTER = 0x100


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    rdefault = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.RETURN_ITEM |
                     Permission.BORROW_ITEM |
                     Permission.WRITE_COMMENT, True),
            'Moderator': (Permission.RETURN_ITEM |
                          Permission.BORROW_ITEM |
                          Permission.WRITE_COMMENT |
                          Permission.DELETE_OTHERS_COMMENT, False),
            'Administrator': (RETURN_ITEM | 0x1ff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.rdefault = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    itemtype = db.Column(db.String(128))
    platform = db.Column(db.String(128))
    title = db.Column(db.String(128))
    author = db.Column(db.String(128))
    publisher = db.Column(db.String(64))
    image = db.Column(db.String(128))
    pubdate = db.Column(db.String(32))
    price = db.Column(db.String(16))
    summary = db.deferred(db.Column(db.Text, default=""))
    summary_html = db.deferred(db.Column(db.Text))
    hidden = db.Column(db.Boolean, default=0)
    amount = db.Column(db.Integer)

    logs = db.relationship('Log',
                           backref=db.backref('item', lazy='joined'),
                           lazy='dynamic',
                           cascade='all, delete-orphan')

    comments = db.relationship('Comment', backref='item',
                               lazy='dynamic',
                               cascade='all, delete-orphan')

    @property
    def tags_string(self):
        return ",".join([tag.name for tag in self.tags.all()])

    @tags_string.setter
    def tags_string(self, value):
        self.tags = []
        tags_list = value.split(u',')
        for str in tags_list:
            tag = Tag.query.filter(Tag.name.ilike(str)).first()
            if tag is None:
                tag = Tag(name=str)

            self.tags.append(tag)

        db.session.add(self)
        db.session.commit()

    def can_borrow(self,user_id,item_id):
        if not self.hidden and self.can_borrow_number() > 0 and Cart.query.filter_by(user_id=user_id,item_id=item_id).first() == None and Log.query.filter_by(user_id=user_id,item_id=item_id,returned=0).first() == None:
            return True
        else:
            return False    
        #return ((not self.hidden) and self.can_borrow_number() > 0) or Cart.query.filter_by(user_id=user_id,item_id=item_id) != None

    def can_borrow_number(self):
        return self.amount - Log.query.filter_by(item_id=self.id, returned=0).count()

    @staticmethod
    def on_changed_summary(target, value, oldvalue, initiaor):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquate', 'code', 'em', 'i',
                        'li', 'ol', 'pre', 'strong', 'ul', 'h1', 'h2', 'h3', 'p']
        target.summary_html = bleach.linkify(
            bleach.clean(markdown(value, output_format='html'),
                         tags=allowed_tags, strip=True))

    def __repr__(self):
        return u'<Item %r>' % self.title


db.event.listen(Item.summary, 'set', Item.on_changed_summary)


class Log(db.Model):
    __tablename__ = 'logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'))
    borrow_timestamp = db.Column(db.DateTime, default=datetime.now())
    return_timestamp = db.Column(db.DateTime, default=datetime.now())
    returned = db.Column(db.Integer, default=0)

    def __init__(self, user, item):
        self.user = user
        self.item = item
        self.borrow_timestamp = datetime.now()
        self.return_timestamp = datetime.now() + timedelta(days=30)
        self.returned = 0

    def __repr__(self):
        return u'<%r - %r>' % (self.user.name, self.item.title)

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    items = db.Column(db.String(128))
    total_cost = db.Column(db.Float)
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'))

    def __init__(self,user_id,items,total_cost,payment_id):
        self.user_id = user_id
        self.items = items
        self.total_cost = total_cost
        self.payment_id = payment_id

class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    total_cost = db.Column(db.Float)
    cardholder = db.Column(db.String(128))
    card_nbr = db.Column(db.String(128))

    def __init__(self,user_id,total_cost,cardholder,card_nbr):
        self.user_id = user_id
        self.total_cost = total_cost
        self.cardholder = cardholder
        self.card_nbr = card_nbr

class Cart(db.Model):
    __tablename__ = 'cart'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'))      


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'))
    comment = db.Column(db.String(1024))
    create_timestamp = db.Column(db.DateTime, default=datetime.now())
    edit_timestamp = db.Column(db.DateTime, default=datetime.now())
    deleted = db.Column(db.Boolean, default=0)

    def __init__(self, item, user, comment):
        self.user = user
        self.item = item
        self.comment = comment
        self.create_timestamp = datetime.now()
        self.edit_timestamp = self.create_timestamp
        self.deleted = 0


