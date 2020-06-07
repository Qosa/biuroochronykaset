# -*- coding:utf-8 -*-
from app import db
from app.models import Item, Comment, Permission
from flask import url_for, flash, redirect, request, abort
from flask_login import login_required, current_user
from . import comment
from .forms import CommentForm
from ..decorators import permission_required


@comment.route('/add/<int:item_id>/', methods=['POST', ])
@login_required
@permission_required(Permission.WRITE_COMMENT)
def add(item_id):
    form = CommentForm()
    the_item = Item.query.get_or_404(item_id)
    if the_item.hidden and not current_user.is_administrator():
        abort(404)

    if form.validate_on_submit():
        the_comment = Comment(user=current_user, item=the_item, comment=form.comment.data)
        db.session.add(the_comment)
        db.session.commit()
        flash(u'Recenzja została opublikowana', 'success')
    return redirect(request.args.get('next') or url_for('item.detail', item_id=item_id))


@comment.route('/delete/<int:comment_id>')
@login_required
def delete(comment_id):
    the_comment = Comment.query.get_or_404(comment_id)
    if current_user.id == the_comment.user_id or current_user.can(Permission.DELETE_OTHERS_COMMENT):
        the_comment.deleted = 1
        item_id = the_comment.item_id
        db.session.add(the_comment)
        db.session.commit()
        flash(u'Komentarz usunięto.', 'info')
        return redirect(request.args.get('next') or url_for('item.detail', item_id=item_id))
    else:
        abort(403)
