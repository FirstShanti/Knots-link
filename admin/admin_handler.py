from functools import wraps
from flask import redirect, url_for
from flask_jwt_extended import current_user
from models import Knot



def admin_handler(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		try:
			if current_user:
				user = Knot.query.filter(Knot.username==current_user.username).first()
				if user.admin:
					return f(*args, **kwargs)
				else:
					redirect(url_for('login.log_in'))
		except:
			return redirect(url_for('login.log_in'))
	return decorated_function