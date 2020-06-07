# -*- coding:utf-8 -*-
from flask import render_template, url_for, flash, redirect, request, abort, g
from flask_login import login_required, current_user
from app.models import User, Log, Permission, Cart, Item
from .forms import EditProfileForm, AvatarEditForm, AvatarUploadForm
from app import db, avatars
from . import user
import json


@user.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.id.desc()).paginate(page, per_page=10)
    users = pagination.items
    return render_template("user.html", users=users, pagination=pagination, title=u"Zarejestrowani użytkownicy")

@user.route('/<int:user_id>/cart/')
@login_required
def cart(user_id):
    class IntCart():
        def __init__(self,id,name,platform,price):
            self.id = id
            self.name = name
            self.platform = platform
            self.price = price

    cart = []
    cart_db = Cart.query.filter_by(user_id=user_id)
    total = 0
    for i,s in enumerate(cart_db):
        id = s.item_id
        the_item = Item.query.get_or_404(id)
        name = the_item.title
        platform = the_item.platform
        price = the_item.price
        cart.append(IntCart(i+1,name,platform,price))
        total+=int(the_item.price)
        #pagination = cart.paginate(page, per_page=10)
   
    return render_template("user_cart.html", cart=cart, total=total,title=u"Koszyk")



@user.route('/<int:user_id>/')
def detail(user_id):
    the_user = User.query.get_or_404(user_id)

    show = request.args.get('show', 0, type=int)
    if show != 0:
        show = 1

    page = request.args.get('page', 1, type=int)
    pagination = the_user.logs.filter_by(returned=show) \
        .order_by(Log.borrow_timestamp.desc()).paginate(page, per_page=5)
    logs = pagination.items

    return render_template("user_detail.html", user=the_user, logs=logs, pagination=pagination,
                           title=u"Użytkownik: " + the_user.name)


@user.route('/<int:user_id>/edit/', methods=['GET', 'POST'])
@login_required
def edit(user_id):
    if current_user.id == user_id or current_user.can(Permission.UPDATE_OTHERS_INFORMATION):
        the_user = User.query.get_or_404(user_id)
        form = EditProfileForm()
        if form.validate_on_submit():
            the_user.name = form.name.data
            the_user.major = form.major.data
            the_user.headline = form.headline.data
            the_user.about_me = form.about_me.data
            db.session.add(the_user)
            db.session.commit()
            flash(u'Informacje zaaktualizowane pomyślnie!', "info")
            return redirect(url_for('user.detail', user_id=user_id))
        form.name.data = the_user.name
        form.major.data = the_user.major
        form.headline.data = the_user.headline
        form.about_me.data = the_user.about_me

        return render_template('user_edit.html', form=form, user=the_user, title=u"Edytuj")
    else:
        abort(403)


@user.route('/<int:user_id>/avatar_edit/', methods=['GET', 'POST'])
@login_required
def avatar(user_id):
    if current_user.id == user_id or current_user.can(Permission.UPDATE_OTHERS_INFORMATION):
        the_user = User.query.get_or_404(user_id)
        avatar_edit_form = AvatarEditForm()
        avatar_upload_form = AvatarUploadForm()
        if avatar_upload_form.validate_on_submit():
            if 'avatar' in request.files:
                forder = str(user_id)
                avatar_name = avatars.save(avatar_upload_form.avatar.data, folder=forder)
                the_user.avatar = json.dumps({"use_out_url": False, "url": avatar_name})
                db.session.add(the_user)
                db.session.commit()
                flash(u'Pomyślnie zaaktualizowano awatar!', 'success')
                return redirect(url_for('user.detail', user_id=user_id))
        if avatar_edit_form.validate_on_submit():
            the_user.avatar = json.dumps({"use_out_url": True, "url": avatar_edit_form.avatar_url.data})
            db.session.add(the_user)
            db.session.commit()
            return redirect(url_for('user.detail', user_id=user_id))
        return render_template('avatar_edit.html', user=the_user, avatar_edit_form=avatar_edit_form,
                               avatar_upload_form=avatar_upload_form, title=u"Zmień awatar")
    else:
        abort(403)
