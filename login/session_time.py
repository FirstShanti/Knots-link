from flask import session, redirect, url_for, flash
from datetime import datetime, timedelta
from functools import wraps
from models import Knot


def session_time(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		try:
			if session['private_key_exp'] > datetime.now() and abs(session['last_login'] - datetime.now()).days < 1:
				session['private_key_exp'] = datetime.now() + timedelta(seconds=3600)
			else:
				session.clear()
				flash(u'Session time has expired', 'alert alert-warning')
				return redirect(url_for('login.log_in'))
		except KeyError:
			return redirect(url_for('login.log_in'))
		return f(*args, **kwargs)
	return decorated_function







	