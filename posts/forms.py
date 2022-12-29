from app import app
from wtforms import (
	StringField,
	TextAreaField,
	SelectField,
	PasswordField,
)
from wtforms.validators import (
	DataRequired,
	EqualTo,
	Length,
	ValidationError
)
from flask_wtf import FlaskForm, RecaptchaField
from flask_ckeditor import CKEditorField
from models import Knot, Category
from utils import encrypt_string
import re
from models import Category


def get_category():
	with app.app_context():
		return [('ch', '--choose category--',)] + [(i.short_name, i.name) for i in Category.query.all()]


class PostForm(FlaskForm):
	title = StringField('Title',
		[DataRequired(), Length(4, 78)])
	preview = TextAreaField('Preview',
		[DataRequired(), Length(50, 250)])
	body = CKEditorField('Body',
		[DataRequired(), Length(250, 50000)])
	category = SelectField('Category', choices=get_category())
	tags = StringField('Tag',
		[DataRequired(), Length(3, 100)])

	def validate_tags(form, tags):
		invalid_chars = re.findall(r"[!@#$%^&*()~`\-+=\/?\|:\;'\"{}\\.\[\]]", str(tags._value()))
		invalid_tags = []
		if invalid_chars:
			for char in invalid_chars:
				for tag in str(tags._value()).split():
					if char in tag:
						invalid_tags.append(tag)
			raise ValidationError(f'\
				<span style="color: red;">Invalid char in {"tags" if len(invalid_tags) > 1 else "tag"}\
				</span> <span style="color: black;">\
				{" ".join(tag for tag in invalid_tags)}</span>:\
				<span style="color: red;">{", ".join(char for char in invalid_chars)}</span>')

	# def validate_category(form, category):
	# 	if category.data in ['ch', '--choose category--']:
	# 		raise ValidationError(f'Choose category')


class CommentForm(FlaskForm):
	text = TextAreaField('Text',
		validators=[DataRequired(), Length(1, 2000)])


class CategoryForm(FlaskForm):
	name = StringField('Name', validators=[DataRequired()])
	short_name = StringField('Short name', validators=[DataRequired()])
