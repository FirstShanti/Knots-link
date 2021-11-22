from app import app

from flask import session
from flask_socketio import SocketIO, send, join_room, emit, leave_room
from flask import redirect

from login.session_time import session_time
from .chat_processor import save_message

socketio = SocketIO(app, cors_allowed_origins='*')

@socketio.on('join', namespace='/messanger/')
@session_time
def join(message):
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    if session.get('username'):
        print('join: ', message)
        session['chat_id'] = message['chat_id']
        room = session['chat_id']
        join_room(room)
        emit('status', {'msg': session.get('username') + ' has entered the room.'}, room=room)
    else:
        session.clear()
        return redirect('/log_in')


@socketio.on('text', namespace='/messanger/')
@session_time
def text(message):
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    if session.get('username'):
        print('text: ', message)
        room = session['chat_id']
        emit('message', message, room=room)
        save_message(message)
    else:
        session.clear()
        return redirect('/log_in')


@socketio.on('left', namespace='/messanger/')
def left(message):
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    print('left: ', message)
    room = session['chat_id']
    leave_room(room)
    emit('status', {'msg': session.get('username') + ' has left the room.'}, room=room)
