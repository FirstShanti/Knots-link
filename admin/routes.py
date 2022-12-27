from flask import (
	redirect,
	url_for,
)

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from app import app, db
from login.session_time import user_or_anon
from models import *


class KnotsModelView(ModelView):

    @user_or_anon
    def is_accessible(self, current_user):
        return current_user and current_user.admin

    @user_or_anon
    def is_visible(self, current_user):
        return current_user and current_user.admin

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login.log_in'))


admin = Admin(app, name='Knots admin', template_mode='bootstrap3')

admin.add_view(KnotsModelView(Knot, db.session))
admin.add_view(KnotsModelView(Post, db.session))
admin.add_view(KnotsModelView(Tag, db.session))
admin.add_view(KnotsModelView(Comment, db.session))
admin.add_view(KnotsModelView(Category, db.session))






