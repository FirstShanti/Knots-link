import os

class Configuration(object):
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    CKEDITOR_PKG_TYPE = "standard"


class Home(Configuration):
	SQLALCHEMY_DATABASE_URI = os.environ.get('DB').format(
	    	os.environ['DB_USERNAME'],
	    	os.environ['DB_PASSWORD'],
	    	os.environ['DB_NAME']
	    )

class Work(Configuration):
	SQLALCHEMY_DATABASE_URI = os.environ.get('DB')
