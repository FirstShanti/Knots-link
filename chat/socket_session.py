import json

from app import app

from flask import request, session
from flask_socketio import SocketIO, send, join_room, emit, leave_room
from flask import redirect
from flask_jwt_extended import current_user, verify_jwt_in_request

from login.session_time import session_time
from .chat_processor import save_message

socketio = SocketIO(app, cors_allowed_origins='*')

@session_time
@socketio.on('join', namespace='/messanger/')
def join(message):
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    verify_jwt_in_request()
    room = message['chat_id']
    join_room(room)
    emit('status', {'msg': current_user.username + ' has entered the room.'}, room=room)


@session_time
@socketio.on('text', namespace='/messanger/')
def text(message):
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    verify_jwt_in_request()
    room = message['chat_id']
    if room:
        msg = save_message(message, current_user)
        data = {'data': message, 'messages': [msg]}
        emit('message', data, room=room)


@socketio.on('left', namespace='/messanger/')
def left(message):
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    room = session['chat_id']
    leave_room(room)
    emit('status', {'msg': session.get('username') + ' has left the room.'}, room=room)
