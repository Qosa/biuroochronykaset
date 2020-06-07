# -*- coding:utf-8 -*-
from app import db
from app.models import Item, Log, Permission, User
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_required, current_user
from . import log
from ..decorators import permission_required


@log.route('/borrow/')
@login_required
@permission_required(Permission.BORROW_ITEM)
def item_borrow():
    item_id = request.args.get('item_id')
    the_item = Item.query.get_or_404(item_id)
    if the_item.hidden and not current_user.is_administrator():
        abort(404)

    result, message = current_user.borrow_item(the_item)
    flash(message, 'success' if result else 'danger')
    db.session.commit()
    return redirect(request.args.get('next') or url_for('item.detail', item_id=item_id))


@log.route('/return/')
@login_required
@permission_required(Permission.RETURN_ITEM)
def item_return():
    log_id = request.args.get('log_id')
    item_id = request.args.get('item_id')
    the_log = None
    if log_id:
        the_log = Log.query.get(log_id)
        the_user = the_log.user_id
        the_item = the_log.item_id
        print(the_user)
        print(the_item)
    if the_item:
        the_log = Log.query.filter_by(user_id=the_user, item_id=the_item).first()
        print(the_log)
    if log is None:
        flash(u'Nie znaleziono wypożyczenia!', 'warning')
    else:
        result, message = current_user.return_item(the_log)
        flash(message, 'success' if result else 'danger')
        db.session.commit()
    return redirect(request.args.get('next') or url_for('item.detail', item_id=log_id))


@log.route('/')
@login_required
def index():
    show = request.args.get('show', 0, type=int)
    if show != 0:
        show = 1

    page = request.args.get('page', 1, type=int)
    pagination = Log.query.filter_by(returned=show).order_by(Log.borrow_timestamp.desc()).paginate(page, per_page=10)
    print(Log.query.filter_by(returned=show).order_by(Log.borrow_timestamp.desc()))
    logs = pagination.items
    return render_template("logs_info.html", logs=logs, pagination=pagination, title=u"Informacje o wypożyczeniach")
