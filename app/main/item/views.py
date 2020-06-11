# -*- coding:utf-8 -*-
from app import db
from app.models import Item, Log, Comment, Permission, Cart
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import current_user, login_required
from . import item
from .forms import SearchForm, EditItemForm
from ..comment.forms import CommentForm
from ..decorators import admin_required, permission_required


@item.route('/')
def index():
    search_word = request.args.get('search', None)
    search_form = SearchForm()
    page = request.args.get('page', 1, type=int)

    the_items = Item.query
    if not current_user.can(Permission.UPDATE_ITEM_INFORMATION):
        the_items = Item.query.filter_by(hidden=0)

    if search_word:
        search_word = search_word.strip()
        the_items = the_items.filter(db.or_(
            Item.title.ilike(u"%%%s%%" % search_word), Item.author.ilike(u"%%%s%%" % search_word), Item.itemtype.ilike(
                u"%%%s%%" % search_word), Item.platform.ilike(u"%%%s%%" % search_word)))
        search_form.search.data = search_word
    else:
        the_items = Item.query.order_by(Item.id.desc())

    pagination = the_items.paginate(page, per_page=8)
    result_items = pagination.items
    return render_template("item.html", items=result_items, pagination=pagination, search_form=search_form,
                           title=u"Lista pozycji")


@item.route('/<item_id>/')
def detail(item_id):
    the_item = Item.query.get_or_404(item_id)

    if the_item.hidden and (not current_user.is_authenticated or not current_user.is_administrator()):
        abort(404)

    show = request.args.get('show', 0, type=int)
    page = request.args.get('page', 1, type=int)
    form = CommentForm()

    if show in (1, 2):
        pagination = the_item.logs.filter_by(returned=show - 1) \
            .order_by(Log.borrow_timestamp.desc()).paginate(page, per_page=5)
    else:
        pagination = the_item.comments.filter_by(deleted=0) \
            .order_by(Comment.edit_timestamp.desc()).paginate(page, per_page=5)

    data = pagination.items
    return render_template("item_detail.html", item=the_item, data=data, pagination=pagination, form=form,
                           title=the_item.title)


@item.route('/<int:item_id>/edit/', methods=['GET', 'POST'])
@permission_required(Permission.UPDATE_ITEM_INFORMATION)
def edit(item_id):
    item = Item.query.get_or_404(item_id)
    form = EditItemForm()
    if form.validate_on_submit():
        item.itemtype = form.itemtype.data
        item.platform = form.platform.data
        item.title = form.title.data
        item.author = form.author.data
        item.publisher = form.publisher.data
        item.image = form.image.data
        item.pubdate = form.pubdate.data
        item.price = form.price.data
        item.summary = form.summary.data
        item.amount = form.amount.data
        db.session.add(item)
        db.session.commit()
        flash(u'Dodano pozycję!', 'success')
        return redirect(url_for('item.detail', item_id=item_id))
    form.itemtype.data = item.itemtype
    form.platform.data = item.platform
    form.title.data = item.title
    form.author.data = item.author
    form.publisher.data = item.publisher
    form.image.data = item.image
    form.pubdate.data = item.pubdate
    form.price.data = item.price
    form.summary.data = item.summary or ""
    form.amount.data = item.amount
    return render_template("item_edit.html", form=form, item=item, title=u"Edytuj pozycję")


@item.route('/add/', methods=['GET', 'POST'])
@permission_required(Permission.ADD_ITEM)
def add():
    form = EditItemForm()
    form.amount.data = 3
    if form.validate_on_submit():
        new_item = Item(
            itemtype=form.itemtype.data,
            platform=form.platform.data,
            title=form.title.data,
            author=form.author.data,
            publisher=form.publisher.data,
            image=form.image.data,
            pubdate=form.pubdate.data,
            price=form.price.data,
            summary=form.summary.data or "",
            amount=form.amount.data)
        db.session.add(new_item)
        db.session.commit()
        flash(u'Pozycja %s dodana do bazy!' % new_item.title, 'success')
        return redirect(url_for('item.detail', item_id=new_item.id))
    return render_template("item_edit.html", form=form, title=u"Dodaj nową pozycję")


@item.route('/<int:item_id>/delete/')
@permission_required(Permission.DELETE_ITEM)
def delete(item_id):
    the_item = Item.query.get_or_404(item_id)
    the_item.hidden = 1
    db.session.add(the_item)
    db.session.commit()
    flash(u'Pomyślnie usunięto ksiązki.', 'info')
    return redirect(request.args.get('next') or url_for('item.detail', item_id=item_id))


@item.route('/<int:item_id>/put_back/')
@admin_required
def put_back(item_id):
    the_item = Item.query.get_or_404(item_id)
    the_item.hidden = 0
    db.session.add(the_item)
    db.session.commit()
    flash(u'Pozycja przywrócona.', 'info')
    return redirect(request.args.get('next') or url_for('item.detail', item_id=item_id))

@item.route('/<int:item_id>/add_to_cart/')
@login_required
def add_to_cart(item_id):  
    #item_id = request.args.get('item_id')  
    cart_item = Cart(
        user_id=current_user.id,
        item_id=item_id
    )
    db.session.add(cart_item)
    db.session.commit()    
    flash(u'Pozycja dodana do koszyka!', 'success')
    return redirect(url_for('item.index', item_id=item_id))
    #return redirect(url_for('log.item_borrow',item_id=item_id))

