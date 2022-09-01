from flask import session
from models import Knot, Chat, Message
import datetime

def get_user(username=None, user_id=None):
    if username:
        return Knot.query.filter_by(username=username).first()
    elif user_id:
        return Knot.query.filter_by(id=user_id).first()
    else:
        return Knot.query.filter_by(username=session['username']).first()


def get_chat(curent_user=None, another_user=None, chat_id=None, all_chats=False):
    if chat_id:
        return Chat.query.filter(Chat.uuid==chat_id).first()
    return Chat.query.filter(Chat.users.contains(curent_user)).filter(Chat.users.contains(another_user)).first()


def get_all_chat(user_id):
    return Knot.query.filter(Knot.id==user_id).first().chats


def get_message(chat_id, msg_ig=None, username=None):
    query = Chat.query.filter(Chat.uuid==chat_id).first()
    if msg_ig:
        return Message.query.get(msg_ig).first()
    if username and query:
        return filter(lambda x : x.author_username == username, query.messages)
    if query:
        return query.messages
    # if order=='desc':
    #     return query.order_by(Message.created.desc())
    # elif order=='asc':
    #     return query.order_by(Message.created.asc())
    # return query


def serrialize(data, new_data={}):
    if not new_data:
        new_data = {}
    if isinstance(data, dict):
        if data.get('id'):
            del data['id']
        for key, value in data.items():
            if isinstance(value, datetime.datetime):
                new_data[key] = value.timestamp() #.strftime("%Y %B %d %A %H:%M")
            elif isinstance(value, (list, dict)):
                serrialize(value, new_data)
            elif key == '_sa_instance_state':
                continue
            else:
                new_data[key] = value
    elif isinstance(data, list):
        for key, value in enumerate(data, 0):
            if isinstance(value, datetime.datetime):
                new_data[key] = value.timestamp() #.strftime("%Y %B %d %A %H:%M")
            elif isinstance(value, (list, dict)):
                serrialize(value, new_data)
            elif key == '_sa_instance_state':
                continue
            else:
                new_data[key] = value
    return new_data



