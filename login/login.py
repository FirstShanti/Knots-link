from flask import (
	render_template,
	Blueprint,
	session,
	request,
	redirect,
	url_for,
	jsonify
)
from app import app
from forms import RegistrationForm, LoginForm
from models import Knot
from login.hash import encrypt_string
from app import db

# route user enter data to form for autorization process.

login = Blueprint('login', __name__, template_folder='templates')


@login.route('/sign_up', methods=['GET', 'POST'])
def sign_up():

	form = RegistrationForm(request.form)
	print('test session', session)

	if 'username' in session:
		#точка выхода из сессии
		print('test url_for', url_for('posts.index'))
		return redirect('/blog/')

	elif request.method == 'POST' and form.validate_on_submit(): 
		try:
			knot = Knot(
				f_name=form.f_name.data,
				s_name=form.s_name.data,
				username=form.username.data,
				number=form.number.data,
				# включить шифрование для номеров телефона
				password=encrypt_string(form.password.data)
			)
			session['username'] = form.username.data
			db.session.add(knot)
			db.session.commit()
		except:
			print('something wrong')
		return redirect(url_for('posts.index'))
		return jsonify({'status': 'success'})
	
	return render_template('login/registration.html',
		title='Sign In',
		form=form,
		session=session
	)


@login.route('/log_in', methods=['POST', 'GET'])
def log_in():

	form = LoginForm(request.form)
	print('test session', session)
	
	if 'username' in session:
		return redirect('/blog/')

	elif request.method == "POST" and form.validate_on_submit():
		user = Knot.query.filter_by(username=form.username.data).first()
		if user.password == encrypt_string(
			form.password.data
		):
			session['username'] = user.username
			return redirect(url_for('posts.index'))
			
	return render_template('login/login.html',
		title='Log in',
		form=form,
		session=session
	)
	
@login.route('/log_out', methods=['POST', 'GET'])
def log_out():
	if session['username']:
		session.clear()
		return redirect('/')