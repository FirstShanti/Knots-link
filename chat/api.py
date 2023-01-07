from login.session_time import session_time
from flask_restful import Resource, reqparse
from flask_jwt_extended import current_user, jwt_required
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
class ChatApi(Resource):

	@jwt_required()
	@session_time
	def get(self):
		if current_user:
			parser = args_to_parser(validator, 'get_msgs', 'args')
			data = parser.parse_args()
			chat_id, page = data['chat_id'], int(data['page'])
			messages = [serrialize(item.__dict__) for item in get_message(chat_id=chat_id) or []]
			return {
				'status': 'success',
				'messages': messages}, 200
		return {'status': 'error', 'chat_id': None}, 403

	@jwt_required()
	@session_time
	def post(self):
		try:
			if current_user:
				parser = args_to_parser(validator, 'get_chat_uuid', 'headers')
				data = parser.parse_args()
				user = get_user(user_id=current_user.id)
				another_user = get_user(data.get('username'))
				chat = get_chat(user, another_user)
				if chat:
					return {'status': 'success', 'chat_id': chat.uuid, 'chat_username': another_user.username}, 200
				else:
					return {'status': 'success', 'chat_id': '', 'chat_username': another_user.username}, 200
		except Exception as e:
			raise e
		return {'status': 'error', 'details': 'permission denied'}, 403
