from email import message
import json

from app import db
from flask import jsonify, request
from itsdangerous import serializer
from login.session_time import session_time
from flask_restful import Resource, reqparse
from flask_jwt_extended import current_user, jwt_required
from models import (
	Knot,
	Chat,
	Message,
	get_user,
	get_chat,
	get_message
)
from .schemas import msgs_schema, chats_schema
from exceptions import UnauthorizedError

parser = reqparse.RequestParser(bundle_errors=True)

def args_to_parser(validator, params, location):
	parser.args.clear()
	for field, valid_param in validator[params].items():
		parser.add_argument(field, **valid_param, location=location)
	return parser

validator = {
	'send_msg': {
		'msg': dict(type=str, required=True, help='This field cannot be blank.'),
	},
	'get_msgs': {
		'receiver': dict(type=str, required=True, help='This field cannot be blank.'),
		'page': dict(type=int, required=False, help='This field cannot be blank.'),
	},
	'post_msgs': {
		'parameter': dict(type=str, required=True),
		'uuid': dict(type=str, required=True) 
	}
	# 'get_chats': {
	# 	'username': dict(type=str, required=True, help='This field cannot be blank.')
	# }
}


class MsgProcessor:

	PROCESSES = [
		'set_read'
	]

	def __init__(self, msg_uuid):
		self.msg_uuid = msg_uuid
		self.msg = Message.query.filter(Message.uuid==msg_uuid).first()

	def process(self, process):
		if process in self.PROCESSES:
			self.__getattribute__(process)()
			db.session.commit()

	def set_read(self):
		self.msg.is_read = True



# RESOURCES
class ChatApi(Resource):

	@jwt_required()
	@session_time
	def get(self):
		# parser = args_to_parser(validator, 'get_msgs', 'args')
		# data = parser.parse_args()
		# chat_id, page = data['chat_id'], int(data['page'])
		# if current_user and chat_id in current_user.chat_ids:
			# messages = [serrialize(item.__dict__) for item in get_message(chat_id=chat_id) or []]
			# return {'status': 'success', 'messages': messages}, 200
		# return {'status': 'error', 'chat_id': None}, 403
		chats = Chat.query.join(Knot.chats).filter(Knot.id==current_user.id).order_by(Chat.created)
		return chats_schema.dump(chats)

	@jwt_required()
	@session_time
	def post(self):
		try:
			if current_user:
				parser = args_to_parser(validator, 'get_chat_uuid', 'headers')
				data = parser.parse_args()
				user = get_user(user_id=current_user.id)
				another_user = get_user(username=data.get('username'))
				chat = get_chat(user, another_user)
				if chat:
					return {'status': 'success', 'chat_id': chat.uuid, 'chat_username': another_user.username}, 200
				else:
					return {'status': 'success', 'chat_id': '', 'chat_username': ''}, 200
		except Exception as e:
			raise e
		return {'status': 'error', 'details': 'permission denied'}, 403

class MessageApi(Resource):

	# @jwt_required()
	@session_time
	def get(self):
		parser = args_to_parser(validator, 'get_msgs', 'headers')
		data = parser.parse_args()
		receiver, page = data['receiver'], int(data['page'])
		another_user = get_user(uuid=receiver)
		chat = get_chat(current_user=current_user, another_user=another_user)
		if chat and current_user and chat.uuid in current_user.chat_ids:
			messages_paginated = get_message(chat=chat).paginate(page=page, per_page=20, max_per_page=20)
			messages = msgs_schema.dump(messages_paginated)
			return jsonify({
				'status': 'success',
				'msgs': messages,
				'nextPage': messages_paginated.next_num
			})
		raise UnauthorizedError

	@session_time
	def post(self):
		parser = args_to_parser(validator, 'post_msgs', 'headers')
		data = parser.parse_args()
		parameter = data['parameter']
		msg_uuid = data['uuid']
		processor = MsgProcessor(msg_uuid)
		try:
			processor.process(parameter)
		except Exception as e:
			return {'status': 'success', 'message': str(e)}, 500
		else:
			return {'status': 'success', 'message': 'readed'}, 200
			