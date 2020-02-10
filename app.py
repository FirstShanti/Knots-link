
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from config import * 
import sys
import logging




app = Flask(__name__)
app.config.from_object(Configuration)

db = SQLAlchemy(app)
ckeditor = CKEditor(app)
app.cli.add_command(create_tables)
# migrate data to sql
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand) 
# heroku logs
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)









