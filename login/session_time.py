from flask import session, redirect, url_for
from datetime import datetime
from functools import wraps


def session_time(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		try:
			if session['private_key_exp'] < datetime.now():
				session.clear()
				return redirect(url_for('login.log_in', alert='P'))
		except KeyError:
			return redirect(url_for('login.log_in', alert='P'))
		return f(*args, **kwargs)
	return decorated_function







	