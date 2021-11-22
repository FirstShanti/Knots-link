import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from config import Development, Production, environments, env

app = Flask(__name__)

if env:
    app.config.from_object(environments[env.get('ENVIRONMENT')])
else:
    app.config.from_object(environments['Production'])

db = SQLAlchemy(app)
ckeditor = CKEditor(app)

# migrate data to sql
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)
