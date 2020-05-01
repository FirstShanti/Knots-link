from flask import (
	render_template,
	Blueprint,
	session,
	request,
	redirect,
	url_for,
	jsonify,
	flash
)
import os
from app import app, db
from forms import RegistrationForm, LoginForm
from models import Knot
from login.hash import encrypt_string
from datetime import datetime, timedelta
from .send_email import send_email


# route user enter data to form for autorization process.
login = Blueprint('login', __name__, template_folder='templates')


@login.route('auth/', methods=['GET'])
def authentication():

	now = datetime.now()

	try:
		user = Knot.query.filter(Knot.slug==request.args.get('user')).first()
		time_delta = now - user.auth_key_create

		if user.authenticated:
			return redirect('/blog/')
		elif user.auth_key == request.args.get('key') and user.check_auth_key():
			user.authenticated = 1
			db.session.commit()
			flash(u'Your email address has been verified!', 'alert alert-success')
			return redirect(url_for('login.log_in'))
		else:
			user.get_auth_key()
			send_email(user)
			flash(u'Time has passed, we are sending a new link', 'alert alert-danger')
			return redirect(url_for('login.log_in'))
	except Exception as e:
		print(f'Something wrong: {e.__class__}')
		return redirect(url_for('posts.index'))


@login.route('/sign_up', methods=['GET', 'POST'])
def sign_up():

	form = RegistrationForm(request.form)

	if 'username' in session:
		return redirect('/blog/')
	elif request.method == 'POST' and form.validate_on_submit(): 
		try:
			user = Knot(
				f_name=form.f_name.data,
				s_name=form.s_name.data,
				username=form.username.data,
				# включить шифрование для номеров телефона
				number=form.number.data,
				email=form.email.data,
				password=encrypt_string(form.password.data)
			)
			send_email(user)
			db.session.add(user)
			db.session.commit()
			flash(u'Confirm you email', 'alert alert-warning')
		except Exception as e:
			print(f'Something wrong: {e.__class__}')
			raise e
		return redirect(url_for('login.log_in'))	
	return render_template('registration.html',
		title='Sign In',
		form=form,
		session=session,
		endpoint=request.endpoint
	)


@login.route('/log_in', methods=['POST', 'GET'])
def log_in(alert=None):
	url = request.url_root
	form = LoginForm(request.form)
	alert = request.args.get('alert')

	if 'username' in session:
		return redirect('/blog/')
	elif request.method == "POST" and form.validate_on_submit():
		user = Knot.query.filter_by(username=form.username.data).first()
		if user.password == encrypt_string(form.password.data):
			session['username'] = user.username
			session['auth'] = user.authenticated
			user.last_login = datetime.now()
			session['last_login'] = user.last_login
			session['private_key_exp'] = user.last_login + timedelta(hours=3)
			return redirect(url_for('posts.index'))
	
	return render_template('login.html',
		title='Log in',
		form=form,
		session=session,
		alert=alert,
		endpoint=request.endpoint
	)
	
	
@login.route('/log_out', methods=['POST', 'GET'])
def log_out():
	if session['username']:
		session.clear()
		return redirect('/')