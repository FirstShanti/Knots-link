from os import access
from flask import request, redirect, url_for
from functools import wraps
from models import TokenBlackList
from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended import current_user as jwt_current_user
from exceptions import UnauthorizedError

def session_time(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		try:
			access_token = request.cookies.get('access_token_cookie')
			if access_token and not TokenBlackList.query.filter_by(access_token=access_token).first():
				verify_jwt_in_request()
			else:
				raise UnauthorizedError
		except Exception as e:
			return redirect(url_for('login.log_in'))
		return f(*args, **kwargs)
	return decorated_function


def user_or_anon(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		current_user = None
		try:
			if request.cookies:
				access_token = request.cookies.get('access_token_cookie')
				if access_token and not TokenBlackList.query.filter_by(access_token=access_token).first():
					verify_jwt_in_request()
					current_user = jwt_current_user
		except Exception as e:
			pass
		return f(*args, current_user, **kwargs)
	return decorated_function