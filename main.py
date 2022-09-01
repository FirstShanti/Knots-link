from flask_cors import CORS
from flask_restful import Api

import view

from app import app
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


if __name__=='__main__':
    socketio.run(app)