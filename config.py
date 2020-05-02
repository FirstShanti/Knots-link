import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Configuration(object):
	DEBUG = False
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	SECRET_KEY = os.environ.get('SECRET_KEY')
	CKEDITOR_PKG_TYPE = "standard"
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


class Development(Configuration):
	DEBUG = True
	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
	SECRET_KEY = 'secret-very-secret-key'


class Production(Configuration):
	pass


env = {
	'Development': Development,
	'Production': Production
	}