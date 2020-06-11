import os

basedir = os.path.abspath(os.path.dirname(__file__))
#DATABASE = os.path.join(basedir, 'app.db')

MAX_CONTENT_LENGTH = 1024 * 1024

UPLOADS_DEFAULT_DEST = os.path.join(basedir, 'upload/')

SQLALCHEMY_DATABASE_URI = 'postgres://mmdtnlminvbljk:55022d8ecfbed3ba08dedf6a504bff4c18aabfc8a64a1779d8f1d868a7d42fbb@ec2-54-75-246-118.eu-west-1.compute.amazonaws.com:5432/d8n9suk82pv1ju'

SECRET_KEY = 'you-will-never-guess'

FLASKY_ADMIN = 'root@gmail.com'

SQLALCHEMY_TRACK_MODIFICATIONS = False
