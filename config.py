import os
import locale
from dotenv import dotenv_values

env = dotenv_values(".env")
basedir = os.path.abspath(os.path.dirname(__file__))
locale.setlocale(locale.LC_ALL, "")
local = locale.getdefaultlocale()[0]
lang = {'ru_RU':{'comment':['вчера в ', 'сегодня в ', 'в']},
        'en_US':{'comment':['yesterday at ', 'today at ', 'at']}
    }


class Configuration(object):
	DEBUG = True
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	SECRET_KEY = os.environ.get('SECRET_KEY')
	CKEDITOR_PKG_TYPE = "standard"
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

class Development(Configuration):
	DEBUG = True
	SQLALCHEMY_DATABASE_URI = env.get('DATABASE_URL')
	SECRET_KEY = env.get('SECRET_KEY')
	MAIL_USERNAME=env.get('MAIL_USERNAME')
	MAIL_PASSWORD=env.get('MAIL_PASSWORD')
	HOST='0.0.0.0'
	PORT = 5000

class Production(Configuration):
	DEBUG = False


environments = {
	'Development': Development,
	'Production': Production
	}