from flask_socketio import SocketIO, join_room, emit
from flask_jwt_extended import current_user, verify_jwt_in_request
from jwt.exceptions import ExpiredSignatureError

from app import app
from .chat_processor import save_message


socketio = SocketIO(app, cors_allowed_origins='*')


@socketio.on('join', namespace='/messanger/')
def join(message):
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    room = message['chat_id']
    try:
        verify_jwt_in_request()
    except ExpiredSignatureError:
        emit('status', {'status': False}, room=room)
    else:
        join_room(room)
        emit('status', {'status': True}, room=room)


@socketio.on('text', namespace='/messanger/')
def text(message):
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    room = message['chat_id']
    try:
        verify_jwt_in_request()
    except ExpiredSignatureError: 
        emit('status', {'status': False}, room=room)
    else:
        if room:
            msg = save_message(message, current_user)
            data = {'data': message, 'messages': [msg]}
            emit('message', data, room=room)


# @socketio.on('left', namespace='/messanger/')
# def left(message):
#     """Sent by clients when they leave a room.
#     A status message is broadcast to all people in the room."""
#     room = session['chat_id']
#     leave_room(room)
#     emit('status', {'msg': session.get('username') + ' has left the room.'}, room=room)
