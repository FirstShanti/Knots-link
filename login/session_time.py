import traceback

from flask import session, redirect, url_for, flash
from datetime import datetime, timedelta
from functools import wraps
from models import Knot


def session_time(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		try:
			if session.get('username') and Knot.query.filter(Knot.username==session['username']).first():
				if session['private_key_exp'] > datetime.now() and abs(session['last_login'] - datetime.now()).days < 1:
					session['private_key_exp'] = datetime.now() + timedelta(seconds=3600)
				else:
					session.clear()
					flash(u'Session time has expired', 'alert alert-warning')
					return redirect(url_for('login.log_in')) #redirect=f.request.url
			else:
				session.clear()
				return redirect(url_for('login.log_in'))
		except Exception as e:
			traceback.format_exc()
			return redirect(url_for('login.log_in'))
		return f(*args, **kwargs)
	return decorated_function
