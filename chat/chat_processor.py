from datetime import datetime
from flask_jwt_extended import current_user
from app import db
from models import (
	Message,
	Chat,
	get_user, get_chat
)
from .schemas import msg_schema

def save_message(data, another_user=None):
	# chat_id = data['chat_id']
	current_chat = get_chat(current_user=current_user, another_user=another_user)
	if current_chat and str(current_user) in [str(_user) for _user in current_chat.users]:
		msg = Message(
			text=data['msg'],
			author=current_user
		)
		current_chat.messages.append(msg)
		current_chat.edited = datetime.utcnow()
		db.session.commit()
		return msg
	# TODO 
	# add raise API exception
	return []
