from app import db
from app.models import User, Item, Comment, Log, Permission
from flask import render_template
from flask_login import current_user
from . import main
from ..item.forms import SearchForm


@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)


@main.route('/')
def index():
    search_form = SearchForm()
    the_items = Item.query
    if not current_user.can(Permission.UPDATE_ITEM_INFORMATION):
        the_items = the_items.filter_by(hidden=0)
    popular_items = the_items.outerjoin(Log).group_by(Item.id).order_by(db.func.count(Log.id).desc()).limit(5)
    popular_users = User.query.outerjoin(Log).group_by(User.id).order_by(db.func.count(Log.id).desc()).limit(5)
    recently_comments = Comment.query.filter_by(deleted=0).order_by(Comment.edit_timestamp.desc()).limit(5)
    return render_template("index.html", items=popular_items, users=popular_users, recently_comments=recently_comments,
                           search_form=search_form)
