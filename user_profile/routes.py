from flask import (
    Blueprint,
    request,
    render_template,
    redirect,
    url_for
)
from flask_jwt_extended import current_user
from login.session_time import session_time
from models import Knot, Post, Category


user_profile = Blueprint('user_profile',
    __name__,
    template_folder='templates')


@user_profile.route('/<slug>')
@session_time
def get_user_data(slug):
    page = request.args.get('page')

    if slug == 'anonymous':
        return redirect(url_for('login.log_in'))

    try:
        user = Knot.query.filter(Knot.username==slug).first()

        posts = Post.query.filter(Post.author==slug)

        if current_user.username != slug:
            posts = posts.filter(Post.visible==True)

        if not user:
            return redirect(url_for('posts.index'))

        if page and page.isdigit():
            page = int(page)
        else:
            page = 1

    except Exception as e:
        return redirect(url_for('login.log_in'))

    pages = posts.paginate(page=page, per_page=6)

    return render_template('about.html',
        first_name=user.f_name,
        second_name=user.s_name,
        username=user.username,
        phone_number=user.phone_number,
        email=user.email,
        posts=posts,
        pages=pages,
        categories=Category.query.all()
    )