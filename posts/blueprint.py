from flask import Blueprint, render_template, request
from models import Post, Tag
import locale

locale.setlocale(locale.LC_ALL, "")

posts = Blueprint('posts', __name__, template_folder='templates')
about = Blueprint('about', __name__, template_folder='templates')

@posts.route('/')
def index():

	q = request.args.get('q')

	if q:
		posts = Post.query.filter(Post.title.contains(q) | Post.body.contains(q)).all()
	else:
		posts = Post.query.all()
	
	return render_template('posts/index.html', posts=posts)

# http://localhost/blog/first_post
@posts.route('/<slug>')
def post_content(slug):
    post = Post.query.filter(Post.slug==slug).first()
    tags = post.tags
    time = post.created.strftime("%d %B %Y (%A) %I:%M")
    return render_template('posts/post_content.html', post=post, tags=tags, time=time)


@about.route('/')
def contacts():
    return render_template('posts/about.html', post=about)


@posts.route('/tag/<slug>')
def tag_detail(slug):
    tag = Tag.query.filter(Tag.slug == slug).first()
    posts = tag.posts.all()
    return render_template('posts/tag_detail.html', tag=tag, posts=posts)


