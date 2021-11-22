from flask import session, redirect, url_for, flash
from functools import wraps

from utility import get_user


def is_email_authenticated(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		# print(f.__dict__)
		try:
			if session.get('username') and (user:= get_user(session['username'])):
				if not user.authenticated:
					flash(u'You must confirm email', 'alert alert-warning')
					return redirect(url_for('posts.index')) #redirect=f.request.url
			else:
				session.clear()
				# flash(u'Session time has expired', 'alert alert-warning')
				return redirect(url_for('login.log_in'))
		except KeyError:
			return redirect(url_for('login.log_in'))
		return f(*args, **kwargs)
	return decorated_function