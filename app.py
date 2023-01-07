from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor
from config import environments, env, fix_heroku_dialect_issue
from flask_migrate import Migrate#, MigrateCommand
# from flask_script import Manager
from flask_jwt_extended import JWTManager
from flask_talisman import Talisman
from middlewares import CustomSessionInterface
# from flask_marshmallow import Marshmallow
# from flask_wtf.csrf import CSRFProtect


app = Flask(__name__)
app.session_interface = CustomSessionInterface()

if env:
    app.config.from_object(environments[env.get('ENVIRONMENT')])
else:
    app.config.from_object(environments['Production'])

# csrf = CSRFProtect(app)
jwt = JWTManager(app)

# DB
fix_heroku_dialect_issue(app)
db = SQLAlchemy(app)
# ma = Marshmallow(app)

with app.app_context():
  from models import *

if not app.config['DEBUG']:
    Talisman(app, content_security_policy=None)

ckeditor = CKEditor(app)

# migrate data to sql
migrate = Migrate(app, db)
# manager = Manager(app)
# manager.add_command('db', MigrateCommand)
