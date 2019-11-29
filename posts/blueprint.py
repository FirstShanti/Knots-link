from flask import Blueprint, render_template
from models import Post

posts = Blueprint('posts', __name__, template_folder='templates')
about = Blueprint('about', __name__, template_folder='templates')

@posts.route('/')
def index():
    posts = Post.query.all()
    return render_template('posts/index.html', posts=posts)


@posts.route('/<slug>')
def post_content(slug):
    post = Post.query.filter(Post.slug==slug).first()
    return render_template('posts/post_content.html', post=post)

@about.route('/')
def contacts():
    return render_template('posts/about.html', post=about)
