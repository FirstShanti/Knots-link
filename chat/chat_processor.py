from app import db
from models import (
	Message,
	get_user, get_chat
)

def save_message(data, user):
	current_chat = get_chat(chat_id=data['chat_id'])
	if current_chat:
		msg = Message(
			text=data['msg'],
			author=get_user(user_id=user.id))
		current_chat.messages.append(msg)
		db.session.commit()
		return msg.data()
