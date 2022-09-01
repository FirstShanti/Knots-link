from flask_cors import CORS
from flask_restful import Api
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Command

from app import app, db
from admin.admin import admin
from login.login import login
from posts.blueprint import posts, user_profile, message#, quest
from resources.chat import Chat
from chat.socket_session import socketio

import view


api = Api(app, prefix='/api/v1')
CORS(app, resorces={r'/d/*': {"origins": '*'}})

api.add_resource(Chat, '/chat')

app.register_blueprint(login, url_prefix='/')
app.register_blueprint(posts, url_prefix='/blog')
app.register_blueprint(user_profile, url_prefix='/knot')
app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(message, url_prefix='/messanger')
# app.register_blueprint(quest, url_prefix='/quest')

# Custom commands classes
class RunServer(Command):

    def run(self):
        socketio.run(app, host=app.config['HOST'], port=app.config['PORT'])

# migrate data to sql
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

# start server command
manager.add_command('runserver', RunServer)

if __name__=='__main__':
    socketio.run(app, host=app.config['HOST'], port=app.config['PORT'])