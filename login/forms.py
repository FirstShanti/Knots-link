
import re

from flask_wtf import FlaskForm
from wtforms import (
	StringField,
	PasswordField,
)
from wtforms.validators import (
	DataRequired,
	EqualTo,
	ValidationError
)

from models import Knot, Category
from models import Category


def password_validator(content):
    if not any([char.isdigit() for char in content]):
        raise ValidationError('Password must include numbers')
    if not any([char.isalpha() for char in content]):
        raise ValidationError('Password must include letters')


def email_validation(email):
	try:
		email = re.match(r"^[a-zA-Z0-9_'+*/^&=?~{}\-](\.?[a-zA-Z0-9_'+*/^&=?~{}\-])*\@((\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(\:\d{1,3})?)|(((([a-zA-Z0-9][a-zA-Z0-9\-]+[a-zA-Z0-9])|([a-zA-Z0-9]{1,2}))[\.]{1})+([a-zA-Z]{2,6})))$", email).string
	except AttributeError:
		raise ValidationError("Invalid email")


def get_category():
	return [('ch', '--choose category--',)] + [(i.short_name, i.name) for i in Category.query.all()]


class RegistrationForm(FlaskForm):
	f_name = StringField('First name', 
		validators=[DataRequired()], id='first name')
	s_name = StringField('Last name',
		validators=[DataRequired()], id='last name')
	username = StringField('Username',
		validators=[DataRequired()], id='username')
	email = StringField('Email*',
		validators=[DataRequired()], id='email')
	phone_number = StringField('Phone number', id='phone number')
	password = PasswordField('New Password',
		validators=[DataRequired()], id='password')
	confirm = PasswordField('Re-enter password',
		validators=[DataRequired(),
					EqualTo('password', message='Passwords do not match')],
		id='repeat password*')
	#accept_tos = BooleanField('I accept the TOS',
	#	validators=[DataRequired()])

	def validate_email(form, email):
		email_validation(email.data)
		if Knot.query.filter_by(email=email.data).first() is not None:
			raise ValidationError('''This email number is reserved.''')

	def validate_number(form, phone_number):
		if phone_number.data:
			try:
				num = re.match(r"^(\s*)?(\+)?([- _():=+]?\d[- _():=+]?){10,14}(\s*)?$", phone_number.data).string
				if Knot.query.filter_by(phone_number=num).first() is not None:
					raise ValidationError('''This phone number is reserved.\n
						Please use another number.''')
			except AttributeError:
				raise ValidationError('''Invalid number''')
		else:
			pass

	def validate_username(form, username):
		if Knot.query.filter_by(username=username.data).first() is not None:
			raise ValidationError('Please use a different username.')

	def validate_password(form, password):
		password_validator(password.data)


class LoginForm(FlaskForm):
	username = StringField('Username',
		validators=[DataRequired()])
	password = PasswordField('Password',
		validators=[DataRequired()])
	# recaptcha = RecaptchaField()
	# remember_me = BooleanField('Remember me')


class EmailForm(FlaskForm):
	email = StringField('Email',
		validators=[DataRequired()], id='email')


class ResetPasswordForm(FlaskForm):
	password = PasswordField('Password',
		validators=[DataRequired()])
	repeat_password = PasswordField('Re-enter password',
		validators=[DataRequired(),
					EqualTo('password', message='Passwords do not match')])

	def validate_password(form, password):
		password_validator(password.data)
