import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from config import Development, Production, environments, env
# from gevent.server import StreamServer

app = Flask(__name__)
app.config.from_object(environments[env.get('ENVIRONMENT')])

db = SQLAlchemy(app)
ckeditor = CKEditor(app)

# migrate data to sql
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand) 

# server = StreamServer((app), handle) # creates a new server
# server.start()









