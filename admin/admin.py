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
from forms import RegistrationForm, LoginForm, CategoryForm
from models import *
from datetime import datetime, timedelta
from login.session_time import session_time
from admin.admin_handler import admin_handler


admin = Blueprint('admin', __name__, template_folder='templates')

@admin.route('/paginate', methods=['GET'])
@admin_handler
@session_time
def get_next_page():
	models = {'Posts': Post, 'User': Knot, 'Tags': Tag, 'Categories': Category}
	page = request.args.get('page')
	model = models[request.args.get('model')]

	if page and page.isdigit():
		page = int(page)
	else:
		page = 1
	# сортировка видимых от последнего до первого 
	results = model.query.order_by(db.desc(model.created))

	pages = results.paginate(page=page, per_page=6, max_per_page=6)
	return pages


@admin.route('/', methods=['GET'])
@admin_handler
@session_time
def admin_index():
	data = {}
	category_form = CategoryForm(request.form)

	data.update({'Posts' : Post.query.order_by(db.desc(Post.created)).paginate(page=1, per_page=6, max_per_page=6)})
	data.update({'User' : Knot.query.order_by(db.desc(Knot.created)).paginate(page=1, per_page=6, max_per_page=6)})
	data.update({'Tags' : Tag.query.order_by(db.desc(Tag.name)).paginate(page=1, per_page=6, max_per_page=6)})
	data.update({'Categories' : Category.query.order_by(db.desc(Category.name)).paginate(page=1, per_page=6, max_per_page=6)})
	return render_template(
		'admin_index.html',
		data=[data],
		category_form=category_form
	)






