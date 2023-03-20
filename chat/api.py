import json
from app import db
from flask import jsonify
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
from .schemas import msg_schema, msgs_schema, chats_schema
from exceptions import UnauthorizedError, AuthenticationError

parser = reqparse.RequestParser(bundle_errors=True)

def args_to_parser(validator, params, location):
	parser.args.clear()
	for field, valid_param in validator[params].items():
		parser.add_argument(field, **valid_param, location=location)
	return parser

validator = {
	'get_msg': {
		'receiver': dict(type=str, required=True, help='This field cannot be blank.'),
		'page': dict(type=int, required=False, help='This field cannot be blank.'),
	},
	'post_msg': {
		'uuid': dict(type=str, required=True, help='This field cannot be blank.'),
		'parameter': dict(type=str, required=True, help='This field cannot be blank.'),
		'data': dict(type=str, required=False)
	}
}


class MsgProcessor:

	PROCESSES = [
		'update'
	]

	def __init__(self, uuid, data={}, current_user=None):
		self.uuid = uuid
		self.current_user = current_user
		self.msg = Message.query.filter(Message.uuid==uuid).first()
		self.data = data

	def process(self, process):
		if process in self.PROCESSES:
			self.__getattribute__(process)()
			db.session.commit()

	def update(self):
		if self.msg and self.msg.chat in self.current_user.chats and self.data:
			msg_schema.load(
				self.data,
				session=db.session,
				instance=self.msg,
				partial=True)


# RESOURCES
class ChatApi(Resource):

	@jwt_required()
	@session_time
	def get(self):
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
		raise AuthenticationError


class MessageApi(Resource):

	@jwt_required()
	@session_time
	def get(self):
		parser = args_to_parser(validator, 'get_msg', 'headers')
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
		raise AuthenticationError


	@jwt_required()
	@session_time
	def post(self):
		parser = args_to_parser(validator, 'post_msg', 'headers')
		result = parser.parse_args()

		data = json.loads(result.get('data', {}))
		parameter = result['parameter']
		msg_uuid = result['uuid']

		processor = MsgProcessor(msg_uuid, data, current_user)

		try:
			processor.process(parameter)
		except Exception as e:
			return {'status': 'error', 'message': str(e)}, 500
		else:
			return {'status': 'success', 'message': 'ok'}, 200
			