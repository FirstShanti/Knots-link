
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from config import * 
from flask_sslify import SSLify


app = Flask(__name__)
app.config.from_object(Configuration)

sslify = SSLify(app)
db = SQLAlchemy(app)
ckeditor = CKEditor(app)

# migrate data to sql
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand) 









