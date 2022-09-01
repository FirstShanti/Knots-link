from flask import session
from app import db
from utility import get_user, get_chat
from models import Message


def save_message(data):
	current_user = get_user()
	current_chat = get_chat(chat_id=data['chat_id'])
	if current_chat:
		msg = Message(
			text=data['msg'],
			author=current_user)
		current_chat.messages.append(msg)
		db.session.commit()
		return msg.data()
