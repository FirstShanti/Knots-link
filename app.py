import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor
from config import Development, Production, environments, env

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


if env:
    app.config.from_object(environments[env.get('ENVIRONMENT')])
else:
    app.config.from_object(environments['Production'])

db = SQLAlchemy(app)
ckeditor = CKEditor(app)

