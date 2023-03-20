from distutils import errors
from flask import redirect, request
from flask_cors import CORS
from flask_restful import Api

from app import app, db, jwt#, csrf
from login.routes import login
from login.api import AuthApi
from admin.routes import admin
from posts.routes import posts#, quest
from user_profile.routes import user_profile
from chat.routes import message
from chat.api import ChatApi, MessageApi
from chat.socket_session import socketio
from exceptions import errors
from models import *
from flask_jwt_extended import verify_jwt_in_request, current_user


import view

api = Api(app, prefix='/api/v1', errors=errors)
CORS(app, resorces={r'/api/*': {"origins": '*'}})


api.add_resource(ChatApi, '/chat')
api.add_resource(MessageApi, '/messages')
api.add_resource(AuthApi, '/authenticate')

app.register_blueprint(login, url_prefix='/')
app.register_blueprint(posts, url_prefix='/blog')
app.register_blueprint(user_profile, url_prefix='/knot')
app.register_blueprint(message, url_prefix='/messanger')

# app.register_blueprint(quest, url_prefix='/quest')

@app.before_request
def admin_gate():
    origin = request.scheme + '://' + request.host
    if request.path == '/admin/' or request.headers.get('Referer') ==  origin + '/admin/':
        access_token = request.cookies.get('access_token_cookie')
        if access_token and not TokenBlackList.query.filter_by(access_token=access_token).first():
            verify_jwt_in_request()
            if current_user.admin:
                pass
        else:
            return redirect(origin + '/blog/')

@jwt.user_identity_loader
def _user_identity_lookup(data):
    return data['user']

@jwt.user_lookup_loader
def _user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    user = get_user(user_id=identity)
    if user is None:
        return None
    return user

@app.context_processor
def app_environment():
    return {
        'dev_anv': app.config.get('DEBUG'),
    }

if __name__=='__main__':
    socketio.run(app, host=app.config['HOST'], port=app.config['PORT'])
