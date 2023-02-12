from pyexpat.errors import messages
from flask_socketio import SocketIO, join_room, emit
from flask_jwt_extended import current_user, verify_jwt_in_request
from itsdangerous import serializer
from jwt.exceptions import ExpiredSignatureError
from flask_jwt_extended.exceptions import NoAuthorizationError

from app import app
from .chat_processor import save_message
from .schemas import MessageSchema
from models import Knot

socketio = SocketIO(app, cors_allowed_origins='*')


@socketio.on('join', namespace='/messanger/')
def join(message):
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    token = message.get('token')
    try:
        verify_jwt_in_request()
        if not token:
            raise NoAuthorizationError
    except (ExpiredSignatureError, NoAuthorizationError):
        emit('status', {'status': False}, room=str(current_user))
    else:
        join_room(str(current_user))
        emit('status', {'status': True}, room=str(current_user))


@socketio.on('text', namespace='/messanger/')
def text(message):
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    receiver = message.get('receiver')
    token = message.get('token')
    try:
        verify_jwt_in_request()
        if not token:
            raise NoAuthorizationError
    except (ExpiredSignatureError, NoAuthorizationError):
        emit('status', {'status': False}, room=str(current_user))
    else:
        try:
            another_user = Knot.query.filter(Knot.uuid==receiver).first()
            msg = save_message(message, another_user)
            del message['token']
            serializer_for_right = MessageSchema(context={'user': current_user})
            right_data = {'data': message, 'message': serializer_for_right.dump(msg)}
            emit('message', right_data, room=str(current_user))
            message['receiver'] = str(current_user.uuid)
            serializer_for_left = MessageSchema(context={'user': another_user})
            left_data = {'data': message, 'message': serializer_for_left.dump(msg)}
            emit('message', left_data, room=str(receiver))
        except Exception as e:
            emit('status', {'status': True, 'message': str(e)}, room=str(current_user))

# @socketio.on('left', namespace='/messanger/')
# def left(message):
#     """Sent by clients when they leave a room.
#     A status message is broadcast to all people in the room."""
#     room = session['chat_id']
#     leave_room(room)
#     emit('status', {'msg': session.get('username') + ' has left the room.'}, room=room)
