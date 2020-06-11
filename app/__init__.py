import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_pagedown import PageDown
from flask_uploads import UploadSet, IMAGES, configure_uploads

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
lm = LoginManager(app)
bootstrap = Bootstrap(app)
pagedown = PageDown(app)
avatars = UploadSet('avatars', IMAGES)
configure_uploads(app, avatars)

from app.main import main, auth, user, item, comment, log

for blueprint in [main, auth, user, item, comment, log]:
    app.register_blueprint(blueprint)

from app import models

exists_db = os.path.isfile(app.config['DATABASE'])
