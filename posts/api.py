from flask import (
	session,
)
from flask_restful import Resource, reqparse
from models import get_user, get_chat, get_message, serrialize

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
    'get_posts': {
        'username': dict(type=str, required=False)
    }
}

# RESOURCES
# class Chat(Resource):

# 	def get(self):
# 		if session.get('username'):
# 			parser = args_to_parser(validator, 'get_msgs', 'args')
# 			data = parser.parse_args()
# 			chat_id, page = data['chat_id'], int(data['page'])
# 			# current_user = get_user()
# 			# another_user = get_user(username=data['another_username'])
# 			messages = [serrialize(item.__dict__) for item in get_message(chat_id=chat_id) or []]
# 			# from time import sleep 
# 			# sleep(50)
# 			return {
# 				'status': 'success',
# 				'messages': messages}, 200
# 		return {'status': 'error', 'chat_id': None}, 403


# 	def post(self):
# 		try:
# 			if session.get('username'):
# 				parser = args_to_parser(validator, 'get_chat_uuid', 'headers')
# 				data = parser.parse_args()
# 				current_user = get_user()
# 				if current_user.username == session['username']:
# 					another_user = get_user(data.get('username'))
# 					chat = get_chat(current_user, another_user)
# 					if chat:
# 						return {'status': 'success', 'chat_id': chat.uuid}, 200
# 		except Exception as e:
# 			raise e
# 		return {'status': 'error', 'details': 'permission denied'}, 403


class Post(Resource):

    def get(self):
        if session.get('username'):
            parser = args_to_parser(validator, 'get_posts', 'args')
            data = parser.parse_args()
            if data.get('username'):
                pass
