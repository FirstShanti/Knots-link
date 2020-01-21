from wtforms import (
	StringField,
	TextAreaField,
	PasswordField,
	BooleanField,
	SubmitField,
	Form,
	validators,
)
from wtforms.validators import (
	DataRequired,
	EqualTo,
	Length,
	ValidationError
)
from flask_wtf import FlaskForm
from flask_ckeditor import CKEditorField
from models import Knot
from login.hash import encrypt_string
import re
from models import slugify, Post
from app import db


class RegistrationForm(FlaskForm):
	f_name = StringField('First name', 
		validators=[DataRequired()])
	s_name = StringField('Last name',
		validators=[DataRequired()])
	username = StringField('Username',
		validators=[DataRequired()])
	number = StringField('Phone number',
		validators=[DataRequired()])
	password = PasswordField('New Password',
		validators=[DataRequired()])
	confirm = PasswordField('Repeat password',
		validators=[DataRequired(),
					EqualTo('password', message='Passwords do not match')])
	#accept_tos = BooleanField('I accept the TOS',
	#	validators=[DataRequired()])


	def validate_number(form, number):
		if Knot.query.filter_by(number=number.data).first() is not None:
			raise ValidationError('''This phone number is reserved.\n
									Please use another number.''') 
			

	def validate_username(form, username):
		if Knot.query.filter_by(username=username.data).first() is not None:
			raise ValidationError('Please use a different username.')
			# может следует добавить ссылку на инициалы узла 
			# который зарегистрирован под этим username

	#submit = SubmitField('register')

class LoginForm(FlaskForm):
	username = StringField('Username',
		validators=[DataRequired()])
	password = PasswordField('Password',
		validators=[DataRequired()])
	#remember_me = BooleanField('Remember me')

	def validate_username(form, username):
		if Knot.query.filter_by(username=username.data).first() is None:
			raise ValidationError('Invalid username')


	def validate_password(form, password):
		if Knot.query.filter_by(password=encrypt_string(password.data)).first() is None:
			raise ValidationError('Invalid password')
	


class PostForm(FlaskForm):
	title = StringField('Title',
		validators=[DataRequired(), Length(4, 78)])
	body = CKEditorField('Body',
		validators=[DataRequired(), Length(250, 50000)])
	tags = StringField('Tag',
		validators=[DataRequired(), Length(3, 100)])
	
	def validate_tags(form, tags):
		invalid_tags = re.findall(r"[!@#$%^&*()~`\-+=\/?\|:\;'\"{}\\.\[\]]", str(tags._value()))
		if invalid_tags:
			raise ValidationError(f'Invalid char in tag: {", ".join(i for i in invalid_tags)}')

	#def validate_title(form, title):
	#	if Post.query.filter(Post.slug==slugify(str(title._value()))).first():
	#		raise ValidationError(f'Non uniq title')


class CommentForm(FlaskForm):
	text = StringField('Text',
		validators=[DataRequired(), Length(1, 2000)])
