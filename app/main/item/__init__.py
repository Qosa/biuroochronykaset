from flask import Blueprint

item = Blueprint('item', __name__, url_prefix='/items',template_folder='templates')

from . import views
