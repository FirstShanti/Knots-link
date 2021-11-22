import traceback
from flask import (
	render_template,
	session,
	request,
	redirect,
)
import os
from globals_cache import DailyMsg
import json

import traceback
from datetime import datetime, timedelta
from flask_restful import Resource, reqparse
from pprint import pprint
from utility import get_user
from login import session_time
from utility import get_chat, get_message, serrialize
from pprint import pprint

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
		'chat_id': dict(type=str, required=False, help='This field cannot be blank.'),
		'page': dict(type=str, required=False, help='This field cannot be blank.'),
		'another_username': dict(type=str, required=False, help='This field cannot be blank.'),
	},
	'get_chat_uuid': {
		'username': dict(type=str, required=True, help='This field cannot be blank.')
	}
}

# RESOURCES
class Chat(Resource):

	def get(self):
		if session.get('username'):
			parser = args_to_parser(validator, 'get_msgs', 'args')
			data = parser.parse_args()
			chat_id, page = data['chat_id'], int(data['page'])
			# current_user = get_user()
			# another_user = get_user(username=data['another_username'])
			messages = [serrialize(item.__dict__) for item in get_message(chat_id=chat_id)]
			return {
				'status': 'success',
				'data': messages}, 200
		return {'status': 'error', 'chat_id': None}, 403


	def post(self):
		try:
			print('in POST chat')
			if session.get('username'):
				parser = args_to_parser(validator, 'get_chat_uuid', 'headers')
				data = parser.parse_args()
				current_user = get_user()
				if current_user.username == session['username']:
					another_user = get_user(data.get('username'))
					chat = get_chat(current_user, another_user)
					print(f'return chat_id: {chat.uuid}')
					if chat:
						return {'status': 'success', 'chat_id': chat.uuid}, 200
		except Exception as e:
			print('\n\n\n', e, '\n\n\n')
			raise e
		return {'status': 'error', 'details': 'permission denied'}, 403