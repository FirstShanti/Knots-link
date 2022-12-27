from functools import wraps
from urllib import response

from flask import redirect, request, url_for, flash
from flask_jwt_extended import current_user


def is_email_authenticated(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		try:
			if not current_user.authenticated:
				flash(u'Before saving the changes, you must confirm the email address.', 'alert alert-warning')
		except KeyError:
			return redirect(url_for('login.log_in'))
		return f(*args, **kwargs)
	return decorated_function