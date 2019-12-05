from wtforms import Form, StringField, TextAreaField, validators



class PostForm(Form):
	title = StringField('Title', [validators.Length(min=4, max=78)])
	body = TextAreaField('Body', [validators.Length(min=250, max=50000)])
	name = StringField('Tag', [validators.Length(min=3, max=100)])

