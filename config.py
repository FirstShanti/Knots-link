import os

class Configuration(object):
	DEBUG = True
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	SECRET_KEY = os.environ.get('SECRET_KEY')
	CKEDITOR_PKG_TYPE = "standard"


class Home(Configuration):
	try:
		SQLALCHEMY_DATABASE_URI = os.environ.get('DB').format(
			os.environ['DB_USERNAME'],
			os.environ['DB_PASSWORD'],
			os.environ['DB_NAME']
		)
	except Exception as e:
		print(e.__class__)

class Work(Configuration):
	try:
		SQLALCHEMY_DATABASE_URI = os.environ.get('DB')
	except Exception as e:
		print(e.__class__)