import os

class Configuration(object):
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ['SECRET_KEY']
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://{}:{}@localhost:3306/{}'\
                               .format(os.environ['DB_USERNAME'],
                                       os.environ['DB_PASSWORD'],
                                       os.environ['DB_NAME']
                                       )
