from flask import request
from flask_socketio import SocketIO, join_room, emit
from flask_jwt_extended import current_user, verify_jwt_in_request
from jwt.exceptions import ExpiredSignatureError, DecodeError
from flask_jwt_extended.exceptions import NoAuthorizationError

from app import app
from .chat_processor import save_message
from .schemas import MessageSchema
from models import Knot

socketio = SocketIO(app, cors_allowed_origins='*', async_mode='gevent')


@socketio.on('connect', namespace='/messanger/')
def join():
    """Sent by clients when connect to socket"""
    try:
        verify_jwt_in_request()
        emit('status', {'status': True}, to=request.sid)
    except (DecodeError, ExpiredSignatureError, NoAuthorizationError):
        emit('status', {'status': False}, to=request.sid)


@socketio.on('join', namespace='/messanger/')
def join(message):
    """Sent by clients when they enter a room.
    A status message"""
    token = message.get('token')
    try:
        verify_jwt_in_request()
        if not token:
            raise NoAuthorizationError
    except (DecodeError, ExpiredSignatureError, NoAuthorizationError):
        emit('status', {'status': False}, to=str(request.sid))
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
    except (DecodeError, ExpiredSignatureError, NoAuthorizationError):
        emit('status', {'status': False}, to=request.sid)
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
            emit('status', {'status': True, 'message': str(e)}, to=str(request.sid))

# TODO to handle async task

# import asyncio

# async def background_task():
#     while True:
#         await asyncio.sleep(1)
#         socketio.emit('message', {'data': 'This is a message from the server.'})

# @socketio.on('start-task')
# def handle_start_task():
#     task = asyncio.create_task(background_task())